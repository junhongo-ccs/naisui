import EvidencePanel from "./EvidencePanel";

const scenarioDetail = {
  scenario_id: "sc_100mm_extreme",
  depth_threshold_m: 0.2,
  towns: {
    "futaba-3": { name: "二葉三丁目", risk_level: "床上浸水相当（危険）", area_over_threshold_ratio: 0.0238 },
    "nakanobu-1": { name: "中延一丁目", risk_level: "湛水なし（本簡易モデル上）", area_over_threshold_ratio: 0 },
  },
};

export default {
  title: "naisui/EvidencePanel",
  component: EvidencePanel,
  parameters: { layout: "padded" },
  decorators: [(Story) => <div style={{ width: 280 }}><Story /></div>],
};

export const NoSelection = {
  render: () => <EvidencePanel scenarioDetail={scenarioDetail} selectedTown={null} />,
};

export const HighRisk = {
  render: () => (
    <EvidencePanel scenarioDetail={scenarioDetail} selectedTown={{ name: "二葉三丁目", slug: "futaba-3" }} />
  ),
};

export const NoPonding = {
  render: () => (
    <EvidencePanel scenarioDetail={scenarioDetail} selectedTown={{ name: "中延一丁目", slug: "nakanobu-1" }} />
  ),
};
