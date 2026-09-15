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
                "text-sm rounded-full px-3 py-1 border transition-colors " +
                (active
                  ? "bg-brand-600 text-white border-brand-600"
                  : "bg-white text-gray-700 border-gray-300 hover:border-brand-400")
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
