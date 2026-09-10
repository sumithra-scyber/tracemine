import { useNavigate } from "react-router-dom";
import GhostMascot from "../components/GhostMascot";

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="max-w-xl mx-auto text-center px-4 py-16">
      <GhostMascot expression="happy" size={100} />

      <p className="text-xs uppercase tracking-widest text-footprint-600 font-semibold mt-3 mb-1">
        Footprint
      </p>
      <h1 className="text-3xl font-bold text-footprint-900 mb-3">
        Find the accounts
        <br />
        you forgot you had
      </h1>
      <p className="text-footprint-800/80 text-[15px] max-w-sm mx-auto mb-7">
        We scan your Gmail for old sign-up emails and surface the accounts you left behind.
      </p>

      <button
        onClick={() => navigate("/connect")}
        className="bg-footprint-600 hover:bg-footprint-800 transition-colors text-white font-semibold text-[15px] h-11 px-7 rounded-full"
      >
        Connect Gmail
      </button>

      <p className="text-xs text-footprint-200 mt-3">
        Read-only. Nothing is stored or shared.
      </p>
    </div>
  );
}
