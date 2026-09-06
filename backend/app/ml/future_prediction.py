import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json


@dataclass
class PredictionResult:
    """Result of a change prediction"""
    
    # Prediction details
    predicted_change_area: float
    predicted_change_percentage: float
    prediction_horizon_days: int
    confidence: float
    
    # Spatial prediction
    predicted_hotspots: List[Dict]
    
    # Temporal prediction
    predicted_timeline: List[Dict]
    
    # Risk assessment
    risk_level: str
    recommended_actions: List[str]
    
    # Metadata
    prediction_method: str
    generated_at: str
    model_version: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "predicted_change_area": self.predicted_change_area,
            "predicted_change_percentage": self.predicted_change_percentage,
            "prediction_horizon_days": self.prediction_horizon_days,
            "confidence": self.confidence,
            "predicted_hotspots": self.predicted_hotspots,
            "predicted_timeline": self.predicted_timeline,
            "risk_level": self.risk_level,
            "recommended_actions": self.recommended_actions,
            "prediction_method": self.prediction_method,
            "generated_at": self.generated_at,
            "model_version": self.model_version
        }


class FutureChangePredictor:
    """Predict future changes based on historical patterns"""
    
    def __init__(self):
        self.model_version = "1.0.0"
        self.historical_data = {}
    
    def add_historical_data(
        self,
        area_id: int,
        change_events: List[Dict]
    ):
        """Add historical change data for an area"""
        self.historical_data[area_id] = change_events
    
    def predict_future_changes(
        self,
        area_id: int,
        horizon_days: int = 30,
        prediction_method: str = "trend_analysis"
    ) -> PredictionResult:
        """
        Predict future changes for an area.
        
        Args:
            area_id: ID of the area to predict for
            horizon_days: Number of days ahead to predict
            prediction_method: Method to use for prediction
        
        Returns:
            PredictionResult object
        """
        if area_id not in self.historical_data:
            return self._empty_prediction(horizon_days)
        
        historical_events = self.historical_data[area_id]
        
        if len(historical_events) < 3:
            return self._insufficient_data_prediction(horizon_days)
        
        # Select prediction method
        if prediction_method == "trend_analysis":
            return self._predict_with_trend_analysis(
                area_id,
                historical_events,
                horizon_days
            )
        elif prediction_method == "seasonal":
            return self._predict_with_seasonal_model(
                area_id,
                historical_events,
                horizon_days
            )
        else:
            return self._predict_with_trend_analysis(
                area_id,
                historical_events,
                horizon_days
            )
    
    def _predict_with_trend_analysis(
        self,
        area_id: int,
        historical_events: List[Dict],
        horizon_days: int
    ) -> PredictionResult:
        """Predict using trend analysis"""
        # Extract change areas over time
        change_areas = [e.get("change_area", 0) for e in historical_events]
        timestamps = [
            datetime.fromisoformat(e["timestamp"]) if isinstance(e["timestamp"], str)
            else e["timestamp"]
            for e in historical_events
        ]
        
        # Calculate trend
        if len(change_areas) >= 2:
            # Linear regression for trend
            x = np.arange(len(change_areas))
            y = np.array(change_areas)
            
            # Simple linear fit
            slope, intercept = np.polyfit(x, y, 1)
            
            # Predict future change
            future_x = len(change_areas) + (horizon_days / 30)  # Assume monthly data
            predicted_area = max(0, slope * future_x + intercept)
        else:
            predicted_area = np.mean(change_areas)
        
        # Calculate confidence based on variance
        variance = np.var(change_areas) if len(change_areas) > 1 else 0
        mean_change = np.mean(change_areas)
        confidence = max(0.0, min(1.0, 1.0 - variance / (mean_change + 1e-6)))
        
        # Predict hotspots based on historical patterns
        hotspots = self._predict_hotspots(historical_events)
        
        # Generate timeline
        timeline = self._generate_timeline(predicted_area, horizon_days)
        
        # Assess risk
        risk_level = self._assess_prediction_risk(predicted_area, confidence)
        
        # Generate recommendations
        actions = self._generate_recommendations(risk_level, predicted_area)
        
        return PredictionResult(
            predicted_change_area=float(predicted_area),
            predicted_change_percentage=float(predicted_area / 10000 * 100),  # Assume 10000 pixel reference
            prediction_horizon_days=horizon_days,
            confidence=float(confidence),
            predicted_hotspots=hotspots,
            predicted_timeline=timeline,
            risk_level=risk_level,
            recommended_actions=actions,
            prediction_method="trend_analysis",
            generated_at=datetime.utcnow().isoformat(),
            model_version=self.model_version
        )
    
    def _predict_with_seasonal_model(
        self,
        area_id: int,
        historical_events: List[Dict],
        horizon_days: int
    ) -> PredictionResult:
        """Predict using seasonal patterns"""
        # Extract seasonal patterns
        monthly_changes = self._extract_seasonal_patterns(historical_events)
        
        # Get current month
        current_month = datetime.utcnow().month
        
        # Predict based on seasonal average for the target period
        target_months = []
        for day in range(horizon_days):
            target_date = datetime.utcnow() + timedelta(days=day)
            target_months.append(target_date.month)
        
        # Average change for target months
        seasonal_avg = np.mean([
            monthly_changes.get(month, np.mean(list(monthly_changes.values())))
            for month in target_months
        ]) if monthly_changes else 0
        
        predicted_area = seasonal_avg
        
        # Calculate confidence based on seasonal consistency
        if len(monthly_changes) > 1:
            seasonal_variance = np.var(list(monthly_changes.values()))
            confidence = max(0.0, min(1.0, 1.0 - seasonal_variance / (np.mean(list(monthly_changes.values())) + 1e-6)))
        else:
            confidence = 0.5
        
        # Generate other components
        hotspots = self._predict_hotspots(historical_events)
        timeline = self._generate_timeline(predicted_area, horizon_days)
        risk_level = self._assess_prediction_risk(predicted_area, confidence)
        actions = self._generate_recommendations(risk_level, predicted_area)
        
        return PredictionResult(
            predicted_change_area=float(predicted_area),
            predicted_change_percentage=float(predicted_area / 10000 * 100),
            prediction_horizon_days=horizon_days,
            confidence=float(confidence),
            predicted_hotspots=hotspots,
            predicted_timeline=timeline,
            risk_level=risk_level,
            recommended_actions=actions,
            prediction_method="seasonal",
            generated_at=datetime.utcnow().isoformat(),
            model_version=self.model_version
        )
    
    def _extract_seasonal_patterns(
        self,
        historical_events: List[Dict]
    ) -> Dict[int, float]:
        """Extract average change by month"""
        monthly_changes = {}
        
        for event in historical_events:
            timestamp = event.get("timestamp")
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
            
            month = timestamp.month
            change_area = event.get("change_area", 0)
            
            if month not in monthly_changes:
                monthly_changes[month] = []
            monthly_changes[month].append(change_area)
        
        # Calculate averages
        return {
            month: np.mean(changes)
            for month, changes in monthly_changes.items()
        }
    
    def _predict_hotspots(
        self,
        historical_events: List[Dict]
    ) -> List[Dict]:
        """Predict future change hotspots"""
        # In production, this would use spatial clustering
        # For now, return placeholder hotspots
        num_hotspots = min(5, len(historical_events))
        
        hotspots = []
        for i in range(num_hotspots):
            hotspots.append({
                "x": np.random.uniform(0, 100),
                "y": np.random.uniform(0, 100),
                "intensity": np.random.uniform(0.5, 1.0),
                "confidence": np.random.uniform(0.6, 0.9)
            })
        
        return hotspots
    
    def _generate_timeline(
        self,
        predicted_area: float,
        horizon_days: int
    ) -> List[Dict]:
        """Generate predicted timeline of changes"""
        timeline = []
        
        # Divide horizon into periods
        num_periods = min(5, horizon_days // 7)  # Weekly periods
        period_length = horizon_days // num_periods if num_periods > 0 else horizon_days
        
        for i in range(num_periods):
            # Distribute predicted area across periods
            period_area = predicted_area / num_periods
            
            timeline.append({
                "period_start_day": i * period_length,
                "period_end_day": (i + 1) * period_length,
                "predicted_change_area": float(period_area),
                "confidence": max(0.3, 0.9 - i * 0.1)  # Decreasing confidence over time
            })
        
        return timeline
    
    def _assess_prediction_risk(
        self,
        predicted_area: float,
        confidence: float
    ) -> str:
        """Assess risk level of prediction"""
        if predicted_area > 10000 and confidence > 0.7:
            return "high"
        elif predicted_area > 5000 and confidence > 0.5:
            return "medium"
        else:
            return "low"
    
    def _generate_recommendations(
        self,
        risk_level: str,
        predicted_area: float
    ) -> List[str]:
        """Generate recommendations based on prediction"""
        recommendations = []
        
        if risk_level == "high":
            recommendations.extend([
                "Increase monitoring frequency",
                "Prepare contingency plans",
                "Alert relevant stakeholders"
            ])
        elif risk_level == "medium":
            recommendations.extend([
                "Monitor area regularly",
                "Review historical patterns"
            ])
        
        if predicted_area > 10000:
            recommendations.append("Consider preventive measures")
        
        return recommendations
    
    def _empty_prediction(self, horizon_days: int) -> PredictionResult:
        """Return empty prediction when no data available"""
        return PredictionResult(
            predicted_change_area=0.0,
            predicted_change_percentage=0.0,
            prediction_horizon_days=horizon_days,
            confidence=0.0,
            predicted_hotspots=[],
            predicted_timeline=[],
            risk_level="unknown",
            recommended_actions=["Collect historical data for better predictions"],
            prediction_method="none",
            generated_at=datetime.utcnow().isoformat(),
            model_version=self.model_version
        )
    
    def _insufficient_data_prediction(
        self,
        horizon_days: int
    ) -> PredictionResult:
        """Return prediction when insufficient data"""
        return PredictionResult(
            predicted_change_area=0.0,
            predicted_change_percentage=0.0,
            prediction_horizon_days=horizon_days,
            confidence=0.2,
            predicted_hotspots=[],
            predicted_timeline=[],
            risk_level="unknown",
            recommended_actions=["Collect more historical change data"],
            prediction_method="insufficient_data",
            generated_at=datetime.utcnow().isoformat(),
            model_version=self.model_version
        )
    
    def compare_predictions(
        self,
        prediction1: PredictionResult,
        prediction2: PredictionResult
    ) -> Dict:
        """Compare two predictions"""
        return {
            "area_difference": prediction2.predicted_change_area - prediction1.predicted_change_area,
            "confidence_difference": prediction2.confidence - prediction1.confidence,
            "risk_level_change": (prediction1.risk_level, prediction2.risk_level),
            "method_comparison": (prediction1.prediction_method, prediction2.prediction_method)
        }
    
    def validate_prediction(
        self,
        prediction: PredictionResult,
        actual_change: Dict
    ) -> Dict:
        """
        Validate a prediction against actual change.
        
        Args:
            prediction: The prediction to validate
            actual_change: Actual change that occurred
        
        Returns:
            Dict with validation metrics
        """
        predicted_area = prediction.predicted_change_area
        actual_area = actual_change.get("change_area", 0)
        
        # Calculate error metrics
        absolute_error = abs(predicted_area - actual_area)
        relative_error = absolute_error / (actual_area + 1e-6)
        
        # Determine if prediction was accurate
        is_accurate = relative_error < 0.3  # Within 30% error
        
        return {
            "predicted_area": predicted_area,
            "actual_area": actual_area,
            "absolute_error": absolute_error,
            "relative_error": float(relative_error),
            "is_accurate": is_accurate,
            "prediction_confidence": prediction.confidence,
            "validation_date": datetime.utcnow().isoformat()
        }
    
    def export_prediction(self, prediction: PredictionResult) -> str:
        """Export prediction as JSON"""
        return json.dumps(prediction.to_dict(), indent=2)
    
    def import_prediction(self, json_data: str) -> PredictionResult:
        """Import prediction from JSON"""
        data = json.loads(json_data)
        return PredictionResult(**data)
