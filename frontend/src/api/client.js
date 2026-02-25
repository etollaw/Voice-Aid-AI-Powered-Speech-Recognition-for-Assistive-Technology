/**
 * API client for VoiceAid backend.
 *
 * In development, Vite proxies /api to localhost:8000.
 * In production, set VITE_API_URL to your backend URL.
 */

const BASE_URL = import.meta.env.VITE_API_URL || "";

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

async function handleResponse(response) {
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const data = await response.json();
      message = data.detail || message;
    } catch {
      // ignore JSON parse errors
    }
    throw new ApiError(message, response.status);
  }
  // 204 No Content
  if (response.status === 204) return null;
  return response.json();
}

const api = {
  /** Upload audio file and process it. Returns the full session object. */
  async createSession(file) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${BASE_URL}/api/sessions`, {
      method: "POST",
      body: formData,
    });
    return handleResponse(response);
  },

  /** List sessions with optional search and pagination. */
  async listSessions({ search = "", status = "", page = 1, pageSize = 20 } = {}) {
    const params = new URLSearchParams();
    if (search) params.set("search", search);
    if (status) params.set("status", status);
    params.set("page", page.toString());
    params.set("page_size", pageSize.toString());

    const response = await fetch(`${BASE_URL}/api/sessions?${params}`);
    return handleResponse(response);
  },

  /** Get a single session by ID. */
  async getSession(id) {
    const response = await fetch(`${BASE_URL}/api/sessions/${id}`);
    return handleResponse(response);
  },

  /** Delete a session. */
  async deleteSession(id) {
    const response = await fetch(`${BASE_URL}/api/sessions/${id}`, {
      method: "DELETE",
    });
    return handleResponse(response);
  },

  /** Re-summarize a session with different settings. */
  async resummarize(id, sentenceCount = 5) {
    const response = await fetch(`${BASE_URL}/api/sessions/${id}/resummarize`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sentence_count: sentenceCount }),
    });
    return handleResponse(response);
  },

  /** Health check. */
  async health() {
    const response = await fetch(`${BASE_URL}/api/health`);
    return handleResponse(response);
  },
};

export default api;
export { ApiError };
