import { useState } from 'react';
import { ShotRequest, RecommendationResponse } from './types';
import { getRecommendation } from './services/api';
import { ShotInputForm } from './components/ShotInputForm';
import { RecommendationCard } from './components/RecommendationCard';
import { AdjustmentDetails } from './components/AdjustmentDetails';
import { HazardWarnings } from './components/HazardWarnings';
import { AlternativeClubs } from './components/AlternativeClubs';

function App() {
  const [recommendation, setRecommendation] = useState<RecommendationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (request: ShotRequest) => {
    setIsLoading(true);
    setError(null);
    setRecommendation(null);

    try {
      const response = await getRecommendation(request);
      setRecommendation(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get recommendation');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-golf-green text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-4xl font-bold">🏌️ Personal Caddie</h1>
          <p className="text-green-100 mt-2">AI-Powered Golf Shot Advisor</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Form */}
          <div className="lg:col-span-1">
            <ShotInputForm onSubmit={handleSubmit} isLoading={isLoading} />
          </div>

          {/* Right Column - Results */}
          <div className="lg:col-span-2">
            {isLoading && (
              <div className="flex flex-col items-center justify-center h-96">
                <div className="spinner mb-4"></div>
                <p className="text-gray-600 text-lg">Getting your recommendation...</p>
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-300 rounded-lg p-6">
                <h3 className="text-red-800 font-bold mb-2">Error</h3>
                <p className="text-red-700">{error}</p>
                <p className="text-sm text-red-600 mt-2">
                  Make sure the backend API is running on http://localhost:8000
                </p>
              </div>
            )}

            {recommendation && !isLoading && (
              <div className="space-y-6 animate-fadeIn">
                <RecommendationCard
                  recommendation={recommendation.primary_recommendation}
                  targetArea={recommendation.primary_recommendation.target_area}
                />

                <AdjustmentDetails adjustments={recommendation.adjustment_summary} />

                <HazardWarnings hazardAnalysis={recommendation.hazard_analysis} />

                {recommendation.strategy_notes && (
                  <div className="bg-blue-50 border border-blue-300 rounded-lg p-6">
                    <h3 className="text-lg font-bold text-blue-900 mb-2">Strategy Notes</h3>
                    <p className="text-blue-800">{recommendation.strategy_notes}</p>
                  </div>
                )}

                <AlternativeClubs clubs={recommendation.alternative_clubs} />
              </div>
            )}

            {!recommendation && !isLoading && !error && (
              <div className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
                <p className="text-gray-600 text-lg">
                  Fill out the form on the left and click "Get Recommendation" to see your personalized shot advice.
                </p>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-gray-400 mt-12 py-6 text-center">
        <p>Personal Caddie © 2024 | Powered by AI Golf Physics Engine</p>
      </footer>
    </div>
  );
}

export default App;
