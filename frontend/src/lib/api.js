// バックエンドの場所。開発中は空（Viteのプロキシが /api と /static を中継する）。
// 本番は画面（Vercel）とバックエンド（Render）が別のサーバーなので、ビルド時に VITE_API_BASE を渡す。
const BASE = import.meta.env.VITE_API_BASE ?? "";

// バックエンドが返す "/static/..." のような相対URLを、バックエンドの場所付きにする。
export const backendUrl = (path) => (path?.startsWith("/") ? `${BASE}${path}` : path);

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
