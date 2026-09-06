import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json


@dataclass
class UnreportedChange:
    """Detected unreported change"""
    
    # Location info
    area_id: int
    bounds: Dict
    
    # Change info
    change_area: float
    change_percentage: float
    confidence: float
    
    # Detection info
    detection_date: str
    first_observed: str
    last_observed: str
    
    # Classification
    suspected_type: str
    human_indicated: bool
    
    # Reporting status
    is_reported: bool
    reporting_delay_days: Optional[float]
    
    # Risk assessment
    risk_level: str
    
    # Evidence
    supporting_evidence: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "area_id": self.area_id,
            "bounds": self.bounds,
            "change_area": self.change_area,
            "change_percentage": self.change_percentage,
            "confidence": self.confidence,
            "detection_date": self.detection_date,
            "first_observed": self.first_observed,
            "last_observed": self.last_observed,
            "suspected_type": self.suspected_type,
            "human_indicated": self.human_indicated,
            "is_reported": self.is_reported,
            "reporting_delay_days": self.reporting_delay_days,
            "risk_level": self.risk_level,
            "supporting_evidence": self.supporting_evidence
        }


class UnreportedChangeDetector:
    """Detect changes that may not have been officially reported"""
    
    def __init__(self):
        self.official_reports = {}
        self.detected_changes = {}
    
    def add_official_report(
        self,
        area_id: int,
        report: Dict
    ):
        """Add an official change report"""
        if area_id not in self.official_reports:
            self.official_reports[area_id] = []
        self.official_reports[area_id].append(report)
    
    def add_detected_change(
        self,
        area_id: int,
        change: Dict
    ):
        """Add a detected change from automated analysis"""
        if area_id not in self.detected_changes:
            self.detected_changes[area_id] = []
        self.detected_changes[area_id].append(change)
    
    def detect_unreported_changes(
        self,
        area_id: int,
        time_window_days: int = 90
    ) -> List[UnreportedChange]:
        """
        Detect changes that may not have been officially reported.
        
        Args:
            area_id: ID of the area to analyze
            time_window_days: Time window to look back for unreported changes
        
        Returns:
            List of UnreportedChange objects
        """
        unreported_changes = []
        
        if area_id not in self.detected_changes:
            return unreported_changes
        
        detected = self.detected_changes[area_id]
        official = self.official_reports.get(area_id, [])
        
        # Get current date
        current_date = datetime.utcnow()
        window_start = current_date - timedelta(days=time_window_days)
        
        # Check each detected change
        for change in detected:
            change_date = self._parse_date(change.get("timestamp"))
            
            # Check if within time window
            if change_date and change_date < window_start:
                continue
            
            # Check if this change was reported
            is_reported = self._check_if_reported(change, official)
            
            if not is_reported:
                # Calculate reporting delay
                reporting_delay = None
                if change_date:
                    reporting_delay = (current_date - change_date).total_seconds() / 86400
                
                # Assess risk
                risk_level = self._assess_unreported_risk(change, reporting_delay)
                
                # Generate supporting evidence
                evidence = self._generate_supporting_evidence(change)
                
                unreported_change = UnreportedChange(
                    area_id=area_id,
                    bounds=change.get("bounds", {}),
                    change_area=change.get("change_area", 0),
                    change_percentage=change.get("change_percentage", 0),
                    confidence=change.get("confidence", 0.5),
                    detection_date=current_date.isoformat(),
                    first_observed=change.get("first_detected", change_date.isoformat() if change_date else ""),
                    last_observed=change.get("last_updated", change_date.isoformat() if change_date else ""),
                    suspected_type=change.get("activity_type", "unknown"),
                    human_indicated=change.get("is_human_induced", False),
                    is_reported=is_reported,
                    reporting_delay_days=reporting_delay,
                    risk_level=risk_level,
                    supporting_evidence=evidence
                )
                
                unreported_changes.append(unreported_change)
        
        # Sort by risk level and reporting delay
        unreported_changes.sort(
            key=lambda x: (
                self._risk_level_to_score(x.risk_level),
                x.reporting_delay_days or 0
            ),
            reverse=True
        )
        
        return unreported_changes
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime"""
        if not date_str:
            return None
        if isinstance(date_str, datetime):
            return date_str
        try:
            return datetime.fromisoformat(date_str)
        except:
            return None
    
    def _check_if_reported(
        self,
        detected_change: Dict,
        official_reports: List[Dict]
    ) -> bool:
        """Check if a detected change was officially reported"""
        detected_bounds = detected_change.get("bounds", {})
        detected_area = detected_change.get("change_area", 0)
        detected_date = self._parse_date(detected_change.get("timestamp"))
        
        for report in official_reports:
            report_bounds = report.get("bounds", {})
            report_area = report.get("change_area", 0)
            report_date = self._parse_date(report.get("timestamp"))
            
            # Check spatial overlap
            if self._bounds_overlap(detected_bounds, report_bounds):
                # Check if areas are similar (within 50%)
                if abs(detected_area - report_area) / max(detected_area, report_area, 1) < 0.5:
                    # Check if dates are close (within 30 days)
                    if detected_date and report_date:
                        date_diff = abs((detected_date - report_date).total_seconds() / 86400)
                        if date_diff < 30:
                            return True
        
        return False
    
    def _bounds_overlap(
        self,
        bounds1: Dict,
        bounds2: Dict
    ) -> bool:
        """Check if two bounding boxes overlap"""
        if not bounds1 or not bounds2:
            return False
        
        # Simple bounding box overlap check
        no_overlap = (
            bounds1.get("max_x", 0) < bounds2.get("min_x", 0) or
            bounds1.get("min_x", 0) > bounds2.get("max_x", 0) or
            bounds1.get("max_y", 0) < bounds2.get("min_y", 0) or
            bounds1.get("min_y", 0) > bounds2.get("max_y", 0)
        )
        
        return not no_overlap
    
    def _assess_unreported_risk(
        self,
        change: Dict,
        reporting_delay: Optional[float]
    ) -> str:
        """Assess risk level of unreported change"""
        risk_score = 0.0
        
        # Change area risk
        change_area = change.get("change_area", 0)
        if change_area > 10000:
            risk_score += 0.3
        elif change_area > 5000:
            risk_score += 0.2
        
        # Human-induced risk
        if change.get("is_human_induced"):
            risk_score += 0.3
        
        # Reporting delay risk
        if reporting_delay:
            if reporting_delay > 180:  # 6 months
                risk_score += 0.4
            elif reporting_delay > 90:  # 3 months
                risk_score += 0.3
            elif reporting_delay > 30:  # 1 month
                risk_score += 0.2
        
        # Confidence risk (low confidence might indicate evasion)
        confidence = change.get("confidence", 0.5)
        if confidence < 0.5:
            risk_score += 0.1
        
        # Determine risk level
        if risk_score >= 0.7:
            return "critical"
        elif risk_score >= 0.5:
            return "high"
        elif risk_score >= 0.3:
            return "medium"
        else:
            return "low"
    
    def _risk_level_to_score(self, level: str) -> float:
        """Convert risk level to numeric score"""
        scores = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1
        }
        return scores.get(level, 0)
    
    def _generate_supporting_evidence(self, change: Dict) -> List[str]:
        """Generate list of supporting evidence for unreported change"""
        evidence = []
        
        # Change characteristics
        change_area = change.get("change_area", 0)
        if change_area > 1000:
            evidence.append(f"Significant change area: {change_area:.0f} pixels")
        
        # Human activity
        if change.get("is_human_induced"):
            evidence.append("Change appears to be human-induced")
            activity_type = change.get("activity_type")
            if activity_type and activity_type != "unknown":
                evidence.append(f"Activity type: {activity_type}")
        
        # Temporal pattern
        first_detected = change.get("first_detected")
        last_updated = change.get("last_updated")
        if first_detected and last_updated:
            evidence.append(f"Change observed from {first_detected} to {last_updated}")
        
        # Confidence
        confidence = change.get("confidence", 0)
        if confidence > 0.7:
            evidence.append(f"High detection confidence: {confidence:.1%}")
        
        # Spectral changes
        if "indices" in change:
            indices = change["indices"]
            if "ndvi" in indices:
                ndvi_change = indices["ndvi"]
                if abs(ndvi_change) > 0.2:
                    evidence.append(f"Significant vegetation change: {ndvi_change:.2f}")
        
        return evidence
    
    def analyze_reporting_patterns(
        self,
        area_id: int
    ) -> Dict:
        """
        Analyze reporting patterns for an area.
        
        Args:
            area_id: ID of the area to analyze
        
        Returns:
            Dict with reporting pattern analysis
        """
        detected = self.detected_changes.get(area_id, [])
        official = self.official_reports.get(area_id, [])
        
        # Calculate reporting rate
        total_detected = len(detected)
        total_reported = len(official)
        reporting_rate = total_reported / total_detected if total_detected > 0 else 0
        
        # Calculate average reporting delay
        delays = []
        for change in detected:
            if self._check_if_reported(change, official):
                change_date = self._parse_date(change.get("timestamp"))
                # Find matching report and calculate delay
                for report in official:
                    report_date = self._parse_date(report.get("timestamp"))
                    if change_date and report_date:
                        delay = (report_date - change_date).total_seconds() / 86400
                        delays.append(delay)
                        break
        
        avg_delay = np.mean(delays) if delays else 0
        
        # Identify under-reported areas
        unreported = self.detect_unreported_changes(area_id)
        
        return {
            "area_id": area_id,
            "total_detected_changes": total_detected,
            "total_official_reports": total_reported,
            "reporting_rate": float(reporting_rate),
            "average_reporting_delay_days": float(avg_delay),
            "unreported_changes_count": len(unreported),
            "reporting_quality": self._assess_reporting_quality(reporting_rate, avg_delay)
        }
    
    def _assess_reporting_quality(self, rate: float, avg_delay: float) -> str:
        """Assess overall reporting quality"""
        if rate > 0.8 and avg_delay < 30:
            return "excellent"
        elif rate > 0.6 and avg_delay < 60:
            return "good"
        elif rate > 0.4 and avg_delay < 90:
            return "fair"
        else:
            return "poor"
    
    def generate_unreported_change_report(
        self,
        area_id: int,
        time_window_days: int = 90
    ) -> Dict:
        """Generate a comprehensive report on unreported changes"""
        unreported = self.detect_unreported_changes(area_id, time_window_days)
        patterns = self.analyze_reporting_patterns(area_id)
        
        # Summary statistics
        total_area = sum(c.change_area for c in unreported)
        avg_confidence = np.mean([c.confidence for c in unreported]) if unreported else 0
        
        # Risk breakdown
        risk_counts = {}
        for change in unreported:
            risk_counts[change.risk_level] = risk_counts.get(change.risk_level, 0) + 1
        
        return {
            "area_id": area_id,
            "time_window_days": time_window_days,
            "unreported_changes": [c.to_dict() for c in unreported],
            "summary": {
                "total_unreported": len(unreported),
                "total_change_area": float(total_area),
                "average_confidence": float(avg_confidence),
                "risk_breakdown": risk_counts
            },
            "reporting_patterns": patterns,
            "recommendations": self._generate_reporting_recommendations(patterns, risk_counts),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _generate_reporting_recommendations(
        self,
        patterns: Dict,
        risk_counts: Dict
    ) -> List[str]:
        """Generate recommendations based on reporting patterns"""
        recommendations = []
        
        # Based on reporting rate
        if patterns["reporting_rate"] < 0.5:
            recommendations.append("Improve change reporting compliance")
        
        # Based on reporting delay
        if patterns["average_reporting_delay_days"] > 60:
            recommendations.append("Reduce reporting delays for detected changes")
        
        # Based on risk levels
        if risk_counts.get("critical", 0) > 0:
            recommendations.append("Immediate investigation required for critical unreported changes")
        if risk_counts.get("high", 0) > 2:
            recommendations.append("Prioritize investigation of high-risk unreported changes")
        
        # General recommendations
        if patterns["reporting_quality"] == "poor":
            recommendations.extend([
                "Implement automated reporting system",
                "Establish reporting protocols and training",
                "Set up monitoring and alerting for unreported changes"
            ])
        
        return recommendations
    
    def export_unreported_change(self, change: UnreportedChange) -> str:
        """Export unreported change as JSON"""
        return json.dumps(change.to_dict(), indent=2)
    
    def import_unreported_change(self, json_data: str) -> UnreportedChange:
        """Import unreported change from JSON"""
        data = json.loads(json_data)
        return UnreportedChange(**data)
