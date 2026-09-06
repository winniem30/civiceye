import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json


class SimulationScenario(Enum):
    """Types of simulation scenarios"""
    DEFORESTATION = "deforestation"
    URBAN_EXPANSION = "urban_expansion"
    AGRICULTURAL_EXPANSION = "agricultural_expansion"
    MINING = "mining"
    WATER_LEVEL_CHANGE = "water_level_change"
    CLIMATE_CHANGE = "climate_change"


@dataclass
class SimulationParameter:
    """Parameter for simulation"""
    name: str
    value: float
    unit: str
    description: str
    min_value: float
    max_value: float


@dataclass
class SimulationResult:
    """Result of a What-If simulation"""
    
    # Scenario info
    scenario: str
    parameters: List[SimulationParameter]
    
    # Predicted outcomes
    predicted_change_area: float
    environmental_impact: Dict
    social_impact: Dict
    economic_impact: Dict
    
    # Risk assessment
    risk_level: str
    risk_factors: List[str]
    
    # Recommendations
    mitigation_strategies: List[str]
    
    # Visualization data
    impact_map: Optional[List[List[float]]]
    
    # Metadata
    simulation_id: str
    generated_at: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "scenario": self.scenario,
            "parameters": [
                {
                    "name": p.name,
                    "value": p.value,
                    "unit": p.unit,
                    "description": p.description,
                    "min_value": p.min_value,
                    "max_value": p.max_value
                }
                for p in self.parameters
            ],
            "predicted_change_area": self.predicted_change_area,
            "environmental_impact": self.environmental_impact,
            "social_impact": self.social_impact,
            "economic_impact": self.economic_impact,
            "risk_level": self.risk_level,
            "risk_factors": self.risk_factors,
            "mitigation_strategies": self.mitigation_strategies,
            "impact_map": self.impact_map,
            "simulation_id": self.simulation_id,
            "generated_at": self.generated_at
        }


