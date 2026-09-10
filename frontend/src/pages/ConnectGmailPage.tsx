import { api } from "../api/client";
import GhostMascot from "../components/GhostMascot";

interface Permission {
  granted: boolean;
  text: string;
  why?: string;
}

const PERMISSIONS: Permission[] = [
  {
    granted: true,
    text: "See your email address",
    why: "So we know which Google account is connected, without you typing it in and risking a mismatch.",
  },
  {
    granted: true,
    text: "Read email metadata and subjects (read-only)",
    why: "So we can search for account-related emails like welcome messages and password resets.",
  },
  {
    granted: false,
    text: "Cannot send, delete, or modify emails",
  },
  {
    granted: false,
    text: "Never sees or stores your password",
  },
];

export default function ConnectGmailPage() {
  return (
    <div className="max-w-md mx-auto mt-12 px-4">
      <div className="bg-white border border-footprint-100 rounded-2xl p-6 text-center">
        <GhostMascot expression="happy" size={72} />
        <h2 className="text-xl font-bold text-footprint-900 mt-2 mb-1">Connect your Gmail</h2>
        <p className="text-footprint-800/70 text-sm mb-4">
          Footprint asks for the minimum access needed to scan for account signals.
        </p>

        <div className="border-t border-b border-footprint-100 py-3 mb-4 text-left">
          {PERMISSIONS.map((p) => (
            <div key={p.text} className="py-2">
              <div className="flex items-start gap-2">
                <span className={p.granted ? "text-green-600" : "text-footprint-200"}>
                  {p.granted ? "✓" : "✕"}
                </span>
                <span className="text-sm text-footprint-800 font-medium">{p.text}</span>
              </div>
              {p.why && <p className="text-xs text-footprint-800/60 ml-6 mt-0.5">{p.why}</p>}
            </div>
          ))}
        </div>

        <a
          href={api.loginUrl()}
          className="block w-full bg-footprint-600 hover:bg-footprint-800 transition-colors text-white font-semibold text-sm h-11 leading-[44px] rounded-lg mb-2"
        >
          Continue with Google
        </a>
        <p className="text-xs text-footprint-200">
          You can revoke access anytime from your Google account or Footprint settings.
        </p>
      </div>
    </div>
  );
}
