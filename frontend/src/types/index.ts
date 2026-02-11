export interface ShotRequest {
  analysis_id: string;
  player_id: string;
  hole_id: string;
  weather_condition_id: string;
  pin_location: 'front' | 'center' | 'back';
  current_distance_to_pin_yards: number;
  player_lie: 'tee' | 'fairway' | 'rough' | 'bunker' | 'woods' | 'semi_rough';
  lie_quality?: 'clean' | 'normal' | 'thick' | 'plugged';
  pin_placement_strategy?: 'aggressive' | 'balanced' | 'conservative';
}

export interface PrimaryRecommendation {
  club: string;
  target_area: string;
  expected_carry_yards: number;
  expected_total_yards: number;
  confidence_percent: number;
}

export interface AdjustmentSummary {
  temperature_adjustment_yards: number;
  elevation_adjustment_yards: number;
  wind_adjustment_yards: number;
  rain_adjustment_percent: number;
  lie_adjustment_percent: number;
  human_readable_summary: string[];
}

export interface AlternativeClub {
  club: string;
  confidence_percent: number;
  rationale: string;
}

export interface Hazard {
  hazard_type: 'water' | 'bunker' | 'out_of_bounds' | 'trees';
  location: string;
  distance_from_tee: number;
  risk_level: 'low' | 'medium' | 'high';
}

export interface HazardAnalysis {
  hazards_in_play: Hazard[];
  safe_miss_direction: string;
}

export interface RecommendationResponse {
  recommendation_id: string;
  shot_analysis_id: string;
  primary_recommendation: PrimaryRecommendation;
  adjustment_summary: AdjustmentSummary;
  alternative_clubs?: AlternativeClub[];
  hazard_analysis: HazardAnalysis;
  strategy_notes?: string;
  timestamp: string;
}
