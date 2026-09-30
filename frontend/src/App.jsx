import { lazy, Suspense, useEffect, useState } from "react";
import { api } from "./lib/api";
import TownSelector from "./components/TownSelector";
import ChatPanel from "./components/ChatPanel";

// モバイルでは地図関連コードをバンドルに含めない。
const MapPanel = lazy(() => import("./components/MapPanel"));

const PC_BREAKPOINT = 1024;
const OFFICIAL_SCENARIO_ID = "sc_153mmh_24h_690mm_official";
const OFFICIAL_SCENARIO_LABEL = "想定最大規模降雨 (1時間153mm・24時間690mm)";

function useIsPC() {
  const [isPC, setIsPC] = useState(
    typeof window !== "undefined" ? window.innerWidth >= PC_BREAKPOINT : true
  );
  useEffect(() => {
    const onResize = () => setIsPC(window.innerWidth >= PC_BREAKPOINT);
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);
  return isPC;
}

// ノートPCではブラウザのタブやアドレスバーの分だけ地図とチャットが狭くなるため、
// ページ全体（地図＋チャット）を全画面にするボタンを出す（F11と同じ）。Escでも戻れる。
// 全画面にできないブラウザ（iPhoneのSafariなど）では出さない。
function FullscreenButton() {
  const [isFull, setIsFull] = useState(() => Boolean(document.fullscreenElement));
  useEffect(() => {
    const onChange = () => setIsFull(Boolean(document.fullscreenElement));
    document.addEventListener("fullscreenchange", onChange);
    return () => document.removeEventListener("fullscreenchange", onChange);
  }, []);
  if (!document.fullscreenEnabled) return null;
  const toggle = () => (isFull ? document.exitFullscreen() : document.documentElement.requestFullscreen());
  return (
    <button
      type="button"
      onClick={toggle}
      className="text-xs text-white border border-white/70 rounded px-2 py-0.5 whitespace-nowrap hover:bg-white/10"
    >
      {isFull ? "全画面を終了" : "全画面で表示"}
    </button>
  );
}

let msgSeq = 0;
const nextId = () => `m${++msgSeq}`;

export default function App() {
  const isPC = useIsPC();

  const [scenarioId] = useState(OFFICIAL_SCENARIO_ID);
  const [towns, setTowns] = useState([]);
  const [scenarioDetail, setScenarioDetail] = useState(null);

  const [selectedTown, setSelectedTown] = useState(null); // {name, slug}
  // 地域を選ぶ欄の開閉。町丁目が選ばれたとき・質問を送ったときに閉じ、会話の場所を空ける（見出しで開き直せる）。
  const [selectorOpen, setSelectorOpen] = useState(true);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 初回読み込み: 町丁目一覧
  useEffect(() => {
    api.towns().then(setTowns).catch((e) => setError(e.message ?? "町丁目一覧の取得に失敗しました"));
  }, []);

  // 固定された公式想定シナリオの詳細を取得する。
  useEffect(() => {
    if (!scenarioId) return;
    api
      .scenario(scenarioId)
      .then((detail) => setScenarioDetail(detail))
      .catch((e) => setError(e.message ?? "シナリオ情報の取得に失敗しました"));
  }, [scenarioId]);

  const handleTownSelect = (town) => {
    setSelectedTown(town);
    setSelectorOpen(false);
    setInput(`${town.name}について教えて`);
  };

  const handleMapTownClick = (townName) => {
    const town = towns.find((t) => t.name === townName);
    if (town) handleTownSelect(town);
  };

  const handleSend = async (text) => {
    setInput("");
    // 会話が始まったら、町丁目を選んでいなくても地域の欄を閉じて回答を読む場所を空ける（見出しで開き直せる）。
    setSelectorOpen(false);
    setError(null);
    setMessages((prev) => [...prev, { id: nextId(), role: "user", text }]);
    setLoading(true);
    try {
      const res = await api.chat({
        message: text,
        scenario_id: scenarioId,
        town_slug: selectedTown?.slug ?? null,
      });
      // メッセージ中の町丁目名をバックエンドが読み取った場合は、画面の選択状態（地図の強調表示）も合わせる。
      if (res.town_slug && res.town_slug !== selectedTown?.slug) {
        const town = towns.find((t) => t.slug === res.town_slug);
        if (town) {
          setSelectedTown(town);
          setSelectorOpen(false);
        }
      }
      setMessages((prev) => [
        ...prev,
        {
          id: nextId(),
          role: "assistant",
          text: res.display_text,
          facts: res.facts,
          sources: res.sources,
          townChoices: res.town_choices,
          townName: towns.find((t) => t.slug === res.town_slug)?.name ?? null,
          status: res.status,
          topic: res.topic ?? null,
          scenarioId,
          scenarioLabel: OFFICIAL_SCENARIO_LABEL,
        },
      ]);
    } catch (e) {
      setError(e.message ?? "通信に失敗しました");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-surface text-gray-900">
      {/* 避難所の記号（brand-600）より一段濃い緑。白文字とのコントラスト比 約5.0:1 */}
      <header className="flex items-center justify-between gap-4 px-4 py-2 bg-brand-700 text-white">
        {/* スマートフォンでは幅が足りないので、地名を省いてマップ名だけにする。 */}
        <div className="flex items-center gap-1.5 font-medium text-sm whitespace-nowrap">
          {/* Material Icons「opacity」（Apache License 2.0）。フォントを読み込まずにSVGで直接描く。 */}
          <svg aria-hidden="true" viewBox="0 0 24 24" className="h-5 w-5 flex-none" fill="currentColor">
            <path d="M17.66 8L12 2.35 6.34 8C4.78 9.56 4 11.64 4 13.64s.78 4.11 2.34 5.67 3.61 2.35 5.66 2.35 4.1-.79 5.66-2.35S20 15.64 20 13.64 19.22 9.56 17.66 8zM6 14c.01-2 .62-3.27 1.76-4.4L12 5.27l4.24 4.38C17.38 10.77 17.99 12 18 14H6z" />
          </svg>
          {isPC ? "品川区 中延・二葉地区 雨水のたまりやすさマップ" : "雨水のたまりやすさマップ"}
        </div>
        <div className="flex items-center gap-4">
          <a
            href="/about.html"
            target="_blank"
            rel="noopener"
            className="inline-flex items-center gap-1 text-sm text-white whitespace-nowrap hover:text-brand-100"
          >
            {/* 下線は文字だけに引く。幅360px未満の画面では見出しに収まらないのでアイコンを出さない。 */}
            {/* Material Symbols Outlined「info」（Apache License 2.0）。フォントを読み込まずにSVGで直接描く。 */}
            <svg aria-hidden="true" viewBox="0 -960 960 960" className="h-[18px] w-[18px] flex-none max-[359px]:hidden" fill="currentColor">
              <path d="M440-280h80v-240h-80v240Zm40-320q17 0 28.5-11.5T520-640q0-17-11.5-28.5T480-680q-17 0-28.5 11.5T440-640q0 17 11.5 28.5T480-600Zm0 520q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm0-80q134 0 227-93t93-227q0-134-93-227t-227-93q-134 0-227 93t-93 227q0 134 93 227t227 93Zm0-320Z" />
            </svg>
            <span className="underline">このマップについて知る</span>
          </a>
          {/* 全画面はノートPC向け。スマートフォンはチャットだけの表示なので出さない。 */}
          {isPC && <FullscreenButton />}
        </div>
      </header>

      {isPC ? (
        <div className="flex-1 min-h-0 grid grid-cols-[minmax(0,1fr)_clamp(360px,32vw,520px)] grid-rows-1">
          <div className="border-r border-gray-200 min-h-0 h-full">
            <Suspense fallback={<div className="h-full flex items-center justify-center text-gray-400">地図を読み込み中…</div>}>
              {scenarioDetail && (
                <MapPanel
                  scenarioDetail={scenarioDetail}
                  selectedTownName={selectedTown?.name}
                  onTownClick={handleMapTownClick}
                />
              )}
            </Suspense>
          </div>
          <div className="flex flex-col min-h-0 h-full">
            <div className="p-3 border-b border-gray-100">
              <TownSelector
                towns={towns}
                selectedSlug={selectedTown?.slug}
                onSelect={handleTownSelect}
                open={selectorOpen}
                onOpenChange={setSelectorOpen}
              />
            </div>
            <div className="flex-1 min-h-0">
              <ChatPanel
                messages={messages}
                input={input}
                onInputChange={setInput}
                onSend={handleSend}
                loading={loading}
                error={error}
                currentScenarioId={scenarioId}
                onSelectTown={handleTownSelect}
              />
            </div>
          </div>
        </div>
      ) : (
        <div className="flex-1 min-h-0 flex flex-col">
          <div className="p-3 border-b border-gray-100 bg-white">
            <TownSelector
              towns={towns}
              selectedSlug={selectedTown?.slug}
              onSelect={handleTownSelect}
              open={selectorOpen}
              onOpenChange={setSelectorOpen}
            />
          </div>
          <div className="flex-1 min-h-0">
            <ChatPanel
              messages={messages}
              input={input}
              onInputChange={setInput}
              onSend={handleSend}
              loading={loading}
              error={error}
              currentScenarioId={scenarioId}
              onSelectTown={handleTownSelect}
            />
          </div>
        </div>
      )}
    </div>
  );
}
