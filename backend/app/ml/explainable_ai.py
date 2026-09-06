import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import json


@dataclass
class FeatureImportance:
    """Importance of a single feature"""
    feature_name: str
    importance_value: float
    direction: str  # "positive" or "negative"
    description: str


@dataclass
class Explanation:
    """Explanation for a model prediction"""
    
    # Prediction info
    prediction: float
    predicted_class: str
    confidence: float
    
    # Feature importance
    feature_importance: List[FeatureImportance]
    
    # Global explanation
    base_value: float
    model_output: float
    
    # Visualization data
    shap_values: List[float]
    feature_names: List[str]
    
    # Summary
    top_factors: List[str]
    explanation_text: str
    
    # Metadata
    explanation_method: str
    generated_at: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "prediction": self.prediction,
            "predicted_class": self.predicted_class,
            "confidence": self.confidence,
            "feature_importance": [
                {
                    "feature_name": fi.feature_name,
                    "importance_value": fi.importance_value,
                    "direction": fi.direction,
                    "description": fi.description
                }
                for fi in self.feature_importance
            ],
            "base_value": self.base_value,
            "model_output": self.model_output,
            "shap_values": self.shap_values,
            "feature_names": self.feature_names,
            "top_factors": self.top_factors,
            "explanation_text": self.explanation_text,
            "explanation_method": self.explanation_method,
            "generated_at": self.generated_at
        }


