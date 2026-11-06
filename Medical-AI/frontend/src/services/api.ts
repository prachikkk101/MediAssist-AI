import axios from "axios";

// Set VITE_API_URL to point at the tunnel or a deployed backend.
// Falls back to localhost for normal local development.
const baseURL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/+$/, "");

const API = axios.create({
  baseURL,
});

export default API;

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Starts a background analysis job and polls until it finishes.
 * Each request is short, so tunnels with a ~100s limit don't cut it off.
 * On failure it throws an error shaped like an Axios HTTP error
 * (error.response.status / error.response.data.detail).
 */
export async function analyzeReportWithPolling(
  file: File,
  question: string,
  onStatus?: (status: string) => void
): Promise<any> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("question", question);

  const { data } = await API.post("/medical/jobs", formData);
  const jobId: string = data.job_id;

  const POLL_MS = 3000;
  const MAX_WAIT_MS = 20 * 60 * 1000;
  const startedAt = Date.now();
  let failures = 0;

  while (true) {
    await sleep(POLL_MS);

    if (Date.now() - startedAt > MAX_WAIT_MS) {
      throw new Error("The analysis is taking too long. Please try again.");
    }

    let job: any;
    try {
      const res = await API.get(`/medical/jobs/${jobId}`);
      job = res.data;
      failures = 0;
    } catch (e: any) {
      if (e?.response?.status === 404) throw e; // job is gone
      failures += 1;
      if (failures >= 5) throw e; // 5 failed checks in a row
      continue;
    }

    onStatus?.(job.status);

    if (job.status === "done") return job.result;

    if (job.status === "error") {
      const err: any = new Error(job.detail || "The analysis failed.");
      err.response = {
        status: job.http_status || 500,
        data: { detail: job.detail },
      };
      throw err;
    }
  }
}