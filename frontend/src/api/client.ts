const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export interface Account {
  id: string;
  platform_name: string;
  primary_domain: string;
  confidence_level: "strong" | "weak" | "uncertain";
  confidence_score: number;
  first_evidence_at: string;
  last_evidence_at: string;
  is_ghost: boolean;
}

export type ScanStatus =
  | "pending"
  | "searching"
  | "classifying"
  | "building_inventory"
  | "completed"
  | "failed";

export interface ScanJob {
  id: string;
  status: ScanStatus;
  candidate_emails_found: number;
  emails_classified: number;
  accounts_discovered: number;
  error_message: string | null;
}

export interface Evidence {
  id: string;
  subject: string;
  sender_domain: string;
  email_date: string;
  evidence_type: string;
  confidence: number;
  classification_source: "rule" | "llm";
  reason: string;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    credentials: "include", // sends the session cookie
    ...options,
  });
  if (!response.ok) {
    throw new Error(`Request to ${path} failed with ${response.status}`);
  }
  return response.json();
}

export const api = {
  loginUrl: () => `${BASE_URL}/auth/google/login`,
  startScan: () => request<ScanJob>("/scan/start", { method: "POST" }),
  getScanStatus: (scanJobId: string) => request<ScanJob>(`/scan/status/${scanJobId}`),
  listAccounts: (ghostsOnly = false) =>
    request<Account[]>(`/accounts${ghostsOnly ? "?ghosts_only=true" : ""}`),
  getEvidence: (accountId: string) => request<Evidence[]>(`/accounts/${accountId}/evidence`),
  deleteMyData: () => request<{ status: string }>("/privacy/delete-my-data", { method: "DELETE" }),
};
