const BASE = import.meta.env.VITE_API_BASE ?? "";

async function json(path, options) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API ${path} failed: ${res.status}`);
  }
  return res.json();
}

export const api = {
  scenarios: () => json("/api/scenarios"),
  towns: () => json("/api/towns"),
  scenario: (scenarioId) => json(`/api/scenario/${scenarioId}`),
  chat: (body) => json("/api/chat", { method: "POST", body: JSON.stringify(body) }),
};
