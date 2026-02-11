import { PrimaryRecommendation } from '../types';

interface RecommendationCardProps {
  recommendation: PrimaryRecommendation;
  targetArea: string;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({
  recommendation,
  targetArea,
}) => {
  return (
    <div className="bg-gradient-to-br from-golf-green to-green-600 rounded-lg shadow-lg p-8 text-white">
      <div className="text-center">
        <p className="text-sm font-semibold opacity-90 mb-2">Recommended Club</p>
        <h1 className="text-5xl font-bold mb-2 uppercase">{recommendation.club}</h1>
        <p className="text-lg opacity-90">Shot for {recommendation.expected_total_yards} yards</p>
      </div>

      <div className="grid grid-cols-2 gap-6 mt-8 pt-8 border-t border-white/30">
        <div className="text-center">
          <p className="text-sm opacity-90 mb-1">Carry Distance</p>
          <p className="text-3xl font-bold">{recommendation.expected_carry_yards}y</p>
        </div>
        <div className="text-center">
          <p className="text-sm opacity-90 mb-1">Total Distance</p>
          <p className="text-3xl font-bold">{recommendation.expected_total_yards}y</p>
        </div>
      </div>

      <div className="mt-8">
        <p className="text-sm font-semibold mb-2">Target Area</p>
        <p className="text-lg opacity-95">{targetArea}</p>
      </div>

      <div className="mt-6">
        <p className="text-sm font-semibold mb-2">Confidence</p>
        <div className="bg-white/30 rounded-full h-3 overflow-hidden">
          <div
            className="bg-white h-full rounded-full transition-all duration-500"
            style={{ width: `${recommendation.confidence_percent}%` }}
          />
        </div>
        <p className="text-center text-sm mt-1">{recommendation.confidence_percent}%</p>
      </div>
    </div>
  );
};
