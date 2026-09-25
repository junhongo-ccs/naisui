import { useEffect, useRef, useState } from "react";
import { Map as MapLibreMap, NavigationControl } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

async function fetchJson(url) {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`${url} -> HTTP ${res.status}`);
  }
  const contentType = res.headers.get("content-type") ?? "";
  if (contentType.includes("text/html")) {
    // バックエンド未起動時、Viteの開発サーバーがSPAのindex.htmlをフォールバックで返すケース。
    // .geojsonはバックエンド側でapplication/octet-streamとして配信されることがあるため、
    // "text/htmlでないこと"だけを見る（"jsonを含むこと"を要求すると誤検知する）。
    throw new Error(`${url} -> HTMLが返ってきました（バックエンドが起動していない可能性）`);
  }
  return res.json();
}

const BASE_STYLE = {
  version: 8,
  sources: {
    osm: {
      type: "raster",
      tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
      tileSize: 256,
      attribution: "&copy; OpenStreetMap contributors",
    },
  },
  layers: [{ id: "osm", type: "raster", source: "osm" }],
};

// 対象10町丁目の実bbox（town_boundaries.geojoから算出、2026-09-15 naisui-f4）
const TARGET_BOUNDS = [
  [139.705784, 35.600735],
  [139.729894, 35.614331],
];

// hazard_pdf_derived.geojsonのproperties.colorは公式凡例色そのまま（記録として維持）。
// 表示用の配色はここでdepth_class→色として持つ。OSM基図の薄茶〜橙と衝突して見えづらかったため
// 青灰系に変更した。ponding-layer（自前モデルの湛水推定）は紫系にして、公式図由来の層と色相で区別する
// （2026-09-15 naisui-f4提案、docs未反映・要目視確認）。
const HAZARD_COLOR_BY_CLASS = {
  "0.1m以上0.5m未満": "#bcd2e0",
  "0.5m以上1.0m未満": "#8fb4cf",
  "1.0m以上3.0m未満": "#5e8fb8",
  "3.0m以上5.0m未満": "#33699c",
  "5.0m以上": "#1a4570",
};
const HAZARD_FILL_COLOR_EXPR = [
  "match",
  ["get", "depth_class"],
  ...Object.entries(HAZARD_COLOR_BY_CLASS).flat(),
  "#888888", // 未知クラスのフォールバック
];

// 自前モデルの湛水表示（ponding-layer）の色。tools/export_web_ponding_overlay.py の RAMP_STOPS と合わせる。
const PONDING_RAMP = ["rgb(226,206,242)", "rgb(196,160,230)", "rgb(160,107,212)", "rgb(120,58,180)", "rgb(80,20,130)"];
const HAZARD_FILL_OPACITY = 0.45;
const PONDING_OPACITY = 0.8 * (190 / 255); // raster-opacity × 画像のアルファ

const HAZARD_LEGEND_LABELS = {
  "0.1m以上0.5m未満": "0.1〜0.5m",
  "0.5m以上1.0m未満": "0.5〜1m",
  "1.0m以上3.0m未満": "1〜3m",
  "3.0m以上5.0m未満": "3〜5m",
  "5.0m以上": "5m以上",
};

// 凡例は「何を示しているか」を書く。データの出どころは左下の注記に任せる。
function MapLegend() {
  return (
    <div className="bg-white/90 rounded px-2.5 py-2 text-xs text-gray-800 border border-gray-200 pointer-events-none space-y-2 w-56">
      <div>
        <div className="font-medium">浸水が想定される区域と深さ</div>
        <div className="text-gray-500 mb-1">大雨（1時間153mm・24時間690mm）のとき</div>
        <div className="space-y-0.5">
          {Object.entries(HAZARD_COLOR_BY_CLASS).map(([depthClass, color]) => (
            <div key={depthClass} className="flex items-center gap-1.5">
              <span
                className="inline-block w-4 h-3 border border-gray-300"
                style={{ backgroundColor: color, opacity: HAZARD_FILL_OPACITY + 0.2 }}
              />
              <span>{HAZARD_LEGEND_LABELS[depthClass] ?? depthClass}</span>
            </div>
          ))}
        </div>
      </div>
      <div>
        <div className="font-medium">雨水がたまりやすい場所</div>
        <div className="text-gray-500 mb-1">低い所や道路沿い。濃いほど深い</div>
        <div
          className="h-3 w-full rounded-sm border border-gray-300"
          style={{ backgroundImage: `linear-gradient(to right, ${PONDING_RAMP.join(", ")})`, opacity: PONDING_OPACITY + 0.15 }}
        />
        <div className="flex justify-between text-gray-500 mt-0.5">
          <span>浅い</span>
          <span>深い</span>
        </div>
      </div>
    </div>
  );
}

