import { useState } from "react";
import ScenarioSwitcher from "./ScenarioSwitcher";

const scenarios = [
  { scenario_id: "sc_50mm_const", label: "50mm/h (計画雨量水準)", default: false },
  { scenario_id: "sc_80mm_peak", label: "80mm/h (実績との相関が最も高い)", default: false },
  { scenario_id: "sc_100mm_extreme", label: "100mm/h (極端降雨)", default: true },
];

export default {
  title: "naisui/ScenarioSwitcher",
  component: ScenarioSwitcher,
  parameters: { layout: "centered" },
};

export const Default = {
  render: () => {
    const [id, setId] = useState("sc_100mm_extreme");
    return <ScenarioSwitcher scenarios={scenarios} scenarioId={id} onChange={setId} />;
  },
};
