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

let msgSeq = 0;
const nextId = () => `m${++msgSeq}`;

export default function App() {
  const isPC = useIsPC();

  const [scenarioId] = useState(OFFICIAL_SCENARIO_ID);
  const [towns, setTowns] = useState([]);
  const [scenarioDetail, setScenarioDetail] = useState(null);

  const [selectedTown, setSelectedTown] = useState(null); // {name, slug}
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
    setInput(`${town.name}の状況は？`);
  };

  const handleMapTownClick = (townName) => {
    const town = towns.find((t) => t.name === townName);
    if (town) handleTownSelect(town);
  };

  const handleSend = async (text) => {
    setInput("");
    setError(null);
    setMessages((prev) => [...prev, { id: nextId(), role: "user", text }]);
    setLoading(true);
    try {
      const res = await api.chat({
        message: text,
        scenario_id: scenarioId,
        town_slug: selectedTown?.slug ?? null,
      });
      setMessages((prev) => [
        ...prev,
        {
          id: nextId(),
          role: "assistant",
          text: res.display_text,
          facts: res.facts,
          sources: res.sources,
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
    <div className="h-screen w-screen flex flex-col bg-base text-gray-900">
      <header className="flex items-center justify-between gap-4 px-4 py-2 border-b border-gray-200 bg-white">
        <div className="font-medium text-sm whitespace-nowrap">中延・二葉 内水氾濫 PoC</div>
        <a
          href="https://www.city.shinagawa.tokyo.jp/PC/bosai/bosai2/index.html"
          target="_blank"
          rel="noreferrer"
          className="text-xs text-brand-700 underline whitespace-nowrap"
        >
          品川区の公式情報を確認
        </a>
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
              <TownSelector towns={towns} selectedSlug={selectedTown?.slug} onSelect={handleTownSelect} />
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
              />
            </div>
          </div>
        </div>
      ) : (
        <div className="flex-1 min-h-0 flex flex-col">
          <div className="p-3 border-b border-gray-100 bg-white">
            <TownSelector towns={towns} selectedSlug={selectedTown?.slug} onSelect={handleTownSelect} />
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
            />
          </div>
        </div>
      )}
    </div>
  );
}
