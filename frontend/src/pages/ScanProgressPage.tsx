import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, ScanJob, ScanStatus } from "../api/client";
import GhostMascot from "../components/GhostMascot";

const POLL_INTERVAL_MS = 1500;

const STAGE_ORDER: ScanStatus[] = [
  "pending",
  "searching",
  "classifying",
  "building_inventory",
  "completed",
];

const STAGE_LABELS: Record<ScanStatus, string> = {
  pending: "Getting ready",
  searching: "Searching for candidate emails",
  classifying: "Classifying evidence",
  building_inventory: "Building your account inventory",
  completed: "Done",
  failed: "Something went wrong",
};

export default function ScanProgressPage() {
  const navigate = useNavigate();
  const [job, setJob] = useState<ScanJob | null>(null);
  const [error, setError] = useState<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function begin() {
      try {
        const started = await api.startScan();
        if (cancelled) return;
        setJob(started);

        pollRef.current = setInterval(async () => {
          try {
            const latest = await api.getScanStatus(started.id);
            if (cancelled) return;
            setJob(latest);

            if (latest.status === "completed") {
              clearInterval(pollRef.current!);
              setTimeout(() => navigate("/dashboard"), 800);
            } else if (latest.status === "failed") {
              clearInterval(pollRef.current!);
            }
          } catch {
            // A transient poll failure isn't fatal; the next tick retries.
          }
        }, POLL_INTERVAL_MS);
      } catch {
        setError("We couldn't start the scan. Please try connecting Gmail again.");
      }
    }

    begin();

    return () => {
      cancelled = true;
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [navigate]);

  if (error) {
    return (
      <div className="max-w-md mx-auto mt-12 px-4 text-center">
        <GhostMascot expression="surprised" size={72} />
        <p className="text-sm text-footprint-800 mt-3">{error}</p>
      </div>
    );
  }

  const currentIndex = job ? STAGE_ORDER.indexOf(job.status) : -1;

  return (
    <div className="max-w-md mx-auto mt-12 px-4 text-center">
      <GhostMascot expression={job?.status === "failed" ? "surprised" : "searching"} size={80} />
      <h2 className="text-xl font-bold text-footprint-900 mt-2 mb-1">Scanning your inbox</h2>
      <p className="text-footprint-800/70 text-sm mb-2">
        This runs on our servers. No email content leaves Footprint.
      </p>

      {job && (
        <p className="text-xs text-footprint-200 mb-6">
          {job.candidate_emails_found} candidate emails found · {job.emails_classified} classified
          {job.status === "completed" && ` · ${job.accounts_discovered} accounts discovered`}
        </p>
      )}

      {job?.status === "failed" ? (
        <p className="text-sm text-warn-text bg-warn-bg rounded-lg py-2 px-3">
          {job.error_message || "The scan failed. Please try again."}
        </p>
      ) : (
        <div className="text-left flex flex-col gap-1">
          {STAGE_ORDER.filter((s) => s !== "pending" || currentIndex <= 0).map((stage) => {
            const stageIndex = STAGE_ORDER.indexOf(stage);
            const done = currentIndex > stageIndex;
            const active = currentIndex === stageIndex;
            return (
              <div key={stage} className={`flex items-center gap-3 py-2 ${!done && !active ? "opacity-40" : ""}`}>
                <span className="w-5 text-footprint-600">{done ? "✓" : active ? "…" : "○"}</span>
                <span className="text-sm text-footprint-800">{STAGE_LABELS[stage]}</span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
