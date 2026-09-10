"""
Thin wrapper around the Gmail API, read-only.

Only two operations are exposed: listing message ids matching a search
query, and fetching lightweight metadata (headers) for a message. We never
fetch full message bodies - see filters.py and detection/rules.py for why
headers plus snippet are enough for classification.
"""

from dataclasses import dataclass

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


@dataclass
class MessageSummary:
    message_id: str
    sender_address: str
    sender_domain: str
    subject: str
    snippet: str
    date_header: str


class GmailClient:
    def __init__(self, credentials: Credentials):
        self._service = build("gmail", "v1", credentials=credentials)

    def search_message_ids(self, query: str, max_results: int = 500) -> list[str]:
        """Return Gmail message ids matching a search query (no content fetched)."""
        ids: list[str] = []
        page_token = None
        while True:
            response = (
                self._service.users()
                .messages()
                .list(userId="me", q=query, maxResults=min(100, max_results - len(ids)), pageToken=page_token)
                .execute()
            )
            ids.extend(m["id"] for m in response.get("messages", []))
            page_token = response.get("nextPageToken")
            if not page_token or len(ids) >= max_results:
                break
        return ids

    def get_message_summary(self, message_id: str) -> MessageSummary:
        """
        Fetch only header metadata and the short snippet Gmail already
        generates - never the full message body.
        """
        message = (
            self._service.users()
            .messages()
            .get(
                userId="me",
                id=message_id,
                format="metadata",
                metadataHeaders=["From", "Subject", "Date"],
            )
            .execute()
        )
        headers = {h["name"]: h["value"] for h in message["payload"]["headers"]}
        sender_header = headers.get("From", "")
        sender_address = _extract_email_address(sender_header)
        sender_domain = sender_address.split("@")[-1] if "@" in sender_address else ""

        return MessageSummary(
            message_id=message_id,
            sender_address=sender_address,
            sender_domain=sender_domain,
            subject=headers.get("Subject", ""),
            snippet=message.get("snippet", ""),
            date_header=headers.get("Date", ""),
        )


def _extract_email_address(from_header: str) -> str:
    """Parse 'Display Name <email@domain.com>' down to just the address."""
    if "<" in from_header and ">" in from_header:
        return from_header.split("<")[1].split(">")[0].strip().lower()
    return from_header.strip().lower()
