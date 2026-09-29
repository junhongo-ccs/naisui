function groupTowns(towns) {
  const nakanobu = towns.filter((t) => t.name.startsWith("中延"));
  const futaba = towns.filter((t) => t.name.startsWith("二葉"));
  return { nakanobu, futaba };
}

export default function TownSelector({ towns, selectedSlug, onSelect }) {
  const { nakanobu, futaba } = groupTowns(towns);

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
    <div className="flex flex-col gap-2">
      {renderGroup("中延", nakanobu)}
      {renderGroup("二葉", futaba)}
    </div>
  );
}
