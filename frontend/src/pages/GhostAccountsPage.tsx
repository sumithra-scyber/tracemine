import { useEffect, useState } from "react";
import { api, Account, Evidence } from "../api/client";
import GhostMascot from "../components/GhostMascot";

export default function GhostAccountsPage() {
  const [ghosts, setGhosts] = useState<Account[]>([]);
  const [evidenceByAccount, setEvidenceByAccount] = useState<Record<string, Evidence[]>>({});

  useEffect(() => {
    api.listAccounts(true).then(async (accounts) => {
      setGhosts(accounts);
      const entries = await Promise.all(
        accounts.map(async (a) => [a.id, await api.getEvidence(a.id)] as const)
      );
      setEvidenceByAccount(Object.fromEntries(entries));
    });
  }, []);

  return (
    <div className="max-w-xl mx-auto px-4 py-10">
      <div className="text-center mb-6">
        <GhostMascot expression="sleepy" size={72} />
        <h1 className="text-2xl font-bold text-footprint-900 mt-2 mb-1">Ghost accounts</h1>
        <p className="text-sm text-footprint-800/70 max-w-sm mx-auto">
          Accounts with old evidence but no recent activity. We can't confirm these still exist.
        </p>
      </div>

      {ghosts.length === 0 ? (
        <p className="text-sm text-center text-footprint-800/60">No ghost accounts found yet.</p>
      ) : (
        <div className="flex flex-col gap-3">
          {ghosts.map((account) => (
            <div key={account.id} className="bg-white border border-footprint-100 rounded-2xl p-5">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <p className="font-semibold text-footprint-900">{account.platform_name}</p>
                  <p className="text-xs text-footprint-200">
                    No activity since {new Date(account.last_evidence_at).getFullYear()}
                  </p>
                </div>
                <span className="text-xs bg-warn-bg text-warn-text px-2.5 py-1 rounded-full whitespace-nowrap">
                  Potential ghost
                </span>
              </div>

              <div className="border-t border-footprint-100 pt-2.5 flex flex-col gap-1.5">
                {(evidenceByAccount[account.id] || []).map((ev) => (
                  <div key={ev.id} className="flex items-center gap-2 text-sm text-footprint-800">
                    <span className="text-green-600">✓</span>
                    <span>
                      {ev.evidence_type.replace(/_/g, " ")}, {new Date(ev.email_date).getFullYear()}
                    </span>
                  </div>
                ))}
              </div>

              <p className="text-xs text-footprint-200 mt-3">
                Based on email history only. We cannot confirm whether this account is still active.
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