class WhatIfSimulator:
    """Simulate What-If scenarios for change prediction"""
    
    def __init__(self):
        self.scenario_templates = self._initialize_scenario_templates()
    
    def _initialize_scenario_templates(self) -> Dict[str, Dict]:
        """Initialize predefined scenario templates"""
        return {
            SimulationScenario.DEFORESTATION.value: {
                "parameters": [
                    SimulationParameter(
                        name="clearing_area",
                        value=1000,
                        unit="hectares",
                        description="Area to be cleared",
                        min_value=10,
                        max_value=10000
                    ),
                    SimulationParameter(
                        name="clearing_rate",
                        value=0.5,
                        unit="hectares/day",
                        description="Rate of clearing",
                        min_value=0.1,
                        max_value=10
                    ),
                    SimulationParameter(
                        name="forest_density",
                        value=0.8,
                        unit="fraction",
                        description="Current forest density",
                        min_value=0,
                        max_value=1
                    )
                ]
            },
            SimulationScenario.URBAN_EXPANSION.value: {
                "parameters": [
                    SimulationParameter(
                        name="expansion_area",
                        value=500,
                        unit="hectares",
                        description="Area for urban expansion",
                        min_value=10,
                        max_value=5000
                    ),
                    SimulationParameter(
                        name="population_growth",
                        value=0.05,
                        unit="fraction/year",
                        description="Population growth rate",
                        min_value=0,
                        max_value=0.2
                    ),
                    SimulationParameter(
                        name="building_density",
                        value=0.6,
                        unit="fraction",
                        description="Target building density",
                        min_value=0.1,
                        max_value=1
                    )
                ]
            },
            SimulationScenario.AGRICULTURAL_EXPANSION.value: {
                "parameters": [
                    SimulationParameter(
                        name="expansion_area",
                        value=2000,
                        unit="hectares",
                        description="Area for agricultural expansion",
                        min_value=50,
                        max_value=20000
                    ),
                    SimulationParameter(
                        name="crop_type",
                        value=1,
                        unit="type_index",
                        description="Type of crop (1-5)",
                        min_value=1,
                        max_value=5
                    ),
                    SimulationParameter(
                        name="irrigation_required",
                        value=0.7,
                        unit="fraction",
                        description="Irrigation requirement",
                        min_value=0,
                        max_value=1
                    )
                ]
            },
            SimulationScenario.MINING.value: {
                "parameters": [
                    SimulationParameter(
                        name="mining_area",
                        value=100,
                        unit="hectares",
                        description="Area for mining operations",
                        min_value=5,
                        max_value=1000
                    ),
                    SimulationParameter(
                        name="extraction_rate",
                        value=1.0,
                        unit="tons/day",
                        description="Rate of resource extraction",
                        min_value=0.1,
                        max_value=100
                    ),
                    SimulationParameter(
                        name="depth",
                        value=50,
                        unit="meters",
                        description="Mining depth",
                        min_value=10,
                        max_value=500
                    )
                ]
            },
            SimulationScenario.WATER_LEVEL_CHANGE.value: {
                "parameters": [
                    SimulationParameter(
                        name="water_level_change",
                        value=2.0,
                        unit="meters",
                        description="Change in water level",
                        min_value=-10,
                        max_value=10
                    ),
                    SimulationParameter(
                        name="affected_area",
                        value=500,
                        unit="hectares",
                        description="Area affected by water level change",
                        min_value=10,
                        max_value=5000
                    )
                ]
            },
            SimulationScenario.CLIMATE_CHANGE.value: {
                "parameters": [
                    SimulationParameter(
                        name="temperature_change",
                        value=2.0,
                        unit="degrees_celsius",
                        description="Temperature increase",
                        min_value=0,
                        max_value=5
                    ),
                    SimulationParameter(
                        name="precipitation_change",
                        value=-0.1,
                        unit="fraction",
                        description="Change in precipitation",
                        min_value=-0.5,
                        max_value=0.5
                    )
                ]
            }
        }
    
    def run_simulation(
        self,
        scenario: str,
        parameters: Optional[List[Dict]] = None,
        context: Optional[Dict] = None
    ) -> SimulationResult:
        """
        Run a What-If simulation.
        
        Args:
            scenario: Type of scenario to simulate
            parameters: Optional custom parameters
            context: Optional context information (GIS, etc.)
        
        Returns:
            SimulationResult object
        """
        # Get scenario template
        template = self.scenario_templates.get(scenario)
        
        if not template:
            raise ValueError(f"Unknown scenario: {scenario}")
        
        # Use custom parameters or template defaults
        if parameters:
            sim_parameters = [
                SimulationParameter(
                    name=p["name"],
                    value=p.get("value", 0),
                    unit=p.get("unit", ""),
                    description=p.get("description", ""),
                    min_value=p.get("min_value", 0),
                    max_value=p.get("max_value", 100)
                )
                for p in parameters
            ]
        else:
            sim_parameters = template["parameters"]
        
        # Calculate predicted change area
        predicted_area = self._calculate_predicted_area(scenario, sim_parameters)
        
        # Calculate impacts
        env_impact = self._calculate_environmental_impact(scenario, sim_parameters, context)
        social_impact = self._calculate_social_impact(scenario, sim_parameters, context)
        economic_impact = self._calculate_economic_impact(scenario, sim_parameters, context)
        
        # Assess risk
        risk_assessment = self._assess_simulation_risk(
            scenario,
            sim_parameters,
            env_impact,
            social_impact,
            economic_impact
        )
        
        # Generate mitigation strategies
        mitigation = self._generate_mitigation_strategies(scenario, risk_assessment)
        
        # Generate impact map (simplified)
        impact_map = self._generate_impact_map(predicted_area)
        
        return SimulationResult(
            scenario=scenario,
            parameters=sim_parameters,
            predicted_change_area=predicted_area,
            environmental_impact=env_impact,
            social_impact=social_impact,
            economic_impact=economic_impact,
            risk_level=risk_assessment["level"],
            risk_factors=risk_assessment["factors"],
            mitigation_strategies=mitigation,
            impact_map=impact_map,
            simulation_id=self._generate_simulation_id(),
            generated_at=self._get_timestamp()
        )
    
    def _calculate_predicted_area(
        self,
        scenario: str,
        parameters: List[SimulationParameter]
    ) -> float:
        """Calculate predicted change area based on parameters"""
        param_dict = {p.name: p.value for p in parameters}
        
        if scenario == SimulationScenario.DEFORESTATION.value:
            return param_dict.get("clearing_area", 1000) * 100  # Convert to pixels (approx)
        elif scenario == SimulationScenario.URBAN_EXPANSION.value:
            return param_dict.get("expansion_area", 500) * 100
        elif scenario == SimulationScenario.AGRICULTURAL_EXPANSION.value:
            return param_dict.get("expansion_area", 2000) * 100
        elif scenario == SimulationScenario.MINING.value:
            return param_dict.get("mining_area", 100) * 100
        elif scenario == SimulationScenario.WATER_LEVEL_CHANGE.value:
            return param_dict.get("affected_area", 500) * 100
        elif scenario == SimulationScenario.CLIMATE_CHANGE.value:
            # Climate change affects larger areas proportionally
            temp_change = param_dict.get("temperature_change", 2)
            return temp_change * 10000  # Approximate
        else:
            return 1000
    
    def _calculate_environmental_impact(
        self,
        scenario: str,
        parameters: List[SimulationParameter],
        context: Optional[Dict]
    ) -> Dict:
        """Calculate environmental impact"""
        param_dict = {p.name: p.value for p in parameters}
        
        impact = {
            "biodiversity_loss": 0.0,
            "carbon_emission": 0.0,
            "water_quality_impact": 0.0,
            "soil_erosion": 0.0,
            "habitat_fragmentation": 0.0
        }
        
        if scenario == SimulationScenario.DEFORESTATION.value:
            area = param_dict.get("clearing_area", 1000)
            density = param_dict.get("forest_density", 0.8)
            impact["biodiversity_loss"] = area * density * 0.5
            impact["carbon_emission"] = area * 200  # tons CO2
            impact["soil_erosion"] = area * 0.3
            impact["habitat_fragmentation"] = area * 0.7
        
        elif scenario == SimulationScenario.URBAN_EXPANSION.value:
            area = param_dict.get("expansion_area", 500)
            impact["biodiversity_loss"] = area * 0.3
            impact["carbon_emission"] = area * 50
            impact["water_quality_impact"] = area * 0.4
        
        elif scenario == SimulationScenario.MINING.value:
            area = param_dict.get("mining_area", 100)
            depth = param_dict.get("depth", 50)
            impact["biodiversity_loss"] = area * 0.6
            impact["water_quality_impact"] = area * depth * 0.01
            impact["soil_erosion"] = area * 0.8
        
        elif scenario == SimulationScenario.WATER_LEVEL_CHANGE.value:
            level_change = param_dict.get("water_level_change", 2)
            impact["biodiversity_loss"] = abs(level_change) * 50
            impact["habitat_fragmentation"] = abs(level_change) * 30
        
        elif scenario == SimulationScenario.CLIMATE_CHANGE.value:
            temp_change = param_dict.get("temperature_change", 2)
            precip_change = param_dict.get("precipitation_change", -0.1)
            impact["biodiversity_loss"] = temp_change * 100
            impact["habitat_fragmentation"] = abs(precip_change) * 50
        
        # Normalize impacts to 0-1 scale
        for key in impact:
            impact[key] = min(1.0, impact[key] / 1000)
        
        return impact
    
    def _calculate_social_impact(
        self,
        scenario: str,
        parameters: List[SimulationParameter],
        context: Optional[Dict]
    ) -> Dict:
        """Calculate social impact"""
        param_dict = {p.name: p.value for p in parameters}
        
        impact = {
            "population_displacement": 0.0,
            "livelihood_impact": 0.0,
            "cultural_heritage_impact": 0.0,
            "health_impact": 0.0,
            "community_disruption": 0.0
        }
        
        if scenario == SimulationScenario.DEFORESTATION.value:
            area = param_dict.get("clearing_area", 1000)
            impact["livelihood_impact"] = area * 0.3
            impact["community_disruption"] = area * 0.2
        
        elif scenario == SimulationScenario.URBAN_EXPANSION.value:
            area = param_dict.get("expansion_area", 500)
            growth = param_dict.get("population_growth", 0.05)
            impact["population_displacement"] = area * 0.4
            impact["community_disruption"] = area * growth * 5
        
        elif scenario == SimulationScenario.MINING.value:
            area = param_dict.get("mining_area", 100)
            impact["population_displacement"] = area * 0.5
            impact["health_impact"] = area * 0.6
            impact["community_disruption"] = area * 0.7
        
        elif scenario == SimulationScenario.WATER_LEVEL_CHANGE.value:
            level_change = param_dict.get("water_level_change", 2)
            impact["livelihood_impact"] = abs(level_change) * 0.5
            impact["population_displacement"] = abs(level_change) * 0.3
        
        # Normalize impacts
        for key in impact:
            impact[key] = min(1.0, impact[key] / 500)
        
        return impact
    
    def _calculate_economic_impact(
        self,
        scenario: str,
        parameters: List[SimulationParameter],
        context: Optional[Dict]
    ) -> Dict:
        """Calculate economic impact"""
        param_dict = {p.name: p.value for p in parameters}
        
        impact = {
            "economic_benefit": 0.0,
            "economic_cost": 0.0,
            "job_creation": 0.0,
            "infrastructure_cost": 0.0,
            "long_term_sustainability": 0.0
        }
        
        if scenario == SimulationScenario.DEFORESTATION.value:
            area = param_dict.get("clearing_area", 1000)
            impact["economic_benefit"] = area * 100  # timber value
            impact["economic_cost"] = area * 50  # ecosystem services loss
            impact["long_term_sustainability"] = -0.7
        
        elif scenario == SimulationScenario.URBAN_EXPANSION.value:
            area = param_dict.get("expansion_area", 500)
            impact["economic_benefit"] = area * 500  # property value
            impact["infrastructure_cost"] = area * 200
            impact["job_creation"] = area * 0.5
            impact["long_term_sustainability"] = 0.3
        
        elif scenario == SimulationScenario.AGRICULTURAL_EXPANSION.value:
            area = param_dict.get("expansion_area", 2000)
            impact["economic_benefit"] = area * 150  # crop value
            impact["job_creation"] = area * 0.3
            impact["long_term_sustainability"] = 0.5
        
        elif scenario == SimulationScenario.MINING.value:
            area = param_dict.get("mining_area", 100)
            rate = param_dict.get("extraction_rate", 1.0)
            impact["economic_benefit"] = area * rate * 1000
            impact["economic_cost"] = area * 500
            impact["job_creation"] = area * 2
            impact["long_term_sustainability"] = -0.5
        
        # Normalize impacts
        for key in impact:
            if key == "long_term_sustainability":
                impact[key] = max(-1.0, min(1.0, impact[key]))
            else:
                impact[key] = min(1.0, impact[key] / 10000)
        
        return impact
    
    def _assess_simulation_risk(
        self,
        scenario: str,
        parameters: List[SimulationParameter],
        env_impact: Dict,
        social_impact: Dict,
        economic_impact: Dict
    ) -> Dict:
        """Assess overall risk of simulation"""
        # Calculate weighted risk score
        env_score = np.mean(list(env_impact.values()))
        social_score = np.mean(list(social_impact.values()))
        economic_cost = economic_impact.get("economic_cost", 0)
        sustainability = abs(economic_impact.get("long_term_sustainability", 0))
        
        overall_risk = (env_score * 0.4 + social_score * 0.3 + economic_cost * 0.2 + sustainability * 0.1)
        
        # Determine risk level
        if overall_risk > 0.7:
            level = "critical"
        elif overall_risk > 0.5:
            level = "high"
        elif overall_risk > 0.3:
            level = "medium"
        else:
            level = "low"
        
        # Identify risk factors
        factors = []
        if env_score > 0.5:
            factors.append("High environmental impact")
        if social_score > 0.5:
            factors.append("Significant social disruption")
        if economic_cost > 0.5:
            factors.append("High economic costs")
        if sustainability > 0.5:
            factors.append("Low long-term sustainability")
        
        return {
            "level": level,
            "score": float(overall_risk),
            "factors": factors
        }
    
    def _generate_mitigation_strategies(
        self,
        scenario: str,
        risk_assessment: Dict
    ) -> List[str]:
        """Generate mitigation strategies based on scenario and risk"""
        strategies = []
        
        if scenario == SimulationScenario.DEFORESTATION.value:
            strategies.extend([
                "Implement selective logging instead of clear-cutting",
                "Establish reforestation programs",
                "Create buffer zones around sensitive areas"
            ])
        elif scenario == SimulationScenario.URBAN_EXPANSION.value:
            strategies.extend([
                "Implement green building standards",
                "Preserve green spaces within development",
                "Improve public transportation to reduce sprawl"
            ])
        elif scenario == SimulationScenario.MINING.value:
            strategies.extend([
                "Implement strict environmental monitoring",
                "Plan for site rehabilitation",
                "Use less invasive extraction methods"
            ])
        elif scenario == SimulationScenario.WATER_LEVEL_CHANGE.value:
            strategies.extend([
                "Implement adaptive management plans",
                "Protect critical habitats",
                "Develop water conservation measures"
            ])
        
        # Add risk-specific strategies
        if risk_assessment["level"] in ["high", "critical"]:
            strategies.extend([
                "Conduct comprehensive environmental impact assessment",
                "Engage with local communities",
                "Establish monitoring and early warning systems"
            ])
        
        return strategies
    
    def _generate_impact_map(self, area: float) -> List[List[float]]:
        """Generate simplified impact map"""
        # Create a 50x50 grid representing impact intensity
        size = 50
        impact_map = np.zeros((size, size))
        
        # Create a circular impact pattern
        center = size // 2
        radius = int(min(size // 2, np.sqrt(area / 100)))
        
        for i in range(size):
            for j in range(size):
                distance = np.sqrt((i - center)**2 + (j - center)**2)
                if distance <= radius:
                    impact_map[i][j] = 1.0 - (distance / radius)
        
        return impact_map.tolist()
    
    def _generate_simulation_id(self) -> str:
        """Generate unique simulation ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    def compare_simulations(
        self,
        simulation1: SimulationResult,
        simulation2: SimulationResult
    ) -> Dict:
        """Compare two simulation results"""
        return {
            "scenario_comparison": (simulation1.scenario, simulation2.scenario),
            "area_difference": simulation2.predicted_change_area - simulation1.predicted_change_area,
            "environmental_difference": self._compare_impacts(
                simulation1.environmental_impact,
                simulation2.environmental_impact
            ),
            "social_difference": self._compare_impacts(
                simulation1.social_impact,
                simulation2.social_impact
            ),
            "economic_difference": self._compare_impacts(
                simulation1.economic_impact,
                simulation2.economic_impact
            ),
            "risk_level_change": (simulation1.risk_level, simulation2.risk_level)
        }
    
    def _compare_impacts(self, impact1: Dict, impact2: Dict) -> Dict:
        """Compare two impact dictionaries"""
        return {
            key: impact2.get(key, 0) - impact1.get(key, 0)
            for key in set(impact1.keys()) | set(impact2.keys())
        }
    
    def get_available_scenarios(self) -> List[Dict]:
        """Get list of available simulation scenarios"""
        return [
            {
                "name": scenario,
                "description": self._get_scenario_description(scenario),
                "parameters": [
                    {
                        "name": p.name,
                        "description": p.description,
                        "min_value": p.min_value,
                        "max_value": p.max_value,
                        "unit": p.unit
                    }
                    for p in template["parameters"]
                ]
            }
            for scenario, template in self.scenario_templates.items()
        ]
    
    def _get_scenario_description(self, scenario: str) -> str:
        """Get description for a scenario"""
        descriptions = {
            SimulationScenario.DEFORESTATION.value: "Simulate forest clearing and its impacts",
            SimulationScenario.URBAN_EXPANSION.value: "Simulate urban development and expansion",
            SimulationScenario.AGRICULTURAL_EXPANSION.value: "Simulate agricultural land expansion",
            SimulationScenario.MINING.value: "Simulate mining operations and impacts",
            SimulationScenario.WATER_LEVEL_CHANGE.value: "Simulate changes in water levels",
            SimulationScenario.CLIMATE_CHANGE.value: "Simulate climate change impacts"
        }
        return descriptions.get(scenario, "Unknown scenario")
    
    def export_simulation(self, simulation: SimulationResult) -> str:
        """Export simulation as JSON"""
        return json.dumps(simulation.to_dict(), indent=2)
    
    def import_simulation(self, json_data: str) -> SimulationResult:
        """Import simulation from JSON"""
        data = json.loads(json_data)
        
        parameters = [
            SimulationParameter(
                **p
            )
            for p in data["parameters"]
        ]
        
        return SimulationResult(
            scenario=data["scenario"],
            parameters=parameters,
            predicted_change_area=data["predicted_change_area"],
            environmental_impact=data["environmental_impact"],
            social_impact=data["social_impact"],
            economic_impact=data["economic_impact"],
            risk_level=data["risk_level"],
            risk_factors=data["risk_factors"],
            mitigation_strategies=data["mitigation_strategies"],
            impact_map=data.get("impact_map"),
            simulation_id=data["simulation_id"],
            generated_at=data["generated_at"]
        )
