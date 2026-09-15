import { useState } from "react";
import TownSelector from "./TownSelector";

const towns = [
  { name: "中延一丁目", slug: "nakanobu-1" },
  { name: "中延二丁目", slug: "nakanobu-2" },
  { name: "中延三丁目", slug: "nakanobu-3" },
  { name: "中延四丁目", slug: "nakanobu-4" },
  { name: "中延五丁目", slug: "nakanobu-5" },
  { name: "中延六丁目", slug: "nakanobu-6" },
  { name: "二葉一丁目", slug: "futaba-1" },
  { name: "二葉二丁目", slug: "futaba-2" },
  { name: "二葉三丁目", slug: "futaba-3" },
  { name: "二葉四丁目", slug: "futaba-4" },
];

export default {
  title: "naisui/TownSelector",
  component: TownSelector,
  parameters: { layout: "padded" },
};

export const NoSelection = {
  render: () => <TownSelector towns={towns} selectedSlug={null} onSelect={() => {}} />,
};

export const Interactive = {
  render: () => {
    const [selected, setSelected] = useState("futaba-3");
    return (
      <TownSelector towns={towns} selectedSlug={selected} onSelect={(t) => setSelected(t.slug)} />
    );
  },
};
