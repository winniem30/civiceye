import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import json


@dataclass
class GISContext:
    """GIS context information for a change event"""
    
    # Proximity features
    proximity_to_water: float  # Distance in meters
    proximity_to_urban: float  # Distance to urban areas
    proximity_to_roads: float  # Distance to roads
    proximity_to_forest: float  # Distance to forest
    
    # Terrain features
    elevation: float  # Elevation in meters
    slope: float  # Slope in degrees
    aspect: float  # Aspect in degrees
    
    # Land cover features
    land_cover_type: str  # Primary land cover type
    land_cover_confidence: float
    land_cover_history: List[str]  # Historical land cover
    
    # Administrative features
    country: str
    region: str
    population_density: float  # People per km²
    
    # Protected areas
    is_protected_area: bool
    protected_area_type: Optional[str]
    protected_area_name: Optional[str]
    
    # Climate features
    precipitation: float  # Annual precipitation in mm
    temperature: float  # Average temperature in Celsius
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class GISContextAnalyzer:
    """Analyze GIS context for change events"""
    
    def __init__(self):
        self.feature_cache = {}
    
    def analyze_context(
        self,
        bounds: Dict,
        change_mask: Optional[np.ndarray] = None,
        timestamp: Optional[str] = None
    ) -> GISContext:
        """
        Analyze GIS context for a given area.
        
        Args:
            bounds: Geographic bounds {min_x, max_x, min_y, max_y}
            change_mask: Optional change mask for focused analysis
            timestamp: Optional timestamp for temporal context
        
        Returns:
            GISContext object
        """
        # Calculate centroid
        centroid_x = (bounds["min_x"] + bounds["max_x"]) / 2
        centroid_y = (bounds["min_y"] + bounds["max_y"]) / 2
        
        # Proximity features
        proximity = self._calculate_proximity_features(centroid_x, centroid_y)
        
        # Terrain features
        terrain = self._calculate_terrain_features(centroid_x, centroid_y)
        
        # Land cover features
        land_cover = self._calculate_land_cover_features(centroid_x, centroid_y, timestamp)
        
        # Administrative features
        admin = self._calculate_administrative_features(centroid_x, centroid_y)
        
        # Protected areas
        protected = self._calculate_protected_area_features(centroid_x, centroid_y)
        
        # Climate features
        climate = self._calculate_climate_features(centroid_x, centroid_y)
        
        return GISContext(
            proximity_to_water=proximity["to_water"],
            proximity_to_urban=proximity["to_urban"],
            proximity_to_roads=proximity["to_roads"],
            proximity_to_forest=proximity["to_forest"],
            elevation=terrain["elevation"],
            slope=terrain["slope"],
            aspect=terrain["aspect"],
            land_cover_type=land_cover["type"],
            land_cover_confidence=land_cover["confidence"],
            land_cover_history=land_cover["history"],
            country=admin["country"],
            region=admin["region"],
            population_density=admin["population_density"],
            is_protected_area=protected["is_protected"],
            protected_area_type=protected["type"],
            protected_area_name=protected["name"],
            precipitation=climate["precipitation"],
            temperature=climate["temperature"]
        )
    
    def _calculate_proximity_features(
        self,
        lon: float,
        lat: float
    ) -> Dict:
        """
        Calculate proximity to various features.
        
        In production, this would query GIS databases like:
        - OpenStreetMap for roads and urban areas
        - HydroSHEDS for water bodies
        - Global Forest Watch for forest cover
        
        For now, return placeholder values.
        """
        # Placeholder implementation
        # In production, use actual GIS queries
        return {
            "to_water": np.random.uniform(0, 10000),  # 0-10km
            "to_urban": np.random.uniform(0, 50000),  # 0-50km
            "to_roads": np.random.uniform(0, 5000),  # 0-5km
            "to_forest": np.random.uniform(0, 20000)  # 0-20km
        }
    
    def _calculate_terrain_features(
        self,
        lon: float,
        lat: float
    ) -> Dict:
        """
        Calculate terrain features.
        
        In production, this would query DEM data from:
        - SRTM (Shuttle Radar Topography Mission)
        - ASTER GDEM
        - Copernicus DEM
        """
        # Placeholder implementation
        # In production, query actual elevation data
        elevation = np.random.uniform(0, 5000)  # 0-5000m
        slope = np.random.uniform(0, 45)  # 0-45 degrees
        aspect = np.random.uniform(0, 360)  # 0-360 degrees
        
        return {
            "elevation": elevation,
            "slope": slope,
            "aspect": aspect
        }
    
    def _calculate_land_cover_features(
        self,
        lon: float,
        lat: float,
        timestamp: Optional[str] = None
    ) -> Dict:
        """
        Calculate land cover features.
        
        In production, this would query:
        - ESA WorldCover
        - MODIS Land Cover
        - Copernicus Land Monitoring Service
        """
        # Placeholder implementation
        land_cover_types = [
            "forest", "shrubland", "grassland", "cropland",
            "urban", "bare", "water", "wetland"
        ]
        
        current_type = np.random.choice(land_cover_types)
        history = [current_type]
        
        # Simulate historical changes
        for _ in range(3):
            history.append(np.random.choice(land_cover_types))
        
        return {
            "type": current_type,
            "confidence": np.random.uniform(0.7, 1.0),
            "history": history
        }
    
    def _calculate_administrative_features(
        self,
        lon: float,
        lat: float
    ) -> Dict:
        """
        Calculate administrative features.
        
        In production, this would query:
        - Natural Earth for country boundaries
        - GADM for administrative divisions
        - WorldPop for population data
        """
        # Placeholder implementation
        countries = ["United States", "Brazil", "India", "China", "Russia"]
        regions = ["State A", "State B", "Province C", "Region D"]
        
        return {
            "country": np.random.choice(countries),
            "region": np.random.choice(regions),
            "population_density": np.random.uniform(0, 10000)  # 0-10000 people/km²
        }
    
    def _calculate_protected_area_features(
        self,
        lon: float,
        lat: float
    ) -> Dict:
        """
        Calculate protected area features.
        
        In production, this would query:
        - WDPA (World Database on Protected Areas)
        - IUCN Protected Planet
        """
        # Placeholder implementation
        is_protected = np.random.choice([True, False], p=[0.2, 0.8])
        
        if is_protected:
            protected_types = ["National Park", "Wildlife Reserve", "Nature Reserve"]
            return {
                "is_protected": True,
                "type": np.random.choice(protected_types),
                "name": f"Protected Area {np.random.randint(1, 100)}"
            }
        
        return {
            "is_protected": False,
            "type": None,
            "name": None
        }
    
    def _calculate_climate_features(
        self,
        lon: float,
        lat: float
    ) -> Dict:
        """
        Calculate climate features.
        
        In production, this would query:
        - WorldClim
        - CHELSA
        - ERA5
        """
        # Placeholder implementation
        # Adjust based on latitude
        abs_lat = abs(lat)
        precipitation = max(0, 2000 - abs_lat * 20 + np.random.uniform(-200, 200))
        temperature = 30 - abs_lat * 0.5 + np.random.uniform(-5, 5)
        
        return {
            "precipitation": max(0, precipitation),
            "temperature": temperature
        }
    
    def analyze_change_context(
        self,
        context_before: GISContext,
        context_after: GISContext
    ) -> Dict:
        """
        Analyze how context may have influenced or been affected by change.
        
        Args:
            context_before: GIS context before change
            context_after: GIS context after change
        
        Returns:
            Dict with context change analysis
        """
        # Land cover change
        land_cover_changed = context_before.land_cover_type != context_after.land_cover_type
        
        # Population density change (could indicate urbanization)
        pop_density_change = context_after.population_density - context_before.population_density
        
        # Protected area status change
        protection_changed = context_before.is_protected_area != context_after.is_protected_area
        
        return {
            "land_cover_changed": land_cover_changed,
            "land_cover_transition": {
                "from": context_before.land_cover_type,
                "to": context_after.land_cover_type
            },
            "population_density_change": float(pop_density_change),
            "protection_status_changed": protection_changed,
            "urbanization_indicator": pop_density_change > 100  # Significant increase
        }
    
    def get_risk_factors(
        self,
        context: GISContext,
        change_type: str
    ) -> Dict:
        """
        Identify risk factors based on GIS context.
        
        Args:
            context: GIS context
            change_type: Type of change (construction, deforestation, etc.)
        
        Returns:
            Dict with risk factors
        """
        risk_factors = []
        risk_score = 0.0
        
        # Protected area risk
        if context.is_protected_area:
            risk_factors.append({
                "factor": "protected_area",
                "severity": "high",
                "description": f"Change in {context.protected_area_name}"
            })
            risk_score += 0.3
        
        # High population density risk
        if context.population_density > 1000:
            risk_factors.append({
                "factor": "high_population_density",
                "severity": "medium",
                "description": f"Area has {context.population_density:.0f} people/km²"
            })
            risk_score += 0.2
        
        # Water proximity risk
        if context.proximity_to_water < 1000:
            risk_factors.append({
                "factor": "water_proximity",
                "severity": "medium",
                "description": f"Within {context.proximity_to_water:.0f}m of water body"
            })
            risk_score += 0.15
        
        # Forest proximity risk for deforestation
        if change_type == "deforestation" and context.proximity_to_forest < 5000:
            risk_factors.append({
                "factor": "forest_edge",
                "severity": "high",
                "description": "Change at forest edge"
            })
            risk_score += 0.25
        
        # Steep slope risk
        if context.slope > 30:
            risk_factors.append({
                "factor": "steep_slope",
                "severity": "medium",
                "description": f"Slope of {context.slope:.1f}° increases erosion risk"
            })
            risk_score += 0.1
        
        # Cap risk score at 1.0
        risk_score = min(1.0, risk_score)
        
        return {
            "risk_score": float(risk_score),
            "risk_level": self._get_risk_level(risk_score),
            "risk_factors": risk_factors
        }
    
    def _get_risk_level(self, score: float) -> str:
        """Convert risk score to level"""
        if score >= 0.7:
            return "critical"
        elif score >= 0.5:
            return "high"
        elif score >= 0.3:
            return "medium"
        else:
            return "low"
    
    def generate_context_report(
        self,
        context: GISContext,
        change_mask: Optional[np.ndarray] = None
    ) -> Dict:
        """Generate a comprehensive context report"""
        report = {
            "context": context.to_dict(),
            "summary": self._generate_context_summary(context),
            "recommendations": self._generate_recommendations(context)
        }
        
        if change_mask is not None:
            report["spatial_analysis"] = self._analyze_spatial_context(context, change_mask)
        
        return report
    
    def _generate_context_summary(self, context: GISContext) -> str:
        """Generate a human-readable context summary"""
        summary_parts = [
            f"Located in {context.region}, {context.country}",
            f"Primary land cover: {context.land_cover_type}",
            f"Elevation: {context.elevation:.0f}m with {context.slope:.1f}° slope"
        ]
        
        if context.is_protected_area:
            summary_parts.append(
                f"Within {context.protected_area_type}: {context.protected_area_name}"
            )
        
        summary_parts.append(
            f"Population density: {context.population_density:.0f} people/km²"
        )
        
        return ". ".join(summary_parts) + "."
    
    def _generate_recommendations(self, context: GISContext) -> List[str]:
        """Generate recommendations based on context"""
        recommendations = []
        
        if context.is_protected_area:
            recommendations.append(
                "Verify compliance with protected area regulations"
            )
        
        if context.proximity_to_water < 1000:
            recommendations.append(
                "Assess potential impact on water quality and aquatic ecosystems"
            )
        
        if context.slope > 30:
            recommendations.append(
                "Evaluate erosion risk and mitigation measures"
            )
        
        if context.population_density > 1000:
            recommendations.append(
                "Consider impact on local communities and infrastructure"
            )
        
        if context.land_cover_type == "forest":
            recommendations.append(
                "Assess biodiversity impact and habitat fragmentation"
            )
        
        return recommendations
    
    def _analyze_spatial_context(
        self,
        context: GISContext,
        change_mask: np.ndarray
    ) -> Dict:
        """Analyze spatial context of change"""
        # Calculate change area
        change_area = np.sum(change_mask)
        
        # Calculate centroid of change
        from skimage.measure import regionprops, label
        labeled = label(change_mask)
        regions = regionprops(labeled)
        
        if regions:
            largest = max(regions, key=lambda r: r.area)
            centroid = largest.centroid
        else:
            centroid = (0, 0)
        
        return {
            "change_area_pixels": int(change_area),
            "change_centroid": {"y": float(centroid[0]), "x": float(centroid[1])},
            "terrain_at_change": {
                "elevation": context.elevation,
                "slope": context.slope,
                "aspect": context.aspect
            }
        }
    
    def export_context(self, context: GISContext) -> str:
        """Export context as JSON"""
        return json.dumps(context.to_dict(), indent=2)
    
    def import_context(self, json_data: str) -> GISContext:
        """Import context from JSON"""
        data = json.loads(json_data)
        return GISContext(**data)
