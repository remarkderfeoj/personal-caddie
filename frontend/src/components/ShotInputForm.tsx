import { useState } from 'react';
import { ShotRequest } from '../types';

interface ShotInputFormProps {
  onSubmit: (request: ShotRequest) => void;
  isLoading: boolean;
}

export const ShotInputForm: React.FC<ShotInputFormProps> = ({ onSubmit, isLoading }) => {
  const [distance, setDistance] = useState(110);
  const [pinLocation, setPinLocation] = useState<'front' | 'center' | 'back'>('front');
  const [lie, setLie] = useState<'tee' | 'fairway' | 'rough' | 'bunker' | 'woods' | 'semi_rough'>('fairway');
  const [lieQuality, setLieQuality] = useState<'clean' | 'normal' | 'thick' | 'plugged'>('clean');
  const [strategy, setStrategy] = useState<'aggressive' | 'balanced' | 'conservative'>('balanced');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const request: ShotRequest = {
      analysis_id: `shot_${Date.now()}`,
      player_id: 'joe_kramer_001',
      hole_id: 'pebble_7',
      weather_condition_id: 'weather_001',
      pin_location: pinLocation,
      current_distance_to_pin_yards: distance,
      player_lie: lie,
      lie_quality: lieQuality,
      pin_placement_strategy: strategy,
    };

    onSubmit(request);
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6 space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Shot Context</h2>

      {/* Distance Input */}
      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Distance to Pin (yards)
        </label>
        <input
          type="number"
          value={distance}
          onChange={(e) => setDistance(parseInt(e.target.value))}
          min="30"
          max="300"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-golf-green"
        />
      </div>

      {/* Pin Location */}
      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-3">
          Pin Location
        </label>
        <div className="flex gap-4">
          {(['front', 'center', 'back'] as const).map((loc) => (
            <label key={loc} className="flex items-center">
              <input
                type="radio"
                value={loc}
                checked={pinLocation === loc}
                onChange={(e) => setPinLocation(e.target.value as typeof pinLocation)}
                className="w-4 h-4 text-golf-green"
              />
              <span className="ml-2 text-gray-700 capitalize">{loc}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Lie Selector */}
      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Ball Lie
        </label>
        <select
          value={lie}
          onChange={(e) => setLie(e.target.value as typeof lie)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-golf-green"
        >
          <option value="tee">Tee</option>
          <option value="fairway">Fairway</option>
          <option value="semi_rough">Semi-Rough</option>
          <option value="rough">Rough</option>
          <option value="bunker">Bunker</option>
          <option value="woods">Woods</option>
        </select>
      </div>

      {/* Lie Quality */}
      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Lie Quality
        </label>
        <select
          value={lieQuality}
          onChange={(e) => setLieQuality(e.target.value as typeof lieQuality)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-golf-green"
        >
          <option value="clean">Clean</option>
          <option value="normal">Normal</option>
          <option value="thick">Thick</option>
          <option value="plugged">Plugged</option>
        </select>
      </div>

      {/* Strategy */}
      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-3">
          Playing Strategy
        </label>
        <div className="flex gap-4">
          {(['aggressive', 'balanced', 'conservative'] as const).map((strat) => (
            <label key={strat} className="flex items-center">
              <input
                type="radio"
                value={strat}
                checked={strategy === strat}
                onChange={(e) => setStrategy(e.target.value as typeof strategy)}
                className="w-4 h-4 text-golf-green"
              />
              <span className="ml-2 text-gray-700 capitalize">{strat}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-golf-green hover:bg-green-600 disabled:bg-gray-400 text-white font-bold py-3 px-4 rounded-lg transition duration-200"
      >
        {isLoading ? 'Getting Recommendation...' : 'Get Recommendation'}
      </button>
    </form>
  );
};
