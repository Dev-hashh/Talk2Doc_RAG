const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";
const TOKEN_KEY = "talk2doc_token";

export function getStoredToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setStoredToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearStoredToken() {
  localStorage.removeItem(TOKEN_KEY);
}

async function request(path, options = {}) {
  const { auth, ...fetchOptions } = options;
  const token = getStoredToken();
  const headers = new Headers(options.headers ?? {});

  if (token && auth !== false) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...fetchOptions,
    headers,
  });
  const contentType = response.headers.get("content-type") ?? "";
  const body = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const message = typeof body === "object" && body?.detail ? body.detail : body;
    throw new Error(message || `Request failed with ${response.status}`);
  }

  return body;
}

export const apiClient = {
  signup: async (payload) =>
    request("/auth/signup", {
      method: "POST",
      auth: false,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),

  login: async (payload) =>
    request("/auth/login", {
      method: "POST",
      auth: false,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),

  me: async () => request("/auth/me"),

  listIndexes: async () => request("/indexes"),

  chat: async ({ question, indexName, topK = 5 }) =>
    request("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question,
        index_name: indexName,
        top_k: topK,
      }),
    }),

  ingest: async ({ file, indexName, chunkSize = 500, overlap = 50 }) => {
    const form = new FormData();
    form.append("file", file);

    if (indexName) {
      form.append("index_name", indexName);
    }

    form.append("chunk_size", String(chunkSize));
    form.append("overlap", String(overlap));

    return request("/ingest", {
      method: "POST",
      body: form,
    });
  },
};
