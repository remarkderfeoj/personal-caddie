import { AdjustmentSummary } from '../types';

interface AdjustmentDetailsProps {
  adjustments: AdjustmentSummary;
}

export const AdjustmentDetails: React.FC<AdjustmentDetailsProps> = ({ adjustments }) => {
  const adjustmentItems = [
    { label: 'Temperature', value: adjustments.temperature_adjustment_yards, unit: 'y' },
    { label: 'Elevation', value: adjustments.elevation_adjustment_yards, unit: 'y' },
    { label: 'Wind', value: adjustments.wind_adjustment_yards, unit: 'y' },
    { label: 'Rain', value: adjustments.rain_adjustment_percent * 100, unit: '%' },
    { label: 'Lie Quality', value: adjustments.lie_adjustment_percent * 100, unit: '%' },
  ].filter((item) => item.value !== 0);

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-bold text-gray-800 mb-4">Distance Adjustments</h3>

      {adjustmentItems.length > 0 ? (
        <div className="space-y-3">
          {adjustmentItems.map((item) => (
            <div key={item.label} className="flex items-center justify-between p-3 bg-gray-50 rounded">
              <span className="text-gray-700 font-semibold">{item.label}</span>
              <span
                className={`text-lg font-bold ${
                  item.value > 0 ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {item.value > 0 ? '+' : ''}{item.value.toFixed(0)}{item.unit}
              </span>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-600 italic">No significant adjustments</p>
      )}

      <div className="mt-6 pt-4 border-t border-gray-200">
        <h4 className="font-semibold text-gray-800 mb-2">Summary</h4>
        <ul className="space-y-1">
          {adjustments.human_readable_summary.map((summary, idx) => (
            <li key={idx} className="text-sm text-gray-700">
              • {summary}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};
