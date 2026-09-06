import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import json


@dataclass
class ReportSection:
    """Section of a report"""
    
    section_id: str
    title: str
    content: str
    order: int
    include_table: bool
    include_chart: bool
    table_data: Optional[Dict]
    chart_data: Optional[Dict]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "section_id": self.section_id,
            "title": self.title,
            "content": self.content,
            "order": self.order,
            "include_table": self.include_table,
            "include_chart": self.include_chart,
            "table_data": self.table_data,
            "chart_data": self.chart_data
        }


@dataclass
class Report:
    """Generated report"""
    
    report_id: str
    report_type: str
    title: str
    change_event_id: Optional[int]
    area_id: Optional[int]
    sections: List[ReportSection]
    metadata: Dict
    created_at: str
    created_by: int
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "report_id": self.report_id,
            "report_type": self.report_type,
            "title": self.title,
            "change_event_id": self.change_event_id,
            "area_id": self.area_id,
            "sections": [s.to_dict() for s in self.sections],
            "metadata": self.metadata,
            "created_at": self.created_at,
            "created_by": self.created_by
        }


class ReportGenerator:
    """Generate PDF reports for change events and investigations"""
    
    def __init__(self):
        self.reports = {}
        self.report_templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, Dict]:
        """Initialize report templates"""
        return {
            "change_detection": {
                "title": "Change Detection Report",
                "sections": [
                    "executive_summary",
                    "change_overview",
                    "methodology",
                    "results",
                    "classification",
                    "risk_assessment",
                    "recommendations",
                    "appendix"
                ]
            },
            "investigation": {
                "title": "Investigation Report",
                "sections": [
                    "executive_summary",
                    "background",
                    "evidence_summary",
                    "findings",
                    "conclusions",
                    "recommendations",
                    "appendix"
                ]
            },
            "risk_assessment": {
                "title": "Risk Assessment Report",
                "sections": [
                    "executive_summary",
                    "risk_overview",
                    "environmental_risks",
                    "social_risks",
                    "economic_risks",
                    "mitigation_strategies",
                    "appendix"
                ]
            },
            "temporal_analysis": {
                "title": "Temporal Change Analysis Report",
                "sections": [
                    "executive_summary",
                    "temporal_overview",
                    "change_trends",
                    "seasonal_patterns",
                    "predictions",
                    "recommendations",
                    "appendix"
                ]
            }
        }
    
    def generate_report(
        self,
        report_type: str,
        change_event_id: Optional[int] = None,
        area_id: Optional[int] = None,
        data: Optional[Dict] = None,
        user_id: int = 0
    ) -> Report:
        """
        Generate a report.
        
        Args:
            report_type: Type of report to generate
            change_event_id: Optional change event ID
            area_id: Optional area ID
            data: Optional data for report generation
            user_id: ID of user generating the report
        
        Returns:
            Report object
        """
        report_id = f"report_{report_type}_{datetime.utcnow().timestamp()}"
        
        # Get template
        template = self.report_templates.get(report_type)
        if not template:
            raise ValueError(f"Unknown report type: {report_type}")
        
        # Generate sections
        sections = self._generate_sections(report_type, data or {})
        
        # Create report
        report = Report(
            report_id=report_id,
            report_type=report_type,
            title=template["title"],
            change_event_id=change_event_id,
            area_id=area_id,
            sections=sections,
            metadata={
                "template": template,
                "data_provided": data is not None
            },
            created_at=datetime.utcnow().isoformat(),
            created_by=user_id
        )
        
        self.reports[report_id] = report
        return report
    
    def _generate_sections(
        self,
        report_type: str,
        data: Dict
    ) -> List[ReportSection]:
        """Generate report sections based on type"""
        sections = []
        
        if report_type == "change_detection":
            sections.extend([
                self._executive_summary_section(data),
                self._change_overview_section(data),
                self._methodology_section(data),
                self._results_section(data),
                self._classification_section(data),
                self._risk_assessment_section(data),
                self._recommendations_section(data),
                self._appendix_section(data)
            ])
        elif report_type == "investigation":
            sections.extend([
                self._executive_summary_section(data),
                self._background_section(data),
                self._evidence_summary_section(data),
                self._findings_section(data),
                self._conclusions_section(data),
                self._recommendations_section(data),
                self._appendix_section(data)
            ])
        elif report_type == "risk_assessment":
            sections.extend([
                self._executive_summary_section(data),
                self._risk_overview_section(data),
                self._environmental_risks_section(data),
                self._social_risks_section(data),
                self._economic_risks_section(data),
                self._mitigation_strategies_section(data),
                self._appendix_section(data)
            ])
        elif report_type == "temporal_analysis":
            sections.extend([
                self._executive_summary_section(data),
                self._temporal_overview_section(data),
                self._change_trends_section(data),
                self._seasonal_patterns_section(data),
                self._predictions_section(data),
                self._recommendations_section(data),
                self._appendix_section(data)
            ])
        
        # Update order
        for i, section in enumerate(sections):
            section.order = i
        
        return sections
    
    def _executive_summary_section(self, data: Dict) -> ReportSection:
        """Generate executive summary section"""
        change_area = data.get("change_area", 0)
        change_percentage = data.get("change_percentage", 0)
        risk_level = data.get("risk_level", "unknown")
        
        content = f"""
This report documents a detected change event affecting {change_area:.0f} pixels ({change_percentage:.1f}%).
The overall risk level is assessed as {risk_level.upper()}.

Key findings include:
- Change magnitude: {change_area:.0f} pixels
- Risk assessment: {risk_level}
- Classification: {data.get('activity_type', 'unknown')}
- Detection confidence: {data.get('confidence', 0):.1%}

This report provides detailed analysis of the change, including methodology, results, classification, risk assessment, and recommendations.
"""
        
        return ReportSection(
            section_id="executive_summary",
            title="Executive Summary",
            content=content.strip(),
            order=0,
            include_table=False,
            include_chart=False,
            table_data=None,
            chart_data=None
        )
    
    def _change_overview_section(self, data: Dict) -> ReportSection:
        """Generate change overview section"""
        content = f"""
Change Detection Overview:

- Detection Date: {data.get('detection_date', 'N/A')}
- Area ID: {data.get('area_id', 'N/A')}
- Change Event ID: {data.get('change_event_id', 'N/A')}
- Change Area: {data.get('change_area', 0):.0f} pixels
- Change Percentage: {data.get('change_percentage', 0):.1%}
- Detection Method: {data.get('detection_method', 'baseline')}
- Confidence: {data.get('confidence', 0):.1%}

Geographic Information:
- Location: {data.get('location', 'N/A')}
- Coordinates: {data.get('coordinates', 'N/A')}
- Elevation: {data.get('elevation', 'N/A')}m
"""
        
        return ReportSection(
            section_id="change_overview",
            title="Change Overview",
            content=content.strip(),
            order=1,
            include_table=True,
            include_chart=False,
            table_data=data.get("overview_table"),
            chart_data=None
        )
    
    def _methodology_section(self, data: Dict) -> ReportSection:
        """Generate methodology section"""
        content = """
Methodology:

This change was detected using satellite imagery analysis. The methodology includes:

1. Data Acquisition:
   - Satellite imagery from multiple sources
   - Temporal resolution: 5-30 days
   - Spatial resolution: 10-30m

2. Preprocessing:
   - Atmospheric correction
   - Geometric correction
   - Cloud masking

3. Change Detection:
   - Image differencing
   - Spectral index analysis (NDVI, NDWI)
   - Machine learning classification

4. Validation:
   - Cross-validation with ground truth
   - Confidence scoring
   - Manual verification when required
"""
        
        return ReportSection(
            section_id="methodology",
            title="Methodology",
            content=content.strip(),
            order=2,
            include_table=False,
            include_chart=False,
            table_data=None,
            chart_data=None
        )
    
    def _results_section(self, data: Dict) -> ReportSection:
        """Generate results section"""
        content = f"""
Detection Results:

- Change Mask Generated: Yes
- Bounding Geometry: {data.get('bounding_geometry', 'N/A')}
- Change Hotspots: {len(data.get('hotspots', []))} identified
- Spectral Changes:
  - NDVI Change: {data.get('ndvi_change', 0):.3f}
  - NDWI Change: {data.get('ndwi_change', 0):.3f}
  - NIR Change: {data.get('nir_change', 0):.3f}

The change was detected with {data.get('confidence', 0):.1%} confidence.
"""
        
        return ReportSection(
            section_id="results",
            title="Results",
            content=content.strip(),
            order=3,
            include_table=True,
            include_chart=True,
            table_data=data.get("results_table"),
            chart_data=data.get("results_chart")
        )
    
    def _classification_section(self, data: Dict) -> ReportSection:
        """Generate classification section"""
        is_human = data.get("is_human_induced", False)
        activity = data.get("activity_type", "unknown")
        human_conf = data.get("human_confidence", 0)
        activity_conf = data.get("activity_confidence", 0)
        
        content = f"""
Classification Results:

Human vs Natural:
- Classification: {'Human-Induced' if is_human else 'Natural'}
- Confidence: {human_conf:.1%}

Activity Type:
- Activity: {activity}
- Confidence: {activity_conf:.1%}

The classification was performed using a machine learning model trained on labeled change events.
"""
        
        return ReportSection(
            section_id="classification",
            title="Classification",
            content=content.strip(),
            order=4,
            include_table=True,
            include_chart=False,
            table_data=data.get("classification_table"),
            chart_data=None
        )
    
    def _risk_assessment_section(self, data: Dict) -> ReportSection:
        """Generate risk assessment section"""
        risk_score = data.get("risk_score", 0)
        risk_level = data.get("risk_level", "unknown")
        
        content = f"""
Risk Assessment:

Overall Risk Score: {risk_score:.2f}
Risk Level: {risk_level.upper()}

Risk Factors:
{self._format_risk_factors(data.get('risk_factors', []))}

The risk assessment considers environmental, social, economic, and regulatory factors.
"""
        
        return ReportSection(
            section_id="risk_assessment",
            title="Risk Assessment",
            content=content.strip(),
            order=5,
            include_table=True,
            include_chart=True,
            table_data=data.get("risk_table"),
            chart_data=data.get("risk_chart")
        )
    
    def _format_risk_factors(self, factors: List[str]) -> str:
        """Format risk factors for display"""
        if not factors:
            return "- No significant risk factors identified"
        
        return "\n".join([f"- {factor}" for factor in factors])
    
    def _recommendations_section(self, data: Dict) -> ReportSection:
        """Generate recommendations section"""
        recommendations = data.get("recommendations", [])
        
        content = "Recommendations:\n\n"
        if recommendations:
            content += "\n".join([f"{i+1}. {rec}" for i, rec in enumerate(recommendations)])
        else:
            content += "- No specific recommendations at this time"
        
        return ReportSection(
            section_id="recommendations",
            title="Recommendations",
            content=content.strip(),
            order=6,
            include_table=False,
            include_chart=False,
            table_data=None,
            chart_data=None
        )
    
    def _appendix_section(self, data: Dict) -> ReportSection:
        """Generate appendix section"""
        content = """
Appendix:

A. Data Sources
- Satellite imagery providers
- GIS databases
- Ground truth data

B. Methodology Details
- Detailed algorithm descriptions
- Parameter settings
- Validation procedures

C. Additional Information
- Metadata
- Processing logs
- Version information
"""
        
        return ReportSection(
            section_id="appendix",
            title="Appendix",
            content=content.strip(),
            order=7,
            include_table=False,
            include_chart=False,
            table_data=None,
            chart_data=None
        )
    
    def _background_section(self, data: Dict) -> ReportSection:
        """Generate background section for investigation reports"""
        content = f"""
Background:

This investigation was initiated following the detection of change event {data.get('change_event_id', 'N/A')}.

Investigation Scope:
- Area: {data.get('area_id', 'N/A')}
- Time Period: {data.get('time_period', 'N/A')}
- Investigation Type: {data.get('investigation_type', 'standard')}

The investigation aims to determine the cause, extent, and implications of the detected change.
"""
        
        return ReportSection(
            section_id="background",
            title="Background",
            content=content.strip(),
            order=1,
            include_table=False,
            include_chart=False,
            table_data=None,
            chart_data=None
        )
    
    def _evidence_summary_section(self, data: Dict) -> ReportSection:
        """Generate evidence summary section"""
        evidence = data.get("evidence", [])
        
        content = f"Evidence Summary:\n\n"
        content += f"Total Evidence Items: {len(evidence)}\n\n"
        
        if evidence:
            for i, ev in enumerate(evidence[:10], 1):  # Limit to 10 items
                content += f"{i}. {ev.get('type', 'unknown')} - {ev.get('description', 'N/A')}\n"
                content += f"   Source: {ev.get('source', 'N/A')}\n"
                content += f"   Confidence: {ev.get('confidence', 0):.1%}\n\n"
        
        return ReportSection(
            section_id="evidence_summary",
            title="Evidence Summary",
            content=content.strip(),
            order=2,
            include_table=True,
            include_chart=False,
            table_data=data.get("evidence_table"),
            chart_data=None
        )
    
    def _findings_section(self, data: Dict) -> ReportSection:
        """Generate findings section"""
        findings = data.get("findings", [])
        
        content = "Findings:\n\n"
        if findings:
            content += "\n".join([f"- {finding}" for finding in findings])
        else:
            content += "- Investigation ongoing"
        
        return ReportSection(
            section_id="findings",
            title="Findings",
            content=content.strip(),
            order=3,
            include_table=False,
            include_chart=False,
            table_data=None,
            chart_data=None
        )
    
    def _conclusions_section(self, data: Dict) -> ReportSection:
        """Generate conclusions section"""
        conclusions = data.get("conclusions", [])
        
        content = "Conclusions:\n\n"
        if conclusions:
            content += "\n".join([f"- {conclusion}" for conclusion in conclusions])
        else:
            content += "- Conclusions pending further investigation"
        
        return ReportSection(
            section_id="conclusions",
            title="Conclusions",
            content=content.strip(),
            order=4,
            include_table=False,
            include_chart=False,
            table_data=None,
            chart_data=None
        )
    
    def _risk_overview_section(self, data: Dict) -> ReportSection:
        """Generate risk overview section"""
        risk_score = data.get("risk_score", 0)
        risk_level = data.get("risk_level", "unknown")
        
        content = f"""
Risk Overview:

Overall Risk Score: {risk_score:.2f}
Risk Level: {risk_level.upper()}

This section provides a comprehensive assessment of risks associated with the detected change.
"""
        
        return ReportSection(
            section_id="risk_overview",
            title="Risk Overview",
            content=content.strip(),
            order=1,
            include_table=False,
            include_chart=True,
            table_data=None,
            chart_data=data.get("risk_overview_chart")
        )
    
    def _environmental_risks_section(self, data: Dict) -> ReportSection:
        """Generate environmental risks section"""
        env_risks = data.get("environmental_risks", {})
        
        content = "Environmental Risks:\n\n"
        for risk, value in env_risks.items():
            content += f"- {risk.replace('_', ' ').title()}: {value:.2f}\n"
        
        return ReportSection(
            section_id="environmental_risks",
            title="Environmental Risks",
            content=content.strip(),
            order=2,
            include_table=True,
            include_chart=True,
            table_data=data.get("env_risks_table"),
            chart_data=data.get("env_risks_chart")
        )
    
    def _social_risks_section(self, data: Dict) -> ReportSection:
        """Generate social risks section"""
        social_risks = data.get("social_risks", {})
        
        content = "Social Risks:\n\n"
        for risk, value in social_risks.items():
            content += f"- {risk.replace('_', ' ').title()}: {value:.2f}\n"
        
        return ReportSection(
            section_id="social_risks",
            title="Social Risks",
            content=content.strip(),
            order=3,
            include_table=True,
            include_chart=True,
            table_data=data.get("social_risks_table"),
            chart_data=data.get("social_risks_chart")
        )
    
    def _economic_risks_section(self, data: Dict) -> ReportSection:
        """Generate economic risks section"""
        econ_risks = data.get("economic_risks", {})
        
        content = "Economic Risks:\n\n"
        for risk, value in econ_risks.items():
            content += f"- {risk.replace('_', ' ').title()}: {value:.2f}\n"
        
        return ReportSection(
            section_id="economic_risks",
            title="Economic Risks",
            content=content.strip(),
            order=4,
            include_table=True,
            include_chart=True,
            table_data=data.get("econ_risks_table"),
            chart_data=data.get("econ_risks_chart")
        )
    
    def _mitigation_strategies_section(self, data: Dict) -> ReportSection:
        """Generate mitigation strategies section"""
        strategies = data.get("mitigation_strategies", [])
        
        content = "Mitigation Strategies:\n\n"
        if strategies:
            content += "\n".join([f"{i+1}. {strategy}" for i, strategy in enumerate(strategies)])
        else:
            content += "- No specific mitigation strategies identified"
        
        return ReportSection(
            section_id="mitigation_strategies",
            title="Mitigation Strategies",
            content=content.strip(),
            order=5,
            include_table=False,
            include_chart=False,
            table_data=None,
            chart_data=None
        )
    
    def _temporal_overview_section(self, data: Dict) -> ReportSection:
        """Generate temporal overview section"""
        content = f"""
Temporal Change Overview:

- Analysis Period: {data.get('analysis_period', 'N/A')}
- Total Change Events: {data.get('total_events', 0)}
- Change Rate: {data.get('change_rate', 0):.3f} pixels/day
- Acceleration: {data.get('acceleration', 0):.3f}
"""
        
        return ReportSection(
            section_id="temporal_overview",
            title="Temporal Overview",
            content=content.strip(),
            order=1,
            include_table=True,
            include_chart=True,
            table_data=data.get("temporal_table"),
            chart_data=data.get("temporal_chart")
        )
    
    def _change_trends_section(self, data: Dict) -> ReportSection:
        """Generate change trends section"""
        content = """
Change Trends:

Analysis of change patterns over time reveals the following trends:
- Increasing/decreasing change frequency
- Seasonal variations
- Acceleration/deceleration patterns
"""
        
        return ReportSection(
            section_id="change_trends",
            title="Change Trends",
            content=content.strip(),
            order=2,
            include_table=False,
            include_chart=True,
            table_data=None,
            chart_data=data.get("trends_chart")
        )
    
    def _seasonal_patterns_section(self, data: Dict) -> ReportSection:
        """Generate seasonal patterns section"""
        seasonal = data.get("seasonal_patterns", {})
        
        content = "Seasonal Patterns:\n\n"
        for month, value in seasonal.items():
            content += f"- Month {month}: {value:.2f}\n"
        
        return ReportSection(
            section_id="seasonal_patterns",
            title="Seasonal Patterns",
            content=content.strip(),
            order=3,
            include_table=True,
            include_chart=True,
            table_data=data.get("seasonal_table"),
            chart_data=data.get("seasonal_chart")
        )
    
    def _predictions_section(self, data: Dict) -> ReportSection:
        """Generate predictions section"""
        predicted_area = data.get("predicted_area", 0)
        confidence = data.get("prediction_confidence", 0)
        
        content = f"""
Future Predictions:

- Predicted Change Area (30 days): {predicted_area:.0f} pixels
- Prediction Confidence: {confidence:.1%}
- Trend: {data.get('trend', 'stable')}

Note: Predictions are based on historical patterns and should be validated with actual observations.
"""
        
        return ReportSection(
            section_id="predictions",
            title="Predictions",
            content=content.strip(),
            order=4,
            include_table=False,
            include_chart=True,
            table_data=None,
            chart_data=data.get("prediction_chart")
        )
    
    def get_report(self, report_id: str) -> Optional[Report]:
        """Get a report by ID"""
        return self.reports.get(report_id)
    
    def get_reports(
        self,
        report_type: Optional[str] = None,
        change_event_id: Optional[int] = None,
        area_id: Optional[int] = None,
        limit: int = 100
    ) -> List[Report]:
        """Get filtered list of reports"""
        reports = list(self.reports.values())
        
        if report_type:
            reports = [r for r in reports if r.report_type == report_type]
        if change_event_id:
            reports = [r for r in reports if r.change_event_id == change_event_id]
        if area_id:
            reports = [r for r in reports if r.area_id == area_id]
        
        # Sort by creation date (newest first)
        reports.sort(key=lambda r: r.created_at, reverse=True)
        
        return reports[:limit]
    
    def export_report(self, report: Report) -> str:
        """Export report as JSON"""
        return json.dumps(report.to_dict(), indent=2)
    
    def import_report(self, json_data: str) -> Report:
        """Import report from JSON"""
        data = json.loads(json_data)
        
        sections = [
            ReportSection(**s)
            for s in data["sections"]
        ]
        
        return Report(
            report_id=data["report_id"],
            report_type=data["report_type"],
            title=data["title"],
            change_event_id=data["change_event_id"],
            area_id=data["area_id"],
            sections=sections,
            metadata=data["metadata"],
            created_at=data["created_at"],
            created_by=data["created_by"]
        )
