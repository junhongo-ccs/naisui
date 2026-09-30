import { useEffect, useRef } from "react";

function SystemNotice({ text }) {
  return (
    <div className="flex items-center gap-2 my-2 text-xs text-gray-400">
      <div className="flex-1 h-px bg-gray-200" />
      <span>{text}</span>
      <div className="flex-1 h-px bg-gray-200" />
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
          className="rounded-full border border-brand-700 bg-white px-3 py-1 text-sm font-bold text-brand-700 hover:bg-brand-50"
        >
          {town.name}
        </button>
      ))}
    </div>
  );
}

// 回答のあとに示す質問例。RAGの町丁目ファイル（tools/build_rag_markdown.py）は10町丁目とも
// 同じ章立て（地形・たまりやすい場所・公式の浸水想定・過去の浸水・避難所と土のう置場）なので、
// どの町丁目でも答えのある質問を固定で出せる。
const FOLLOW_UP_QUESTIONS = [
  { label: "水がたまりやすい場所", text: (town) => `${town}で水がたまりやすいのはどこ？` },
  { label: "土地の高さ・地形", text: (town) => `${town}の土地の高さや地形は？` },
  { label: "過去の浸水", text: (town) => `${town}は過去にどれくらい浸水した？` },
  { label: "公式の想定と試算の違い", text: (town) => `${town}の公式の浸水想定と試算はどう違う？` },
  { label: "避難所・土のう置場", text: (town) => `${town}の近くの避難所と土のう置場は？` },
];

// このマップそのものについての回答（topic "about_map"）のあとに示す質問例。RAG/04_このマップについて.md で
// 答えられる話題に限る。どれも backend/app/policy.py の detect_about_map に掛かる言い方にする
// （町丁目を選んでいなくても答えられるように。backend/tests/test_policy.py で確かめている）。
const MAP_FOLLOW_UP_QUESTIONS = [
  { label: "目的", text: "このマップは何のためのもの？" },
  { label: "画面の使い方", text: "このマップの使い方は？" },
  { label: "地図の色の見方", text: "このマップの地図の色は何を表している？" },
  { label: "計算のしかた", text: "このマップはどうやって計算してるの？" },
  { label: "過去の浸水との照合", text: "このマップの試算は過去の浸水とどれくらい合う？" },
  { label: "使っている技術", text: "このマップで使っている技術は？" },
];

// 押すと入力欄に反映する（自動送信はしない）。直前に聞いた質問は出さない。
function FollowUpQuestions({ title, questions: allQuestions, askedText, onPick }) {
  const questions = allQuestions.filter((q) => q.text !== askedText);
  return (
    <div className="mt-3 pt-2 border-t border-gray-100">
      <div className="text-xs text-gray-500 mb-1.5">{title}</div>
      <div className="flex flex-wrap gap-1.5">
        {questions.map((q) => (
          <button
            key={q.label}
            type="button"
            onClick={() => onPick(q.text)}
            className="rounded-full border border-brand-700 bg-white px-3 py-1 text-sm font-bold text-brand-700 hover:bg-brand-50"
          >
            {q.label}
          </button>
        ))}
      </div>
    </div>
  );
}

function Bubble({ message, currentScenarioId, onSelectTown, followUp }) {
  if (message.role === "system") return <SystemNotice text={message.text} />;
  const isUser = message.role === "user";
  const stale = !isUser && message.scenarioLabel && message.scenarioId !== currentScenarioId;
  return (
    <div className={"flex " + (isUser ? "justify-end" : "justify-start")}>
      <div
        className={
          "max-w-[85%] rounded-2xl px-4 py-2 text-base whitespace-pre-wrap " +
          (isUser ? "bg-brand-700 text-white" : "bg-white border border-gray-200 text-gray-900")
        }
      >
        {stale && (
          <div className="text-xs text-gray-400 mb-1">（{message.scenarioLabel}時点の回答）</div>
        )}
        {message.text}
        {!isUser && <TownChoices choices={message.townChoices} onSelectTown={onSelectTown} />}
        {followUp}
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
  const inputRef = useRef(null);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight });
  }, [messages, loading]);

  // 質問例は、町丁目を特定できた回答か、このマップについての回答の、最新のものにだけ出す（緊急時の案内には出さない）。
  const last = messages.at(-1);
  const showFollowUp =
    !loading &&
    last?.role === "assistant" &&
    (last.townName || last.topic === "about_map") &&
    last.status !== "emergency";
  const followUpFor = (m) =>
    m.topic === "about_map"
      ? { title: "このマップについて、ほかに聞けること", questions: MAP_FOLLOW_UP_QUESTIONS }
      : {
          title: `${m.townName}について、ほかに聞けること`,
          questions: FOLLOW_UP_QUESTIONS.map((q) => ({ label: q.label, text: q.text(m.townName) })),
        };
  const pickFollowUp = (text) => {
    onInputChange(text);
    inputRef.current?.focus();
  };

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
            <div>町丁目を選んで、大雨への備えに役立つことを聞いてください。</div>
            <div className="text-xs">{COVERAGE_NOTE}</div>
          </div>
        )}
        {messages.map((m, i) => (
          <Bubble
            key={m.id}
            message={m}
            currentScenarioId={currentScenarioId}
            onSelectTown={onSelectTown}
            followUp={
              showFollowUp && m === last ? (
                <FollowUpQuestions {...followUpFor(m)} askedText={messages[i - 1]?.text} onPick={pickFollowUp} />
              ) : null
            }
          />
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
        {/* 字数の上限は backend/app/policy.py の MAX_MESSAGE_LENGTH と合わせる */}
        <input
          ref={inputRef}
          maxLength={200}
          className="flex-1 border border-gray-300 rounded-full px-4 py-2 text-base focus:outline-none focus:ring-2 focus:ring-brand-400"
          placeholder="町丁目名を入力するか、ボタンで選択してください"
          value={input}
          onChange={(e) => onInputChange(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          disabled={loading}
        />
        {/* 送信ボタンは緑みの濃い灰色（白文字とのコントラスト比 約9:1） */}
        <button
          type="button"
          onClick={send}
          disabled={loading || !input.trim()}
          className="rounded-full bg-[#3f4b44] text-white px-5 py-2 text-base disabled:opacity-40"
        >
          送信
        </button>
      </div>
    </div>
  );
}
