"""
Orchestrates the full discovery pipeline:

  Gmail search -> candidate emails -> rule-based classification
  -> LLM for anything ambiguous -> evidence rows -> aggregated accounts

This is intentionally the only place that wires all the pieces together, so
the pipeline order and data-minimization guarantees are visible in one spot.
"""

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.detection.providers import get_llm_classifier
from app.detection.rules import classify_with_rules
from app.gmail.client import GmailClient
from app.gmail.filters import build_candidate_queries
from app.models.account import Account, ConfidenceLevel
from app.models.evidence import EmailEvidence, EvidenceType, ClassificationSource
from app.models.scan_job import ScanJob, ScanStatus
from app.services.ghost_service import is_ghost_account


def _parse_email_date(date_header: str) -> datetime:
    try:
        return parsedate_to_datetime(date_header)
    except (TypeError, ValueError):
        return datetime.now(timezone.utc)


async def _get_job(db: AsyncSession, scan_job_id) -> ScanJob:
    result = await db.execute(select(ScanJob).where(ScanJob.id == scan_job_id))
    job = result.scalar_one()
    return job


async def run_scan(db: AsyncSession, user_id, gmail_client: GmailClient, scan_job_id) -> None:
    """
    Runs the full pipeline while keeping the ScanJob row up to date so
    GET /scan/status/{id} can report real, meaningful progress:
    searching -> classifying -> building_inventory -> completed/failed.
    """
    try:
        job = await _get_job(db, scan_job_id)
        job.status = ScanStatus.SEARCHING
        await db.commit()

        llm_classifier = None  # lazily created only if a message actually needs it

        # --- Stage 1: search Gmail for candidate emails ---
        # Collected up front (ids only, no content) so we can report a real
        # "candidate emails found" count before classification even starts.
        all_message_ids: list[str] = []
        for query, _hint in build_candidate_queries():
            ids = gmail_client.search_message_ids(query)
            all_message_ids.extend(ids)

            job.candidate_emails_found = len(all_message_ids)
            await db.commit()

        # --- Stage 2: classify each candidate email ---
        job.status = ScanStatus.CLASSIFYING
        await db.commit()

        for message_id in all_message_ids:
            # Skip if we've already recorded evidence for this exact message.
            existing = await db.execute(
                select(EmailEvidence).where(EmailEvidence.gmail_message_id == message_id)
            )
            if existing.first() is not None:
                job.emails_classified += 1
                await db.commit()
                continue

            message = gmail_client.get_message_summary(message_id)
            rule_result = classify_with_rules(message)

            if rule_result.matched:
                if rule_result.evidence_type == EvidenceType.NEWSLETTER:
                    job.emails_classified += 1
                    await db.commit()
                    continue  # never stored as account evidence
                evidence_type = rule_result.evidence_type
                confidence = rule_result.confidence
                reason = rule_result.reason
                source = ClassificationSource.RULE
            else:
                if llm_classifier is None:
                    llm_classifier = get_llm_classifier()
                llm_result = llm_classifier.classify(
                    sender_domain=message.sender_domain,
                    subject=message.subject,
                    snippet=message.snippet,
                )
                if llm_result.classification != "ACCOUNT_EVIDENCE":
                    job.emails_classified += 1
                    await db.commit()
                    continue
                evidence_type = EvidenceType.OTHER
                confidence = llm_result.confidence
                reason = llm_result.reason
                source = ClassificationSource.LLM

            evidence = EmailEvidence(
                user_id=user_id,
                gmail_message_id=message.message_id,
                sender_domain=message.sender_domain,
                sender_address=message.sender_address,
                subject=message.subject,
                email_date=_parse_email_date(message.date_header),
                evidence_type=evidence_type,
                confidence=confidence,
                classification_source=source,
                reason=reason,
            )
            db.add(evidence)
            job.emails_classified += 1
            await db.commit()

        # --- Stage 3: rebuild the account inventory ---
        job.status = ScanStatus.BUILDING_INVENTORY
        await db.commit()

        accounts_discovered = await _rebuild_account_inventory(db, user_id)

        job.status = ScanStatus.COMPLETED
        job.accounts_discovered = accounts_discovered
        await db.commit()

    except Exception as exc:  # noqa: BLE001 - we want to record any failure
        job = await _get_job(db, scan_job_id)
        job.status = ScanStatus.FAILED
        job.error_message = str(exc)
        await db.commit()
        raise


async def _rebuild_account_inventory(db: AsyncSession, user_id) -> int:
    """
    Recompute the Account aggregate table from EmailEvidence.

    Accounts are grouped by sender_domain. Recomputing from scratch (rather
    than incrementally patching) keeps the aggregate always consistent with
    the underlying evidence, including after a user deletes evidence.
    """
    result = await db.execute(select(EmailEvidence).where(EmailEvidence.user_id == user_id))
    all_evidence = result.scalars().all()

    by_domain: dict[str, list[EmailEvidence]] = {}
    for ev in all_evidence:
        by_domain.setdefault(ev.sender_domain, []).append(ev)

    # Clear and rebuild this user's accounts.
    await db.execute(Account.__table__.delete().where(Account.user_id == user_id))

    for domain, evidences in by_domain.items():
        max_confidence = max(e.confidence for e in evidences)
        if max_confidence >= 80:
            level = ConfidenceLevel.STRONG
        elif max_confidence >= 40:
            level = ConfidenceLevel.WEAK
        else:
            level = ConfidenceLevel.UNCERTAIN

        first_seen = min(e.email_date for e in evidences)
        last_seen = max(e.email_date for e in evidences)
        platform_name = domain.split(".")[0].capitalize()

        account = Account(
            user_id=user_id,
            platform_name=platform_name,
            primary_domain=domain,
            confidence_level=level,
            confidence_score=max_confidence,
            first_evidence_at=first_seen,
            last_evidence_at=last_seen,
        )
        account.is_ghost = is_ghost_account(account)
        db.add(account)

    await db.commit()
    return len(by_domain)
