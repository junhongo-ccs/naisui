export default function ScenarioSwitcher({ scenarios, scenarioId, onChange }) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-gray-500 whitespace-nowrap">シナリオ:</span>
      <select
        className="text-sm border border-gray-300 rounded-md px-2 py-1 bg-white"
        value={scenarioId ?? ""}
        onChange={(e) => onChange(e.target.value)}
      >
        {scenarios.map((s) => (
          <option key={s.scenario_id} value={s.scenario_id}>
            {s.label}
          </option>
        ))}
      </select>
    </div>
  );
}
