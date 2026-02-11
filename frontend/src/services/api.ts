import { ShotRequest, RecommendationResponse } from '../types';

export const getRecommendation = async (
  request: ShotRequest
): Promise<RecommendationResponse> => {
  const response = await fetch('/api/v1/recommendations', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error('Failed to get recommendation');
  }

  return response.json();
};
