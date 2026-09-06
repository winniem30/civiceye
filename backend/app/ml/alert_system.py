import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import json


class AlertSeverity(Enum):
    """Severity levels for alerts"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertCategory(Enum):
    """Categories of alerts"""
    CHANGE_DETECTED = "change_detected"
    RISK_ASSESSMENT = "risk_assessment"
    UNREPORTED_CHANGE = "unreported_change"
    PREDICTION_ALERT = "prediction_alert"
    VERIFICATION_REQUIRED = "verification_required"
    SYSTEM_STATUS = "system_status"


@dataclass
class Alert:
    """Alert notification"""
    
    alert_id: str
    category: AlertCategory
    severity: AlertSeverity
    title: str
    description: str
    area_id: Optional[int]
    change_event_id: Optional[int]
    metadata: Dict
    created_at: str
    acknowledged: bool
    acknowledged_by: Optional[int]
    acknowledged_at: Optional[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "alert_id": self.alert_id,
            "category": self.category.value,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "area_id": self.area_id,
            "change_event_id": self.change_event_id,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "acknowledged": self.acknowledged,
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": self.acknowledged_at
        }


@dataclass
class AlertRule:
    """Rule for generating alerts"""
    
    rule_id: str
    name: str
    category: AlertCategory
    condition: str
    severity: AlertSeverity
    enabled: bool
    metadata: Dict
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "category": self.category.value,
            "condition": self.condition,
            "severity": self.severity.value,
            "enabled": self.enabled,
            "metadata": self.metadata
        }


@dataclass
class DashboardMetrics:
    """Metrics for dashboard display"""
    
    total_alerts: int
    active_alerts: int
    acknowledged_alerts: int
    severity_breakdown: Dict[str, int]
    category_breakdown: Dict[str, int]
    recent_alerts: List[Alert]
    trend_data: List[Dict]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "total_alerts": self.total_alerts,
            "active_alerts": self.active_alerts,
            "acknowledged_alerts": self.acknowledged_alerts,
            "severity_breakdown": self.severity_breakdown,
            "category_breakdown": self.category_breakdown,
            "recent_alerts": [a.to_dict() for a in self.recent_alerts],
            "trend_data": self.trend_data
        }


class AlertSystem:
    """System for generating and managing alerts"""
    
    def __init__(self):
        self.alerts = {}
        self.alert_rules = self._initialize_default_rules()
        self.user_subscriptions = {}
    
    def _initialize_default_rules(self) -> Dict[str, AlertRule]:
        """Initialize default alert rules"""
        return {
            "large_change": AlertRule(
                rule_id="large_change",
                name="Large Area Change",
                category=AlertCategory.CHANGE_DETECTED,
                condition="change_area > 10000",
                severity=AlertSeverity.HIGH,
                enabled=True,
                metadata={"threshold": 10000}
            ),
            "protected_area": AlertRule(
                rule_id="protected_area",
                name="Protected Area Change",
                category=AlertCategory.CHANGE_DETECTED,
                condition="is_protected_area == true",
                severity=AlertSeverity.CRITICAL,
                enabled=True,
                metadata={}
            ),
            "high_risk": AlertRule(
                rule_id="high_risk",
                name="High Risk Assessment",
                category=AlertCategory.RISK_ASSESSMENT,
                condition="risk_score > 0.7",
                severity=AlertSeverity.HIGH,
                enabled=True,
                metadata={"threshold": 0.7}
            ),
            "unreported_change": AlertRule(
                rule_id="unreported_change",
                name="Unreported Change Detected",
                category=AlertCategory.UNREPORTED_CHANGE,
                condition="is_reported == false AND reporting_delay > 30",
                severity=AlertSeverity.MEDIUM,
                enabled=True,
                metadata={"delay_threshold": 30}
            ),
            "prediction_alert": AlertRule(
                rule_id="prediction_alert",
                name="Future Change Prediction",
                category=AlertCategory.PREDICTION_ALERT,
                condition="predicted_area > 5000 AND confidence > 0.7",
                severity=AlertSeverity.MEDIUM,
                enabled=True,
                metadata={}
            )
        }
    
    def evaluate_alert_rules(
        self,
        change_data: Dict,
        gis_context: Optional[Dict] = None,
        risk_assessment: Optional[Dict] = None
    ) -> List[Alert]:
        """
        Evaluate alert rules against change data.
        
        Args:
            change_data: Change detection data
            gis_context: Optional GIS context
            risk_assessment: Optional risk assessment
        
        Returns:
            List of generated alerts
        """
        generated_alerts = []
        
        for rule_id, rule in self.alert_rules.items():
            if not rule.enabled:
                continue
            
            # Evaluate rule condition
            if self._evaluate_condition(rule.condition, change_data, gis_context, risk_assessment):
                alert = self._create_alert_from_rule(rule, change_data, gis_context)
                generated_alerts.append(alert)
        
        return generated_alerts
    
    def _evaluate_condition(
        self,
        condition: str,
        change_data: Dict,
        gis_context: Optional[Dict],
        risk_assessment: Optional[Dict]
    ) -> bool:
        """Evaluate a rule condition"""
        # Simple condition evaluation (in production, use a proper expression parser)
        
        # Large change
        if "change_area > 10000" in condition:
            return change_data.get("change_area", 0) > 10000
        
        # Protected area
        if "is_protected_area == true" in condition:
            return gis_context and gis_context.get("is_protected_area", False)
        
        # High risk
        if "risk_score > 0.7" in condition:
            return risk_assessment and risk_assessment.get("risk_score", 0) > 0.7
        
        # Unreported change
        if "is_reported == false" in condition:
            return not change_data.get("is_reported", True)
        
        # Prediction alert
        if "predicted_area > 5000" in condition:
            return change_data.get("predicted_area", 0) > 5000
        
        return False
    
    def _create_alert_from_rule(
        self,
        rule: AlertRule,
        change_data: Dict,
        gis_context: Optional[Dict]
    ) -> Alert:
        """Create an alert from a rule"""
        alert_id = f"alert_{datetime.utcnow().timestamp()}"
        
        # Generate title and description based on rule
        title = rule.name
        description = f"Alert triggered by rule: {rule.name}"
        
        # Add context to description
        if gis_context and gis_context.get("is_protected_area"):
            description += f" in {gis_context.get('protected_area_name', 'protected area')}"
        
        alert = Alert(
            alert_id=alert_id,
            category=rule.category,
            severity=rule.severity,
            title=title,
            description=description,
            area_id=change_data.get("area_id"),
            change_event_id=change_data.get("change_event_id"),
            metadata={
                "rule_id": rule.rule_id,
                "change_data": change_data,
                "gis_context": gis_context or {}
            },
            created_at=datetime.utcnow().isoformat(),
            acknowledged=False,
            acknowledged_by=None,
            acknowledged_at=None
        )
        
        self.alerts[alert_id] = alert
        return alert
    
    def create_manual_alert(
        self,
        category: str,
        severity: str,
        title: str,
        description: str,
        area_id: Optional[int] = None,
        change_event_id: Optional[int] = None,
        metadata: Optional[Dict] = None
    ) -> Alert:
        """
        Create a manual alert.
        
        Args:
            category: Alert category
            severity: Alert severity
            title: Alert title
            description: Alert description
            area_id: Optional area ID
            change_event_id: Optional change event ID
            metadata: Optional metadata
        
        Returns:
            Alert object
        """
        alert_id = f"manual_alert_{datetime.utcnow().timestamp()}"
        
        alert = Alert(
            alert_id=alert_id,
            category=AlertCategory(category),
            severity=AlertSeverity(severity),
            title=title,
            description=description,
            area_id=area_id,
            change_event_id=change_event_id,
            metadata=metadata or {},
            created_at=datetime.utcnow().isoformat(),
            acknowledged=False,
            acknowledged_by=None,
            acknowledged_at=None
        )
        
        self.alerts[alert_id] = alert
        return alert
    
    def acknowledge_alert(
        self,
        alert_id: str,
        user_id: int
    ) -> Optional[Alert]:
        """
        Acknowledge an alert.
        
        Args:
            alert_id: ID of the alert
            user_id: ID of the user acknowledging
        
        Returns:
            Updated Alert or None
        """
        if alert_id not in self.alerts:
            return None
        
        alert = self.alerts[alert_id]
        alert.acknowledged = True
        alert.acknowledged_by = user_id
        alert.acknowledged_at = datetime.utcnow().isoformat()
        
        return alert
    
    def get_alert(
        self,
        alert_id: str
    ) -> Optional[Alert]:
        """Get an alert by ID"""
        return self.alerts.get(alert_id)
    
    def get_alerts(
        self,
        severity: Optional[str] = None,
        category: Optional[str] = None,
        acknowledged: Optional[bool] = None,
        area_id: Optional[int] = None,
        limit: int = 100
    ) -> List[Alert]:
        """
        Get filtered list of alerts.
        
        Args:
            severity: Optional severity filter
            category: Optional category filter
            acknowledged: Optional acknowledged filter
            area_id: Optional area ID filter
            limit: Maximum number of alerts to return
        
        Returns:
            List of Alert objects
        """
        alerts = list(self.alerts.values())
        
        # Apply filters
        if severity:
            alerts = [a for a in alerts if a.severity.value == severity]
        if category:
            alerts = [a for a in alerts if a.category.value == category]
        if acknowledged is not None:
            alerts = [a for a in alerts if a.acknowledged == acknowledged]
        if area_id:
            alerts = [a for a in alerts if a.area_id == area_id]
        
        # Sort by creation date (newest first)
        alerts.sort(key=lambda a: a.created_at, reverse=True)
        
        return alerts[:limit]
    
    def get_dashboard_metrics(
        self,
        time_window_days: int = 30
    ) -> DashboardMetrics:
        """
        Get metrics for dashboard display.
        
        Args:
            time_window_days: Time window for metrics
        
        Returns:
            DashboardMetrics object
        """
        # Get alerts within time window
        cutoff_date = datetime.utcnow() - timedelta(days=time_window_days)
        recent_alerts = [
            a for a in self.alerts.values()
            if datetime.fromisoformat(a.created_at) >= cutoff_date
        ]
        
        # Calculate metrics
        total_alerts = len(recent_alerts)
        active_alerts = len([a for a in recent_alerts if not a.acknowledged])
        acknowledged_alerts = len([a for a in recent_alerts if a.acknowledged])
        
        # Severity breakdown
        severity_breakdown = {}
        for alert in recent_alerts:
            severity = alert.severity.value
            severity_breakdown[severity] = severity_breakdown.get(severity, 0) + 1
        
        # Category breakdown
        category_breakdown = {}
        for alert in recent_alerts:
            category = alert.category.value
            category_breakdown[category] = category_breakdown.get(category, 0) + 1
        
        # Recent alerts (last 10)
        recent_alerts_sorted = sorted(recent_alerts, key=lambda a: a.created_at, reverse=True)[:10]
        
        # Trend data (daily counts)
        trend_data = self._generate_trend_data(recent_alerts, time_window_days)
        
        return DashboardMetrics(
            total_alerts=total_alerts,
            active_alerts=active_alerts,
            acknowledged_alerts=acknowledged_alerts,
            severity_breakdown=severity_breakdown,
            category_breakdown=category_breakdown,
            recent_alerts=recent_alerts_sorted,
            trend_data=trend_data
        )
    
    def _generate_trend_data(
        self,
        alerts: List[Alert],
        days: int
    ) -> List[Dict]:
        """Generate trend data for alerts over time"""
        trend = []
        
        for day in range(days):
            date = datetime.utcnow() - timedelta(days=days - day - 1)
            date_str = date.strftime("%Y-%m-%d")
            
            # Count alerts for this day
            day_alerts = [
                a for a in alerts
                if datetime.fromisoformat(a.created_at).date() == date.date()
            ]
            
            trend.append({
                "date": date_str,
                "count": len(day_alerts),
                "by_severity": {
                    severity.value: len([a for a in day_alerts if a.severity == severity])
                    for severity in AlertSeverity
                }
            })
        
        return trend
    
    def add_alert_rule(
        self,
        rule: AlertRule
    ):
        """Add a new alert rule"""
        self.alert_rules[rule.rule_id] = rule
    
    def update_alert_rule(
        self,
        rule_id: str,
        updates: Dict
    ) -> Optional[AlertRule]:
        """Update an existing alert rule"""
        if rule_id not in self.alert_rules:
            return None
        
        rule = self.alert_rules[rule_id]
        
        if "enabled" in updates:
            rule.enabled = updates["enabled"]
        if "severity" in updates:
            rule.severity = AlertSeverity(updates["severity"])
        if "condition" in updates:
            rule.condition = updates["condition"]
        if "metadata" in updates:
            rule.metadata = updates["metadata"]
        
        return rule
    
    def delete_alert_rule(self, rule_id: str) -> bool:
        """Delete an alert rule"""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            return True
        return False
    
    def get_alert_rules(self) -> List[AlertRule]:
        """Get all alert rules"""
        return list(self.alert_rules.values())
    
    def subscribe_user_to_alerts(
        self,
        user_id: int,
        categories: Optional[List[str]] = None,
        severities: Optional[List[str]] = None
    ):
        """Subscribe a user to alerts"""
        if user_id not in self.user_subscriptions:
            self.user_subscriptions[user_id] = {}
        
        self.user_subscriptions[user_id] = {
            "categories": categories or [],
            "severities": severities or []
        }
    
    def get_user_alerts(
        self,
        user_id: int,
        limit: int = 50
    ) -> List[Alert]:
        """Get alerts for a subscribed user"""
        if user_id not in self.user_subscriptions:
            return []
        
        subscription = self.user_subscriptions[user_id]
        categories = subscription.get("categories", [])
        severities = subscription.get("severities", [])
        
        # Filter alerts by subscription
        user_alerts = []
        for alert in self.alerts.values():
            # Check category
            if categories and alert.category.value not in categories:
                continue
            # Check severity
            if severities and alert.severity.value not in severities:
                continue
            
            user_alerts.append(alert)
        
        # Sort by creation date
        user_alerts.sort(key=lambda a: a.created_at, reverse=True)
        
        return user_alerts[:limit]
    
    def export_alert(self, alert: Alert) -> str:
        """Export alert as JSON"""
        return json.dumps(alert.to_dict(), indent=2)
    
    def import_alert(self, json_data: str) -> Alert:
        """Import alert from JSON"""
        data = json.loads(json_data)
        return Alert(**data)
