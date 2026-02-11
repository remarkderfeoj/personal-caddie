import { HazardAnalysis } from '../types';

interface HazardWarningsProps {
  hazardAnalysis: HazardAnalysis;
}

export const HazardWarnings: React.FC<HazardWarningsProps> = ({ hazardAnalysis }) => {
  const getHazardIcon = (type: string): string => {
    switch (type) {
      case 'water':
        return '💧';
      case 'bunker':
        return '🏜️';
      case 'out_of_bounds':
        return '⛔';
      case 'trees':
        return '🌲';
      default:
        return '⚠️';
    }
  };

  const getRiskColor = (risk: string): string => {
    switch (risk) {
      case 'high':
        return 'bg-red-50 border-red-300';
      case 'medium':
        return 'bg-yellow-50 border-yellow-300';
      case 'low':
        return 'bg-blue-50 border-blue-300';
      default:
        return 'bg-gray-50 border-gray-300';
    }
  };

  const getRiskBadgeColor = (risk: string): string => {
    switch (risk) {
      case 'high':
        return 'bg-red-200 text-red-800';
      case 'medium':
        return 'bg-yellow-200 text-yellow-800';
      case 'low':
        return 'bg-blue-200 text-blue-800';
      default:
        return 'bg-gray-200 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-bold text-gray-800 mb-4">Hazard Analysis</h3>

      {hazardAnalysis.hazards_in_play.length > 0 ? (
        <div className="space-y-3 mb-6">
          {hazardAnalysis.hazards_in_play.map((hazard, idx) => (
            <div
              key={idx}
              className={`p-4 border-l-4 rounded ${getRiskColor(hazard.risk_level)}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <span className="text-2xl">{getHazardIcon(hazard.hazard_type)}</span>
                  <div>
                    <p className="font-semibold text-gray-800 capitalize">
                      {hazard.hazard_type.replace('_', ' ')} on {hazard.location}
                    </p>
                    <p className="text-sm text-gray-600">
                      {hazard.distance_from_tee} yards from tee
                    </p>
                  </div>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getRiskBadgeColor(hazard.risk_level)}`}>
                  {hazard.risk_level.toUpperCase()}
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-600 italic mb-6">No major hazards in play</p>
      )}

      <div className="pt-4 border-t border-gray-200">
        <p className="text-sm font-semibold text-gray-800 mb-2">Safe Miss Direction</p>
        <p className="text-lg font-bold text-golf-green capitalize">
          {hazardAnalysis.safe_miss_direction}
        </p>
      </div>
    </div>
  );
};
