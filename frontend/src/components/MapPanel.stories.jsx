import { useState } from "react";
import MapPanel from "./MapPanel";

// バックエンド（uvicorn, :8000）が起動している必要がある。
// Storybookのdevサーバーはfrontend/vite.config.jsの /api・/static プロキシを引き継ぐ。
const scenarioDetail = {
  scenario_id: "sc_100mm_extreme",
  map_layers: {
    town_boundaries: "/static/web_map/town_boundaries.geojson",
    hazard_pdf_derived: "/static/web_map/hazard_pdf_derived.geojson",
    ponding_overlay_png: "/static/web_map/ponding_depth_sc_100mm_extreme.png",
    ponding_overlay_bounds: "/static/web_map/ponding_depth_sc_100mm_extreme.bounds.json",
    sandbag_locations: "/static/shelter/sandbag_locations_nakanobu_futaba.geojson",
    shelter_locations: "/static/shelter/shelter_locations_nakanobu_futaba.geojson",
  },
};

export default {
  title: "naisui/MapPanel",
  parameters: {
    layout: "fullscreen",
    docs: {
      description: {
        component:
          "実データを使う地図コンポーネント。表示するには `uv --system-certs run --with-requirements requirements.txt uvicorn app.main:app --port 8000` でバックエンドを起動しておくこと。",
      },
    },
  },
};

export const Default = {
  render: () => {
    const [selected, setSelected] = useState(null);
    return (
      <div style={{ height: "100vh", width: "100%" }}>
        <MapPanel scenarioDetail={scenarioDetail} selectedTownName={selected} onTownClick={setSelected} />
      </div>
    );
  },
};
