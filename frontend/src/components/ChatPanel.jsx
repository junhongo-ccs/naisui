import { useEffect, useRef, useState } from "react";

function SystemNotice({ text }) {
  return (
    <div className="flex items-center gap-2 my-2 text-xs text-gray-400">
      <div className="flex-1 h-px bg-gray-200" />
      <span>{text}</span>
      <div className="flex-1 h-px bg-gray-200" />
    </div>
  );
}

function EvidenceDetails({ message }) {
  const [open, setOpen] = useState(false);
  if (!message.facts?.length && !message.sources?.length) return null;
  return (
    <div className="mt-2">
      <button
        type="button"
        className="text-xs text-brand-700 underline"
        onClick={() => setOpen((v) => !v)}
      >
        {open ? "根拠・計算条件を閉じる" : "根拠・計算条件を見る"}
      </button>
      {open && (
        <div className="mt-1 text-xs text-gray-500 bg-gray-50 rounded-md p-2 space-y-1">
          {message.facts?.map((f, i) => (
            <div key={i}>・{f}</div>
          ))}
          {message.sources?.map((s, i) => (
            <div key={i} className="text-gray-400">
              出典: {s.name}（{new Date(s.retrieved_at).toLocaleString("ja-JP")}）
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// PoCでデータがある範囲。backend/app/data.py の COVERAGE_LABEL と合わせる。
const COVERAGE_NOTE = "このPoCのデータは、品川区の中延一〜六丁目・二葉一〜四丁目の10町丁目だけです。";

// 町丁目を特定できなかった回答に添える選択肢。選ぶと入力欄に反映する（自動送信はしない）。
function TownChoices({ choices, onSelectTown }) {
  if (!choices?.length || !onSelectTown) return null;
  return (
    <div className="mt-2 flex flex-wrap gap-1.5">
      {choices.map((town) => (
        <button
          key={town.slug}
          type="button"
          onClick={() => onSelectTown(town)}
          className="rounded-full border border-brand-300 bg-brand-50 px-3 py-1 text-sm text-brand-800 hover:bg-brand-100"
        >
          {town.name}
        </button>
      ))}
    </div>
  );
}

function Bubble({ message, currentScenarioId, onSelectTown }) {
  if (message.role === "system") return <SystemNotice text={message.text} />;
  const isUser = message.role === "user";
  const stale = !isUser && message.scenarioLabel && message.scenarioId !== currentScenarioId;
  return (
    <div className={"flex " + (isUser ? "justify-end" : "justify-start")}>
      <div
        className={
          "max-w-[85%] rounded-2xl px-4 py-2 text-base whitespace-pre-wrap " +
          (isUser ? "bg-brand-600 text-white" : "bg-white border border-gray-200 text-gray-900")
        }
      >
        {stale && (
          <div className="text-xs text-gray-400 mb-1">（{message.scenarioLabel}時点の回答）</div>
        )}
        {message.text}
        {!isUser && <TownChoices choices={message.townChoices} onSelectTown={onSelectTown} />}
        {!isUser && <EvidenceDetails message={message} />}
      </div>
    </div>
  );
}

export default function ChatPanel({
  messages,
  input,
  onInputChange,
  onSend,
  loading,
  error,
  currentScenarioId,
  onSelectTown,
}) {
  const listRef = useRef(null);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight });
  }, [messages, loading]);

  const send = () => {
    const text = input.trim();
    if (!text || loading) return;
    onSend(text);
  };

  return (
    <div className="flex flex-col h-full min-h-0">
      <div ref={listRef} className="flex-1 min-h-0 overflow-y-auto px-3 py-3 space-y-3">
        {messages.length === 0 && (
          <div className="text-sm text-gray-400 text-center mt-8 space-y-1">
            <div>町丁目を選んで、状況を質問してください。</div>
            <div className="text-xs">{COVERAGE_NOTE}</div>
          </div>
        )}
        {messages.map((m) => (
          <Bubble key={m.id} message={m} currentScenarioId={currentScenarioId} onSelectTown={onSelectTown} />
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="rounded-2xl px-4 py-2 bg-white border border-gray-200 text-gray-400 text-base">
              考えています…
            </div>
          </div>
        )}
        {error && (
          <div className="flex justify-center">
            <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md px-3 py-2 flex items-center gap-2">
              <span>エラーが発生しました。{error}</span>
              <button
                type="button"
                className="underline"
                onClick={() => onSend(messages.at(-1)?.role === "user" ? messages.at(-1).text : "")}
              >
                再試行
              </button>
            </div>
          </div>
        )}
      </div>
      <div className="border-t border-gray-200 p-3 flex gap-2 bg-white">
        <input
          className="flex-1 border border-gray-300 rounded-full px-4 py-2 text-base focus:outline-none focus:ring-2 focus:ring-brand-400"
          placeholder="町丁目名を入力するか、ボタンで選択してください"
          value={input}
          onChange={(e) => onInputChange(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          disabled={loading}
        />
        <button
          type="button"
          onClick={send}
          disabled={loading || !input.trim()}
          className="rounded-full bg-brand-600 text-white px-5 py-2 text-base disabled:opacity-40"
        >
          送信
        </button>
      </div>
    </div>
  );
}
