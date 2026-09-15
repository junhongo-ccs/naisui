import { useState } from "react";
import ChatPanel from "./ChatPanel";

const conversation = [
  { id: "1", role: "user", text: "二葉三丁目の状況は？" },
  {
    id: "2",
    role: "assistant",
    text:
      "二葉三丁目のシナリオ別リスク推定: 床上浸水相当（危険）\n\n" +
      "・二葉三丁目: シナリオ「100mm/h (短時間極端降雨)」における推定リスクレベルは「床上浸水相当（危険）」。\n" +
      "・20cm以上の湛水が推定される面積の割合は約2.38%（町丁目内のセル単位集計）。\n\n" +
      "この結果は校正前のスクリーニングモデルによる試行的なシナリオ結果であり、実際の浸水予報ではありません。\n\n" +
      "→ 最新の公式な避難情報・気象警報を確認してください。",
    facts: [
      "二葉三丁目: シナリオ「100mm/h (短時間極端降雨)」における推定リスクレベルは「床上浸水相当（危険）」。",
      "20cm以上の湛水が推定される面積の割合は約2.38%（町丁目内のセル単位集計）。",
    ],
    sources: [{ name: "naisui PoC モデル (pysheds_surface_routing, 校正前)", retrieved_at: "2026-09-15T07:49:55Z" }],
    scenarioId: "sc_100mm_extreme",
    scenarioLabel: "100mm/h (極端降雨)",
  },
];

function Wrapper({ initialMessages = [], loading = false, error = null, currentScenarioId = "sc_100mm_extreme" }) {
  const [messages] = useState(initialMessages);
  const [input, setInput] = useState("");
  return (
    <div style={{ height: 500, width: 420, border: "1px solid #eee" }}>
      <ChatPanel
        messages={messages}
        input={input}
        onInputChange={setInput}
        onSend={() => {}}
        loading={loading}
        error={error}
        currentScenarioId={currentScenarioId}
      />
    </div>
  );
}

export default {
  title: "naisui/ChatPanel",
  parameters: { layout: "centered" },
};

export const Empty = { render: () => <Wrapper /> };
export const Conversation = { render: () => <Wrapper initialMessages={conversation} /> };
export const Loading = { render: () => <Wrapper initialMessages={conversation.slice(0, 1)} loading /> };
export const ErrorState = {
  render: () => <Wrapper initialMessages={conversation.slice(0, 1)} error="通信に失敗しました" />,
};
export const ScenarioChangedNotice = {
  render: () => (
    <Wrapper
      initialMessages={[
        ...conversation,
        { id: "3", role: "system", text: "シナリオを「80mm/h (実績との相関が最も高い)」に変更しました" },
      ]}
      currentScenarioId="sc_80mm_peak"
    />
  ),
};
