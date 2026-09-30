import { useId } from "react";

function groupTowns(towns) {
  const nakanobu = towns.filter((t) => t.name.startsWith("中延"));
  const futaba = towns.filter((t) => t.name.startsWith("二葉"));
  return { nakanobu, futaba };
}

// 会話中にチャット欄を占有しないよう、見出しで折りたためる。
// 開閉の状態は親が持つ（地図やチャットで町丁目が選ばれたときにも自動で閉じるため）。
export default function TownSelector({ towns, selectedSlug, onSelect, open, onOpenChange }) {
  const { nakanobu, futaba } = groupTowns(towns);
  const panelId = useId();
  const selectedName = towns.find((t) => t.slug === selectedSlug)?.name;

  const renderGroup = (label, group) => (
    <div>
      <div className="text-xs text-gray-400 mb-1">{label}</div>
      <div className="flex flex-wrap gap-1.5">
        {group.map((t) => {
          const active = t.slug === selectedSlug;
          return (
            <button
              key={t.slug}
              type="button"
              onClick={() => onSelect(t)}
              aria-pressed={active}
              className={
                "text-sm font-bold rounded-full px-3 py-1 border border-brand-700 transition-colors " +
                (active ? "bg-brand-700 text-white" : "bg-white text-brand-700 hover:bg-brand-50")
              }
            >
              {t.name}
            </button>
          );
        })}
      </div>
    </div>
  );

  return (
    <div className="rounded-lg border border-gray-200 bg-white">
      <button
        type="button"
        onClick={() => onOpenChange(!open)}
        aria-expanded={open}
        aria-controls={panelId}
        className="w-full flex items-center gap-2 px-3 py-2 text-left rounded-lg hover:bg-gray-50"
      >
        <span className="text-sm font-bold text-gray-800 whitespace-nowrap">地域を選ぶ</span>
        {!open && selectedName && (
          <span className="text-sm text-brand-700 font-bold truncate">{selectedName}</span>
        )}
        <svg
          aria-hidden="true"
          viewBox="0 0 20 20"
          className={"ml-auto h-4 w-4 flex-none text-gray-500 transition-transform duration-300 ease-in-out motion-reduce:transition-none " + (open ? "rotate-180" : "")}
        >
          <path d="M5 7.5l5 5 5-5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>
      {/* 高さを0frと1frの間で動かして、開閉が目で追えるようにする。閉じている間はinertで操作と読み上げの対象から外す。 */}
      <div
        id={panelId}
        inert={!open}
        className={
          "grid transition-[grid-template-rows,opacity] duration-300 ease-in-out motion-reduce:transition-none " +
          (open ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0")
        }
      >
        <div className="overflow-hidden">
          <div className="px-3 pb-3 flex flex-col gap-2">
            {renderGroup("中延", nakanobu)}
            {renderGroup("二葉", futaba)}
          </div>
        </div>
      </div>
    </div>
  );
}
