import { lazy, Suspense, useEffect, useMemo, useState } from "react";
import { api } from "./lib/api";
import ScenarioSwitcher from "./components/ScenarioSwitcher";
import TownSelector from "./components/TownSelector";
import ChatPanel from "./components/ChatPanel";
import EvidencePanel from "./components/EvidencePanel";

// モバイルでは地図関連コードをバンドルに含めない。
const MapPanel = lazy(() => import("./components/MapPanel"));

const PC_BREAKPOINT = 1024;

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

  const [scenarios, setScenarios] = useState([]);
  const [scenarioId, setScenarioId] = useState(null);
  const [towns, setTowns] = useState([]);
  const [scenarioDetail, setScenarioDetail] = useState(null);

  const [selectedTown, setSelectedTown] = useState(null); // {name, slug}
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const scenarioLabel = useMemo(
    () => scenarios.find((s) => s.scenario_id === scenarioId)?.label ?? scenarioId,
    [scenarios, scenarioId]
  );

  // 初回読み込み: シナリオ一覧・町丁目一覧
  useEffect(() => {
    api.scenarios().then((list) => {
      setScenarios(list);
      const def = list.find((s) => s.default) ?? list[0];
      if (def) setScenarioId(def.scenario_id);
    });
    api.towns().then(setTowns);
  }, []);

  // シナリオ切替: 詳細を取得し、既存チャットは消さずシステム通知を追加する
  useEffect(() => {
    if (!scenarioId) return;
    const isFirstLoad = scenarioDetail === null;
    api.scenario(scenarioId).then((detail) => {
      setScenarioDetail(detail);
      if (!isFirstLoad) {
        setMessages((prev) => [
          ...prev,
          { id: nextId(), role: "system", text: `シナリオを「${scenarioLabel}」に変更しました` },
        ]);
      }
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
          scenarioLabel,
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
        {scenarios.length > 1 && (
          <ScenarioSwitcher scenarios={scenarios} scenarioId={scenarioId} onChange={setScenarioId} />
        )}
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
        <div className="flex-1 min-h-0 grid grid-cols-[1.1fr_1fr_260px] grid-rows-1">
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
          <div className="flex flex-col min-h-0 h-full border-r border-gray-200">
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
          <div className="min-h-0 h-full">
            <EvidencePanel scenarioDetail={scenarioDetail} selectedTown={selectedTown} />
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
