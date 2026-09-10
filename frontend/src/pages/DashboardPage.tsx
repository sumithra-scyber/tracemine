import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, Account } from "../api/client";
import GhostMascot from "../components/GhostMascot";

type Filter = "all" | "strong" | "weak" | "ghosts";

export default function DashboardPage() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [filter, setFilter] = useState<Filter>("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .listAccounts()
      .then(setAccounts)
      .finally(() => setLoading(false));
  }, []);

  const filtered = accounts.filter((a) => {
    if (filter === "strong") return a.confidence_level === "strong";
    if (filter === "weak") return a.confidence_level === "weak";
    if (filter === "ghosts") return a.is_ghost;
    return true;
  });

  const counts = {
    total: accounts.length,
    strong: accounts.filter((a) => a.confidence_level === "strong").length,
    weak: accounts.filter((a) => a.confidence_level === "weak").length,
    ghosts: accounts.filter((a) => a.is_ghost).length,
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      <div className="flex items-center gap-3 mb-6">
        <GhostMascot expression="happy" size={44} />
        <h1 className="text-2xl font-bold text-footprint-900">Your accounts</h1>
      </div>

      <div className="grid grid-cols-4 gap-3 mb-6">
        <StatCard label="Total accounts" value={counts.total} />
        <StatCard label="Strong evidence" value={counts.strong} />
        <StatCard label="Weak evidence" value={counts.weak} />
        <StatCard label="Ghost accounts" value={counts.ghosts} warn />
      </div>

      <div className="flex gap-2 mb-4">
        {(["all", "strong", "weak", "ghosts"] as Filter[]).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`text-sm px-3 h-8 rounded-full border transition-colors ${
              filter === f
                ? "bg-footprint-600 text-white border-footprint-600"
                : "border-footprint-100 text-footprint-800"
            }`}
          >
            {f === "all" ? "All" : f === "strong" ? "Strong evidence" : f === "weak" ? "Weak evidence" : "Ghosts"}
          </button>
        ))}
      </div>

      {loading ? (
        <p className="text-sm text-footprint-800/60">Loading your accounts…</p>
      ) : filtered.length === 0 ? (
        <p className="text-sm text-footprint-800/60">No accounts found for this filter.</p>
      ) : (
        <div className="flex flex-col">
          {filtered.map((account) => (
            <Link
              key={account.id}
              to={account.is_ghost ? "/ghosts" : "#"}
              className="flex items-center gap-3 py-3 border-b border-footprint-100 last:border-0 hover:bg-footprint-50/40 rounded-lg px-2 -mx-2"
            >
              <div className="w-9 h-9 rounded-full bg-footprint-50 flex items-center justify-center text-xs font-semibold text-footprint-800">
                {account.platform_name.slice(0, 2).toUpperCase()}
              </div>
              <div className="flex-1">
                <p className="text-sm font-semibold text-footprint-900">{account.platform_name}</p>
                <p className="text-xs text-footprint-800/60">
                  Last evidence {new Date(account.last_evidence_at).getFullYear()}
                </p>
              </div>
              <Badge account={account} />
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value, warn }: { label: string; value: number; warn?: boolean }) {
  return (
    <div className={`rounded-lg p-4 ${warn ? "bg-warn-bg" : "bg-footprint-50"}`}>
      <p className={`text-xs mb-1 ${warn ? "text-warn-text" : "text-footprint-800/70"}`}>{label}</p>
      <p className={`text-2xl font-bold ${warn ? "text-warn-text" : "text-footprint-900"}`}>{value}</p>
    </div>
  );
}

function Badge({ account }: { account: Account }) {
  if (account.is_ghost) {
    return <span className="text-xs bg-warn-bg text-warn-text px-2.5 py-1 rounded-full whitespace-nowrap">Ghost</span>;
  }
  if (account.confidence_level === "strong") {
    return <span className="text-xs bg-green-100 text-green-800 px-2.5 py-1 rounded-full whitespace-nowrap">Active</span>;
  }
  return <span className="text-xs bg-footprint-50 text-footprint-800/70 px-2.5 py-1 rounded-full whitespace-nowrap">Uncertain</span>;
}