function boundsOfFeature(feature) {
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  const visit = (coords) => {
    if (typeof coords[0] === "number") {
      const [x, y] = coords;
      if (x < minX) minX = x;
      if (x > maxX) maxX = x;
      if (y < minY) minY = y;
      if (y > maxY) maxY = y;
    } else {
      coords.forEach(visit);
    }
  };
  visit(feature.geometry.coordinates);
  return [[minX, minY], [maxX, maxY]];
}

function focusTown(map, features, townName) {
  const feature = features?.find((item) => item.properties.town_name === townName);
  if (feature) {
    map.fitBounds(boundsOfFeature(feature), { padding: 120, duration: 1200, essential: true });
  }
}

const LAYER_LABELS = {
  hazard: "ハザードレイヤー",
  towns: "町丁目境界",
  ponding: "浸水深オーバーレイ",
  sandbag: "土のう置場",
  shelter: "避難所",
};

export default function MapPanel({ scenarioDetail, selectedTownName, onTownClick }) {
  const containerRef = useRef(null);
  const mapRef = useRef(null);
  const readyRef = useRef(false);
  const townsFeaturesRef = useRef(null);
  const selectedTownNameRef = useRef(selectedTownName);
  const [failedLayers, setFailedLayers] = useState([]);

  // 初期化は一度だけ。以降のシナリオ切替では再生成しない（白画面化を避ける）。
  useEffect(() => {
    const map = new MapLibreMap({
      container: containerRef.current,
      style: BASE_STYLE,
      bounds: TARGET_BOUNDS,
      fitBoundsOptions: { padding: 40 },
    });
    mapRef.current = map;
    map.addControl(new NavigationControl(), "top-right");

    // 地図列の幅は画面幅に応じて変わる。resizeだけでは選択地点の表示範囲が再計算されないため、
    // 選択中の町丁目の境界を現在のコンテナ寸法で再fitする。
    const resizeObserver = new ResizeObserver(() => {
      map.resize();
      if (readyRef.current && selectedTownNameRef.current) {
        focusTown(map, townsFeaturesRef.current, selectedTownNameRef.current);
      }
    });
    resizeObserver.observe(containerRef.current);

    map.on("load", async () => {
      const layers = scenarioDetail.map_layers;

      // データ取得は並行、addLayerは固定順で後から一括して行う。
      // (以前はfetch.then内でaddLayerしており、addLayerの発生順がネットワーク応答順に
      //  左右され、重なり順が非決定になっていた — 2026-09-15 naisui-f4指摘)
      const layerKeys = ["hazard", "towns", "ponding", "sandbag", "shelter"];
      const results = await Promise.allSettled([
        fetchJson(layers.hazard_pdf_derived),
        fetchJson(layers.town_boundaries),
        fetchJson(layers.ponding_overlay_bounds),
        fetchJson(layers.sandbag_locations),
        fetchJson(layers.shelter_locations),
      ]);
      const [hazard, towns, pondingBounds, sandbag, shelter] = results;

      // 失敗したものを記録しつつ、成功したものだけ固定順（下から上へ）で追加する。
      const failed = [];
      results.forEach((result, i) => {
        if (result.status === "rejected") {
          const key = layerKeys[i];
          failed.push(key);
          // eslint-disable-next-line no-console
          console.error(`[MapPanel] ${LAYER_LABELS[key]}の読み込みに失敗:`, result.reason);
        }
      });

      if (towns.status === "fulfilled") {
        townsFeaturesRef.current = towns.value.features;
        map.addSource("towns", { type: "geojson", data: towns.value });
        map.addLayer({
          id: "towns-fill",
          type: "fill",
          source: "towns",
          paint: { "fill-color": "#1c8778", "fill-opacity": 0 },
        });
        map.addLayer({
          id: "towns-line",
          type: "line",
          source: "towns",
          paint: { "line-color": "#1c8778", "line-width": 1 },
        });
        map.addLayer({
          id: "towns-selected",
          type: "line",
          source: "towns",
          paint: { "line-color": "#194843", "line-width": 3 },
          filter: ["==", ["get", "town_name"], "__none__"],
        });
        map.on("click", "towns-fill", (e) => {
          const name = e.features[0]?.properties?.town_name;
          if (name) onTownClick(name);
        });
        map.on("mouseenter", "towns-fill", () => {
          map.getCanvas().style.cursor = "pointer";
        });
        map.on("mouseleave", "towns-fill", () => {
          map.getCanvas().style.cursor = "";
        });
      }

      if (sandbag.status === "fulfilled") {
        map.addSource("sandbag", { type: "geojson", data: sandbag.value });
        map.addLayer({
          id: "sandbag-points",
          type: "circle",
          source: "sandbag",
          paint: {
            "circle-radius": 7,
            "circle-color": "#d97706",
            "circle-stroke-width": 1.5,
            "circle-stroke-color": "#ffffff",
          },
        });
      }

      if (shelter.status === "fulfilled") {
        map.addSource("shelter", { type: "geojson", data: shelter.value });
        // circleレイヤーは丸しか描けないため、■記号のsymbolレイヤーで四角として表示する。
        map.addLayer({
          id: "shelter-points",
          type: "symbol",
          source: "shelter",
          layout: {
            "text-field": "■",
            "text-size": 20,
            "text-allow-overlap": true,
            "text-ignore-placement": true,
          },
          paint: {
            "text-color": "#16a34a",
            "text-halo-color": "#ffffff",
            "text-halo-width": 1.5,
          },
        });
      }

      if (pondingBounds.status === "fulfilled") {
        map.addSource("ponding", {
          type: "image",
          url: layers.ponding_overlay_png,
          coordinates: pondingBounds.value.coordinates,
        });
        map.addLayer({
          id: "ponding-layer",
          type: "raster",
          source: "ponding",
          paint: { "raster-opacity": 0.8 }, // 凡例の PONDING_OPACITY と合わせる
        });
      }

      if (hazard.status === "fulfilled") {
        map.addSource("hazard", { type: "geojson", data: hazard.value });
        map.addLayer({
          id: "hazard-fill",
          type: "fill",
          source: "hazard",
          paint: { "fill-color": HAZARD_FILL_COLOR_EXPR, "fill-opacity": HAZARD_FILL_OPACITY },
        });
      }

      setFailedLayers(failed);
      readyRef.current = true;
      if (selectedTownNameRef.current) {
        focusTown(map, townsFeaturesRef.current, selectedTownNameRef.current);
      }
    });

    return () => {
      resizeObserver.disconnect();
      map.remove();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // シナリオ切替: 着色PNGオーバーレイだけ差し替える。地図全体の再フェッチ・再描画はしない。
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !readyRef.current || !scenarioDetail) return;
    const source = map.getSource("ponding");
    if (!source) return;
    let cancelled = false;
    fetchJson(scenarioDetail.map_layers.ponding_overlay_bounds)
      .then((bounds) => {
        if (cancelled) return;
        source.updateImage({
          url: scenarioDetail.map_layers.ponding_overlay_png,
          coordinates: bounds.coordinates,
        });
      })
      .catch((err) => {
        // eslint-disable-next-line no-console
        console.error("[MapPanel] シナリオ切替時の浸水深オーバーレイ更新に失敗:", err);
      });
    return () => {
      cancelled = true;
    };
  }, [scenarioDetail?.scenario_id]);

  // 選択中の町丁目のハイライト + flyTo（2026-09-15 ユーザー要望、naisui-f4提案）。
  // 重心の座標はハードコードせず、読み込み済みのtown_boundaries.geojsonから都度計算する
  // （境界データが更新されても自動追従する）。
  useEffect(() => {
    selectedTownNameRef.current = selectedTownName;
    const map = mapRef.current;
    if (!map || !readyRef.current || !map.getLayer("towns-selected")) return;
    map.setFilter("towns-selected", ["==", ["get", "town_name"], selectedTownName ?? "__none__"]);
    if (!selectedTownName) return;
    focusTown(map, townsFeaturesRef.current, selectedTownName);
  }, [selectedTownName]);

  return (
    <div className="relative h-full w-full">
      <div ref={containerRef} className="h-full w-full" />
      <div className="absolute top-2 left-2">
        <MapLegend />
      </div>
      <div className="absolute bottom-2 left-2 flex flex-col gap-1 items-start">
        {/* モデルの前提はAPIのmodel（backend/app/data.py MODEL_INFO）から表示する（PLATEAU導入計画 7章）。 */}
        <div className="bg-white/90 rounded px-2 py-1 text-xs text-amber-700 border border-amber-200 pointer-events-none max-w-md">
          <div>{scenarioDetail?.model?.label ?? "校正前のスクリーニング結果"}</div>
          {scenarioDetail?.model && (
            <div className="text-gray-600">
              {scenarioDetail.model.data_versions}。{scenarioDetail.model.not_evaluated}。
            </div>
          )}
        </div>
        {scenarioDetail?.scenario_id === "sc_50mm_const" && (
          <div className="bg-white/90 rounded px-2 py-1 text-xs text-gray-600 border border-gray-200 pointer-events-none">
            このシナリオでは閾値以上の湛水は推定されていません（エラーではありません）
          </div>
        )}
        {failedLayers.length > 0 && (
          <div className="bg-red-50 rounded px-2 py-1 text-xs text-red-700 border border-red-200 pointer-events-none">
            一部のレイヤーを読み込めませんでした: {failedLayers.map((k) => LAYER_LABELS[k]).join("、")}
          </div>
        )}
      </div>
    </div>
  );
}
