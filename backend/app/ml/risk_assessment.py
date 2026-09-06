import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime


class RiskLevel(Enum):
    """Risk severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskCategory(Enum):
    """Categories of risk"""
    ENVIRONMENTAL = "environmental"
    SOCIAL = "social"
    ECONOMIC = "economic"
    REGULATORY = "regulatory"
    SECURITY = "security"


@dataclass
class RiskFactor:
    """Individual risk factor"""
    category: RiskCategory
    name: str
    description: str
    severity: float  # 0.0 to 1.0
    weight: float  # Weight in overall risk calculation
    mitigation: Optional[str]


@dataclass
class RiskAssessment:
    """Complete risk assessment for a change event"""
    
    # Overall risk
    overall_risk_score: float  # 0.0 to 1.0
    risk_level: RiskLevel
    
    # Risk factors
    risk_factors: List[RiskFactor]
    
    # Category scores
    environmental_risk: float
    social_risk: float
    economic_risk: float
    regulatory_risk: float
    security_risk: float
    
    # Recommendations
    immediate_actions: List[str]
    monitoring_recommendations: List[str]
    mitigation_strategies: List[str]
    
    # Metadata
    assessment_date: str
    confidence: float
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "overall_risk_score": self.overall_risk_score,
            "risk_level": self.risk_level.value,
            "risk_factors": [
                {
                    "category": rf.category.value,
                    "name": rf.name,
                    "description": rf.description,
                    "severity": rf.severity,
                    "weight": rf.weight,
                    "mitigation": rf.mitigation
                }
                for rf in self.risk_factors
            ],
            "environmental_risk": self.environmental_risk,
            "social_risk": self.social_risk,
            "economic_risk": self.economic_risk,
            "regulatory_risk": self.regulatory_risk,
            "security_risk": self.security_risk,
            "immediate_actions": self.immediate_actions,
            "monitoring_recommendations": self.monitoring_recommendations,
            "mitigation_strategies": self.mitigation_strategies,
            "assessment_date": self.assessment_date,
            "confidence": self.confidence
        }


class RiskAssessmentEngine:
    """Engine for assessing risk of detected changes"""
    
    def __init__(self):
        self.risk_thresholds = {
            RiskLevel.LOW: 0.25,
            RiskLevel.MEDIUM: 0.5,
            RiskLevel.HIGH: 0.75,
            RiskLevel.CRITICAL: 0.9
        }
    
    def assess_risk(
        self,
        change_data: Dict,
        gis_context: Optional[Dict] = None,
        classification: Optional[Dict] = None,
        temporal_data: Optional[Dict] = None
    ) -> RiskAssessment:
        """
        Perform comprehensive risk assessment.
        
        Args:
            change_data: Change detection results
            gis_context: GIS context information
            classification: Classification results
            temporal_data: Temporal tracking data
        
        Returns:
            RiskAssessment object
        """
        # Extract risk factors from different sources
        risk_factors = []
        
        # Environmental risk factors
        env_factors = self._assess_environmental_risk(change_data, gis_context)
        risk_factors.extend(env_factors)
        
        # Social risk factors
        social_factors = self._assess_social_risk(change_data, gis_context)
        risk_factors.extend(social_factors)
        
        # Economic risk factors
        economic_factors = self._assess_economic_risk(change_data, gis_context)
        risk_factors.extend(economic_factors)
        
        # Regulatory risk factors
        regulatory_factors = self._assess_regulatory_risk(change_data, gis_context)
        risk_factors.extend(regulatory_factors)
        
        # Security risk factors
        security_factors = self._assess_security_risk(change_data, classification)
        risk_factors.extend(security_factors)
        
        # Calculate category scores
        category_scores = self._calculate_category_scores(risk_factors)
        
        # Calculate overall risk score
        overall_score = self._calculate_overall_risk(category_scores)
        
        # Determine risk level
        risk_level = self._determine_risk_level(overall_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            risk_factors,
            category_scores,
            risk_level
        )
        
        return RiskAssessment(
            overall_risk_score=overall_score,
            risk_level=risk_level,
            risk_factors=risk_factors,
            environmental_risk=category_scores[RiskCategory.ENVIRONMENTAL],
            social_risk=category_scores[RiskCategory.SOCIAL],
            economic_risk=category_scores[RiskCategory.ECONOMIC],
            regulatory_risk=category_scores[RiskCategory.REGULATORY],
            security_risk=category_scores[RiskCategory.SECURITY],
            immediate_actions=recommendations["immediate"],
            monitoring_recommendations=recommendations["monitoring"],
            mitigation_strategies=recommendations["mitigation"],
            assessment_date=datetime.utcnow().isoformat(),
            confidence=change_data.get("confidence", 0.5)
        )
    
    def _assess_environmental_risk(
        self,
        change_data: Dict,
        gis_context: Optional[Dict]
    ) -> List[RiskFactor]:
        """Assess environmental risk factors"""
        factors = []
        
        change_area = change_data.get("change_area", 0)
        change_percentage = change_data.get("change_percentage", 0)
        
        # Large area change risk
        if change_area > 10000 or change_percentage > 10:
            factors.append(RiskFactor(
                category=RiskCategory.ENVIRONMENTAL,
                name="large_area_change",
                description=f"Change affects {change_area:.0f} pixels ({change_percentage:.1f}%)",
                severity=min(1.0, change_percentage / 20),
                weight=0.3,
                mitigation="Monitor for ecosystem disruption"
            ))
        
        # Protected area risk
        if gis_context and gis_context.get("is_protected_area"):
            factors.append(RiskFactor(
                category=RiskCategory.ENVIRONMENTAL,
                name="protected_area",
                description=f"Change in {gis_context.get('protected_area_name', 'protected area')}",
                severity=0.9,
                weight=0.4,
                mitigation="Verify compliance with protected area regulations"
            ))
        
        # Water proximity risk
        if gis_context and gis_context.get("proximity_to_water", 10000) < 1000:
            factors.append(RiskFactor(
                category=RiskCategory.ENVIRONMENTAL,
                name="water_proximity",
                description=f"Within {gis_context.get('proximity_to_water'):.0f}m of water body",
                severity=0.7,
                weight=0.25,
                mitigation="Assess water quality impact"
            ))
        
        # Forest proximity risk
        if gis_context and gis_context.get("proximity_to_forest", 20000) < 5000:
            factors.append(RiskFactor(
                category=RiskCategory.ENVIRONMENTAL,
                name="forest_proximity",
                description=f"Near forest edge ({gis_context.get('proximity_to_forest'):.0f}m)",
                severity=0.6,
                weight=0.2,
                mitigation="Evaluate biodiversity impact"
            ))
        
        # Steep slope risk
        if gis_context and gis_context.get("slope", 0) > 30:
            factors.append(RiskFactor(
                category=RiskCategory.ENVIRONMENTAL,
                name="steep_slope",
                description=f"Slope of {gis_context.get('slope'):.1f}° increases erosion risk",
                severity=0.5,
                weight=0.15,
                mitigation="Implement erosion control measures"
            ))
        
        return factors
    
    def _assess_social_risk(
        self,
        change_data: Dict,
        gis_context: Optional[Dict]
    ) -> List[RiskFactor]:
        """Assess social risk factors"""
        factors = []
        
        # Population density risk
        if gis_context:
            pop_density = gis_context.get("population_density", 0)
            if pop_density > 1000:
                factors.append(RiskFactor(
                    category=RiskCategory.SOCIAL,
                    name="high_population_density",
                    description=f"Area has {pop_density:.0f} people/km²",
                    severity=min(1.0, pop_density / 5000),
                    weight=0.4,
                    mitigation="Engage with local communities"
                ))
        
        # Urban area proximity
        if gis_context and gis_context.get("proximity_to_urban", 50000) < 5000:
            factors.append(RiskFactor(
                category=RiskCategory.SOCIAL,
                name="urban_proximity",
                description=f"Near urban area ({gis_context.get('proximity_to_urban'):.0f}m)",
                severity=0.5,
                weight=0.3,
                mitigation="Consider impact on urban services"
            ))
        
        # Road proximity (accessibility risk)
        if gis_context and gis_context.get("proximity_to_roads", 5000) < 500:
            factors.append(RiskFactor(
                category=RiskCategory.SOCIAL,
                name="road_accessibility",
                description=f"High accessibility near roads ({gis_context.get('proximity_to_roads'):.0f}m)",
                severity=0.4,
                weight=0.2,
                mitigation="Monitor for increased human activity"
            ))
        
        return factors
    
    def _assess_economic_risk(
        self,
        change_data: Dict,
        gis_context: Optional[Dict]
    ) -> List[RiskFactor]:
        """Assess economic risk factors"""
        factors = []
        
        # Agricultural land risk
        if gis_context and gis_context.get("land_cover_type") == "cropland":
            factors.append(RiskFactor(
                category=RiskCategory.ECONOMIC,
                name="agricultural_impact",
                description="Change in agricultural area",
                severity=0.6,
                weight=0.4,
                mitigation="Assess food security impact"
            ))
        
        # Infrastructure proximity risk
        if gis_context and gis_context.get("proximity_to_urban", 50000) < 10000:
            factors.append(RiskFactor(
                category=RiskCategory.ECONOMIC,
                name="infrastructure_proximity",
                description="Near existing infrastructure",
                severity=0.4,
                weight=0.3,
                mitigation="Evaluate infrastructure impact"
            ))
        
        # Large change area economic impact
        change_area = change_data.get("change_area", 0)
        if change_area > 50000:
            factors.append(RiskFactor(
                category=RiskCategory.ECONOMIC,
                name="large_scale_change",
                description=f"Large-scale change ({change_area:.0f} pixels)",
                severity=min(1.0, change_area / 100000),
                weight=0.3,
                mitigation="Conduct economic impact assessment"
            ))
        
        return factors
    
    def _assess_regulatory_risk(
        self,
        change_data: Dict,
        gis_context: Optional[Dict]
    ) -> List[RiskFactor]:
        """Assess regulatory risk factors"""
        factors = []
        
        # Protected area violation
        if gis_context and gis_context.get("is_protected_area"):
            factors.append(RiskFactor(
                category=RiskCategory.REGULATORY,
                name="protected_area_violation",
                description=f"Potential violation in {gis_context.get('protected_area_type')}",
                severity=0.95,
                weight=0.5,
                mitigation="Immediate legal review required"
            ))
        
        # Cross-border risk (simplified)
        if gis_context:
            country = gis_context.get("country", "")
            # In production, check if near borders
            factors.append(RiskFactor(
                category=RiskCategory.REGULATORY,
                name="jurisdictional",
                description=f"Located in {country}",
                severity=0.2,
                weight=0.2,
                mitigation="Verify local regulations"
            ))
        
        # Human-induced activity
        if change_data.get("is_human_induced"):
            factors.append(RiskFactor(
                category=RiskCategory.REGULATORY,
                name="human_activity",
                description="Human-induced change may require permits",
                severity=0.5,
                weight=0.3,
                mitigation="Check permit requirements"
            ))
        
        return factors
    
    def _assess_security_risk(
        self,
        change_data: Dict,
        classification: Optional[Dict]
    ) -> List[RiskFactor]:
        """Assess security risk factors"""
        factors = []
        
        # Unusual activity types
        if classification:
            activity_type = classification.get("activity_type", "")
            high_risk_activities = ["mining", "military", "industrial"]
            
            if activity_type in high_risk_activities:
                factors.append(RiskFactor(
                    category=RiskCategory.SECURITY,
                    name="high_risk_activity",
                    description=f"Activity type: {activity_type}",
                    severity=0.7,
                    weight=0.4,
                    mitigation="Security review recommended"
                ))
        
        # Rapid change (suspicious)
        if classification and classification.get("duration_days", 0) < 7:
            factors.append(RiskFactor(
                category=RiskCategory.SECURITY,
                name="rapid_change",
                description="Change occurred over very short period",
                severity=0.6,
                weight=0.3,
                mitigation="Investigate cause of rapid change"
            ))
        
        # Low confidence detection
        confidence = change_data.get("confidence", 1.0)
        if confidence < 0.5:
            factors.append(RiskFactor(
                category=RiskCategory.SECURITY,
                name="low_confidence",
                description=f"Low detection confidence ({confidence:.1%})",
                severity=0.3,
                weight=0.2,
                mitigation="Manual verification required"
            ))
        
        return factors
    
    def _calculate_category_scores(
        self,
        risk_factors: List[RiskFactor]
    ) -> Dict[RiskCategory, float]:
        """Calculate risk scores for each category"""
        category_scores = {
            RiskCategory.ENVIRONMENTAL: 0.0,
            RiskCategory.SOCIAL: 0.0,
            RiskCategory.ECONOMIC: 0.0,
            RiskCategory.REGULATORY: 0.0,
            RiskCategory.SECURITY: 0.0
        }
        
        category_weights = {
            RiskCategory.ENVIRONMENTAL: 0.0,
            RiskCategory.SOCIAL: 0.0,
            RiskCategory.ECONOMIC: 0.0,
            RiskCategory.REGULATORY: 0.0,
            RiskCategory.SECURITY: 0.0
        }
        
        for factor in risk_factors:
            category_scores[factor.category] += factor.severity * factor.weight
            category_weights[factor.category] += factor.weight
        
        # Normalize by total weight
        for category in category_scores:
            if category_weights[category] > 0:
                category_scores[category] /= category_weights[category]
        
        return category_scores
    
    def _calculate_overall_risk(
        self,
        category_scores: Dict[RiskCategory, float]
    ) -> float:
        """Calculate overall risk score from category scores"""
        # Weight categories differently
        weights = {
            RiskCategory.ENVIRONMENTAL: 0.3,
            RiskCategory.SOCIAL: 0.2,
            RiskCategory.ECONOMIC: 0.15,
            RiskCategory.REGULATORY: 0.25,
            RiskCategory.SECURITY: 0.1
        }
        
        overall = sum(
            category_scores[category] * weights[category]
            for category in category_scores
        )
        
        return min(1.0, overall)
    
    def _determine_risk_level(self, score: float) -> RiskLevel:
        """Determine risk level from score"""
        if score >= self.risk_thresholds[RiskLevel.CRITICAL]:
            return RiskLevel.CRITICAL
        elif score >= self.risk_thresholds[RiskLevel.HIGH]:
            return RiskLevel.HIGH
        elif score >= self.risk_thresholds[RiskLevel.MEDIUM]:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _generate_recommendations(
        self,
        risk_factors: List[RiskFactor],
        category_scores: Dict[RiskCategory, float],
        risk_level: RiskLevel
    ) -> Dict[str, List[str]]:
        """Generate recommendations based on risk assessment"""
        immediate = []
        monitoring = []
        mitigation = []
        
        # Immediate actions based on risk level
        if risk_level == RiskLevel.CRITICAL:
            immediate.extend([
                "Immediate investigation required",
                "Alert relevant authorities",
                "Document all evidence"
            ])
        elif risk_level == RiskLevel.HIGH:
            immediate.extend([
                "Schedule urgent review",
                "Notify stakeholders"
            ])
        elif risk_level == RiskLevel.MEDIUM:
            immediate.extend([
                "Add to review queue",
                "Monitor for escalation"
            ])
        
        # Monitoring based on high-risk categories
        if category_scores[RiskCategory.ENVIRONMENTAL] > 0.5:
            monitoring.extend([
                "Monitor environmental indicators",
                "Track ecosystem changes",
                "Assess water quality if near water bodies"
            ])
        
        if category_scores[RiskCategory.SOCIAL] > 0.5:
            monitoring.extend([
                "Monitor local community impact",
                "Track population displacement if applicable"
            ])
        
        if category_scores[RiskCategory.REGULATORY] > 0.5:
            monitoring.extend([
                "Track regulatory compliance",
                "Monitor for legal actions"
            ])
        
        # Mitigation strategies from risk factors
        for factor in risk_factors:
            if factor.severity > 0.6 and factor.mitigation:
                mitigation.append(factor.mitigation)
        
        # Add general mitigation strategies
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            mitigation.extend([
                "Develop comprehensive response plan",
                "Engage with relevant experts",
                "Consider temporary protective measures"
            ])
        
        return {
            "immediate": list(set(immediate)),
            "monitoring": list(set(monitoring)),
            "mitigation": list(set(mitigation))
        }
    
    def compare_risk_assessments(
        self,
        assessment1: RiskAssessment,
        assessment2: RiskAssessment
    ) -> Dict:
        """Compare two risk assessments"""
        return {
            "score_change": assessment2.overall_risk_score - assessment1.overall_risk_score,
            "level_change": (
                assessment1.risk_level.value,
                assessment2.risk_level.value
            ),
            "category_changes": {
                "environmental": assessment2.environmental_risk - assessment1.environmental_risk,
                "social": assessment2.social_risk - assessment1.social_risk,
                "economic": assessment2.economic_risk - assessment1.economic_risk,
                "regulatory": assessment2.regulatory_risk - assessment1.regulatory_risk,
                "security": assessment2.security_risk - assessment1.security_risk
            }
        }
    
    def export_assessment(self, assessment: RiskAssessment) -> str:
        """Export assessment as JSON"""
        import json
        return json.dumps(assessment.to_dict(), indent=2)
    
    def import_assessment(self, json_data: str) -> RiskAssessment:
        """Import assessment from JSON"""
        import json
        data = json.loads(json_data)
        
        risk_factors = [
            RiskFactor(
                category=RiskCategory(rf["category"]),
                name=rf["name"],
                description=rf["description"],
                severity=rf["severity"],
                weight=rf["weight"],
                mitigation=rf["mitigation"]
            )
            for rf in data["risk_factors"]
        ]
        
        return RiskAssessment(
            overall_risk_score=data["overall_risk_score"],
            risk_level=RiskLevel(data["risk_level"]),
            risk_factors=risk_factors,
            environmental_risk=data["environmental_risk"],
            social_risk=data["social_risk"],
            economic_risk=data["economic_risk"],
            regulatory_risk=data["regulatory_risk"],
            security_risk=data["security_risk"],
            immediate_actions=data["immediate_actions"],
            monitoring_recommendations=data["monitoring_recommendations"],
            mitigation_strategies=data["mitigation_strategies"],
            assessment_date=data["assessment_date"],
            confidence=data["confidence"]
        )
