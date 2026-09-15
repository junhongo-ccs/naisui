export default function EvidencePanel({ scenarioDetail, selectedTown }) {
  const townData = selectedTown ? scenarioDetail?.towns?.[selectedTown.slug] : null;

  return (
    <div className="h-full overflow-y-auto p-4 space-y-4 text-sm">
      <div>
        <div className="text-xs text-gray-400 mb-1">校正状態</div>
        <div className="inline-block bg-amber-50 text-amber-700 border border-amber-200 rounded px-2 py-1 text-xs">
          校正前のスクリーニング結果
        </div>
      </div>

      {townData ? (
        <>
          <div>
            <div className="text-xs text-gray-400 mb-1">対象町丁目</div>
            <div className="font-medium">{townData.name}</div>
          </div>
          <div>
            <div className="text-xs text-gray-400 mb-1">推定リスクレベル</div>
            <div className="font-medium">{townData.risk_level}</div>
          </div>
          <div>
            <div className="text-xs text-gray-400 mb-1">
              閾値超過面積割合（{scenarioDetail?.depth_threshold_m}m以上）
            </div>
            <div>{(townData.area_over_threshold_ratio * 100).toFixed(2)}%</div>
          </div>
        </>
      ) : (
        <div className="text-gray-400">町丁目を選択すると詳細が表示されます</div>
      )}

      <div className="pt-2 border-t border-gray-100">
        <div className="text-xs text-gray-400 mb-1">再利用について</div>
        <div className="text-xs text-gray-500">
          同一シナリオのデータはキャッシュから再利用しており、再質問のたびに再計算しません。
        </div>
      </div>
    </div>
  );
}