class ExplainableAI:
    """Explainable AI using SHAP-like methods for model interpretation"""
    
    def __init__(self):
        self.feature_descriptions = {
            "change_area": "Total area of detected change",
            "change_percentage": "Percentage of area that changed",
            "mean_ndvi_change": "Average change in vegetation index",
            "mean_ndwi_change": "Average change in water index",
            "mean_nir_change": "Average change in near-infrared reflectance",
            "mean_red_change": "Average change in red reflectance",
            "spectral_variance": "Variance in spectral changes",
            "duration_days": "Time between image acquisitions",
            "is_human_induced": "Whether change is human-caused",
            "human_confidence": "Confidence in human-caused classification",
            "activity_confidence": "Confidence in activity type classification",
            "proximity_to_water": "Distance to nearest water body",
            "proximity_to_urban": "Distance to nearest urban area",
            "proximity_to_roads": "Distance to nearest road",
            "elevation": "Elevation above sea level",
            "slope": "Terrain slope in degrees",
            "aspect": "Terrain aspect (direction of slope)",
            "population_density": "Population density of area",
            "precipitation": "Annual precipitation",
            "temperature": "Average temperature"
        }
    
    def explain_prediction(
        self,
        model_prediction: Dict,
        feature_values: Dict,
        model_type: str = "change_detection"
    ) -> Explanation:
        """
        Generate explanation for a model prediction.
        
        Args:
            model_prediction: The model's prediction output
            feature_values: Dictionary of feature names to values
            model_type: Type of model (change_detection, classification, etc.)
        
        Returns:
            Explanation object
        """
        # Calculate feature importance using SHAP-like method
        shap_values, base_value = self._calculate_shap_values(
            feature_values,
            model_prediction,
            model_type
        )
        
        # Create feature importance list
        feature_importance = self._create_feature_importance(
            feature_values,
            shap_values
        )
        
        # Sort by importance
        feature_importance.sort(key=lambda x: abs(x.importance_value), reverse=True)
        
        # Get top factors
        top_factors = [fi.feature_name for fi in feature_importance[:5]]
        
        # Generate explanation text
        explanation_text = self._generate_explanation_text(
            model_prediction,
            feature_importance[:3]
        )
        
        return Explanation(
            prediction=model_prediction.get("prediction", 0.0),
            predicted_class=model_prediction.get("predicted_class", "unknown"),
            confidence=model_prediction.get("confidence", 0.5),
            feature_importance=feature_importance,
            base_value=base_value,
            model_output=model_prediction.get("prediction", 0.0),
            shap_values=shap_values,
            feature_names=list(feature_values.keys()),
            top_factors=top_factors,
            explanation_text=explanation_text,
            explanation_method="shap_approximation",
            generated_at=self._get_timestamp()
        )
    
    def _calculate_shap_values(
        self,
        feature_values: Dict,
        model_prediction: Dict,
        model_type: str
    ) -> Tuple[List[float], float]:
        """
        Calculate SHAP values using approximation.
        
        In production, this would use actual SHAP library.
        For now, use a simplified approximation based on feature values.
        """
        features = list(feature_values.keys())
        values = list(feature_values.values())
        
        # Normalize values to 0-1 range
        normalized = self._normalize_values(values)
        
        # Calculate base value (average prediction)
        base_value = 0.5
        
        # Calculate SHAP values as contribution to prediction
        # This is a simplified approximation
        prediction = model_prediction.get("prediction", 0.5)
        
        # Distribute the difference from base value across features
        diff = prediction - base_value
        
        # Calculate feature contributions based on normalized values
        total_norm = sum(normalized) if sum(normalized) > 0 else 1
        shap_values = [
            (norm / total_norm) * diff
            for norm in normalized
        ]
        
        return shap_values, base_value
    
    def _normalize_values(self, values: List[float]) -> List[float]:
        """Normalize values to 0-1 range"""
        if not values:
            return []
        
        min_val = min(values)
        max_val = max(values)
        
        if max_val == min_val:
            return [0.5] * len(values)
        
        return [
            (v - min_val) / (max_val - min_val)
            for v in values
        ]
    
    def _create_feature_importance(
        self,
        feature_values: Dict,
        shap_values: List[float]
    ) -> List[FeatureImportance]:
        """Create feature importance list from SHAP values"""
        features = list(feature_values.keys())
        
        importance_list = []
        for feature, shap_val in zip(features, shap_values):
            direction = "positive" if shap_val > 0 else "negative"
            description = self.feature_descriptions.get(
                feature,
                f"Feature: {feature}"
            )
            
            importance_list.append(FeatureImportance(
                feature_name=feature,
                importance_value=abs(shap_val),
                direction=direction,
                description=description
            ))
        
        return importance_list
    
    def _generate_explanation_text(
        self,
        model_prediction: Dict,
        top_features: List[FeatureImportance]
    ) -> str:
        """Generate human-readable explanation text"""
        predicted_class = model_prediction.get("predicted_class", "unknown")
        confidence = model_prediction.get("confidence", 0.5)
        
        parts = [
            f"The model predicts '{predicted_class}' with {confidence:.1%} confidence."
        ]
        
        if top_features:
            parts.append("\nKey factors influencing this prediction:")
            
            for i, feature in enumerate(top_features, 1):
                direction_text = "increased" if feature.direction == "positive" else "decreased"
                parts.append(
                    f"{i}. {feature.feature_name} ({direction_text} likelihood): "
                    f"{feature.description}"
                )
        
        return "\n".join(parts)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    def explain_global_model(
        self,
        feature_importance_history: List[Dict]
    ) -> Dict:
        """
        Explain global model behavior based on historical predictions.
        
        Args:
            feature_importance_history: List of feature importance from past predictions
        
        Returns:
            Dict with global explanation
        """
        if not feature_importance_history:
            return {
                "message": "No historical data available for global explanation"
            }
        
        # Aggregate feature importance across all predictions
        feature_scores = {}
        feature_counts = {}
        
        for history_item in feature_importance_history:
            for feature_data in history_item.get("feature_importance", []):
                feature_name = feature_data["feature_name"]
                importance = feature_data["importance_value"]
                
                if feature_name not in feature_scores:
                    feature_scores[feature_name] = 0.0
                    feature_counts[feature_name] = 0
                
                feature_scores[feature_name] += importance
                feature_counts[feature_name] += 1
        
        # Calculate average importance
        avg_importance = {
            feature: score / feature_counts[feature]
            for feature, score in feature_scores.items()
        }
        
        # Sort by average importance
        sorted_features = sorted(
            avg_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Generate global explanation
        top_features = sorted_features[:10]
        
        return {
            "top_features": [
                {
                    "feature_name": feature,
                    "average_importance": importance,
                    "description": self.feature_descriptions.get(feature, "")
                }
                for feature, importance in top_features
            ],
            "total_predictions_analyzed": len(feature_importance_history),
            "explanation": (
                f"Based on {len(feature_importance_history)} predictions, "
                f"the most important features are: "
                f"{', '.join([f[0] for f in top_features[:5]])}"
            )
        }
    
    def generate_feature_summary(
        self,
        feature_values: Dict
    ) -> Dict:
        """
        Generate a summary of feature values with context.
        
        Args:
            feature_values: Dictionary of feature names to values
        
        Returns:
            Dict with feature summary
        """
        summary = {}
        
        for feature, value in feature_values.items():
            description = self.feature_descriptions.get(feature, "")
            
            # Add contextual interpretation
            interpretation = self._interpret_feature_value(feature, value)
            
            summary[feature] = {
                "value": value,
                "description": description,
                "interpretation": interpretation
            }
        
        return summary
    
    def _interpret_feature_value(self, feature: str, value: float) -> str:
        """Interpret a feature value in context"""
        interpretations = {
            "change_area": lambda v: f"{'Large' if v > 10000 else 'Small'} area affected ({v:.0f} pixels)",
            "change_percentage": lambda v: f"{'Significant' if v > 10 else 'Minor'} change ({v:.1f}%)",
            "mean_ndvi_change": lambda v: f"{'Vegetation loss' if v < -0.1 else 'Vegetation gain' if v > 0.1 else 'No significant change'}",
            "mean_ndwi_change": lambda v: f"{'Water loss' if v < -0.1 else 'Water gain' if v > 0.1 else 'No significant change'}",
            "duration_days": lambda v: f"{'Rapid' if v < 7 else 'Gradual'} change over {v:.0f} days",
            "is_human_induced": lambda v: f"{'Human-caused' if v else 'Natural'} change",
            "proximity_to_water": lambda v: f"{'Near' if v < 1000 else 'Far from'} water ({v:.0f}m)",
            "proximity_to_urban": lambda v: f"{'Near' if v < 5000 else 'Far from'} urban area ({v:.0f}m)",
            "elevation": lambda v: f"{'High' if v > 1000 else 'Low'} elevation ({v:.0f}m)",
            "slope": lambda v: f"{'Steep' if v > 30 else 'Gentle'} slope ({v:.1f}°)",
            "population_density": lambda v: f"{'High' if v > 1000 else 'Low'} population density ({v:.0f}/km²)"
        }
        
        if feature in interpretations:
            return interpretations[feature](value)
        
        return f"Value: {value:.2f}"
    
    def compare_explanations(
        self,
        explanation1: Explanation,
        explanation2: Explanation
    ) -> Dict:
        """
        Compare two explanations.
        
        Args:
            explanation1: First explanation
            explanation2: Second explanation
        
        Returns:
            Dict with comparison results
        """
        # Compare top factors
        factors1 = set(explanation1.top_factors)
        factors2 = set(explanation2.top_factors)
        
        common_factors = factors1 & factors2
        unique_to_1 = factors1 - factors2
        unique_to_2 = factors2 - factors1
        
        # Compare predictions
        prediction_diff = explanation2.prediction - explanation1.prediction
        
        return {
            "prediction_difference": float(prediction_diff),
            "common_top_factors": list(common_factors),
            "unique_to_first": list(unique_to_1),
            "unique_to_second": list(unique_to_2),
            "confidence_change": explanation2.confidence - explanation1.confidence
        }
    
    def export_explanation(self, explanation: Explanation) -> str:
        """Export explanation as JSON"""
        return json.dumps(explanation.to_dict(), indent=2)
    
    def import_explanation(self, json_data: str) -> Explanation:
        """Import explanation from JSON"""
        data = json.loads(json_data)
        
        feature_importance = [
            FeatureImportance(
                feature_name=fi["feature_name"],
                importance_value=fi["importance_value"],
                direction=fi["direction"],
                description=fi["description"]
            )
            for fi in data["feature_importance"]
        ]
        
        return Explanation(
            prediction=data["prediction"],
            predicted_class=data["predicted_class"],
            confidence=data["confidence"],
            feature_importance=feature_importance,
            base_value=data["base_value"],
            model_output=data["model_output"],
            shap_values=data["shap_values"],
            feature_names=data["feature_names"],
            top_factors=data["top_factors"],
            explanation_text=data["explanation_text"],
            explanation_method=data["explanation_method"],
            generated_at=data["generated_at"]
        )
    
    def generate_visualization_data(
        self,
        explanation: Explanation
    ) -> Dict:
        """
        Generate data for visualizing explanations.
        
        Args:
            explanation: Explanation object
        
        Returns:
            Dict with visualization data
        """
        # Prepare data for various visualization types
        return {
            "bar_chart": {
                "features": [fi.feature_name for fi in explanation.feature_importance[:10]],
                "values": [fi.importance_value for fi in explanation.feature_importance[:10]],
                "directions": [fi.direction for fi in explanation.feature_importance[:10]]
            },
            "waterfall": {
                "base_value": explanation.base_value,
                "contributions": [
                    {
                        "feature": fi.feature_name,
                        "value": fi.importance_value * (1 if fi.direction == "positive" else -1)
                    }
                    for fi in explanation.feature_importance
                ],
                "final_value": explanation.model_output
            },
            "summary_plot": {
                "shap_values": explanation.shap_values,
                "feature_names": explanation.feature_names
            }
        }
