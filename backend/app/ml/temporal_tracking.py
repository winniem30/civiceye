import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import json


class TemporalChangeTracker:
    """Track changes over time for a specific area"""
    
    def __init__(self):
        self.change_history = defaultdict(list)
        self.accumulated_changes = defaultdict(dict)
    
    def add_change_event(
        self,
        area_id: int,
        change_mask: np.ndarray,
        timestamp: datetime,
        metadata: Optional[Dict] = None
    ):
        """Add a change event to the tracking history"""
        event = {
            "timestamp": timestamp,
            "change_mask": change_mask,
            "change_area": np.sum(change_mask),
            "metadata": metadata or {}
        }
        self.change_history[area_id].append(event)
        
        # Sort by timestamp
        self.change_history[area_id].sort(key=lambda x: x["timestamp"])
    
    def get_change_rate(
        self,
        area_id: int,
        time_window: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict:
        """
        Calculate the rate of change over time.
        
        Args:
            area_id: ID of the area to analyze
            time_window: Optional (start, end) datetime tuple
        
        Returns:
            Dict with change rate statistics
        """
        if area_id not in self.change_history:
            return {"rate": 0.0, "total_changes": 0, "events": []}
        
        events = self.change_history[area_id]
        
        # Filter by time window if provided
        if time_window:
            start, end = time_window
            events = [e for e in events if start <= e["timestamp"] <= end]
        
        if len(events) < 2:
            return {"rate": 0.0, "total_changes": 0, "events": events}
        
        # Calculate change rate (change area per unit time)
        total_change = sum(e["change_area"] for e in events)
        time_span = (events[-1]["timestamp"] - events[0]["timestamp"]).total_seconds()
        
        if time_span > 0:
            rate = total_change / time_span  # pixels per second
        else:
            rate = 0.0
        
        return {
            "rate": rate,
            "total_changes": total_change,
            "time_span_seconds": time_span,
            "num_events": len(events),
            "events": events
        }
    
    def detect_acceleration(
        self,
        area_id: int,
        window_size: int = 3
    ) -> Dict:
        """
        Detect if change is accelerating or decelerating.
        
        Args:
            area_id: ID of the area to analyze
            window_size: Number of recent events to consider
        
        Returns:
            Dict with acceleration analysis
        """
        if area_id not in self.change_history:
            return {"acceleration": 0.0, "trend": "stable"}
        
        events = self.change_history[area_id]
        recent_events = events[-window_size:] if len(events) >= window_size else events
        
        if len(recent_events) < 2:
            return {"acceleration": 0.0, "trend": "insufficient_data"}
        
        # Calculate change areas
        change_areas = [e["change_area"] for e in recent_events]
        
        # Calculate acceleration (second derivative)
        if len(change_areas) >= 3:
            # Simple finite difference approximation
            first_diff = np.diff(change_areas)
            acceleration = np.mean(np.diff(first_diff))
        else:
            # Linear trend
            acceleration = change_areas[-1] - change_areas[0]
        
        # Determine trend
        if acceleration > 0.1:
            trend = "accelerating"
        elif acceleration < -0.1:
            trend = "decelerating"
        else:
            trend = "stable"
        
        return {
            "acceleration": float(acceleration),
            "trend": trend,
            "recent_changes": change_areas
        }
    
    def accumulate_changes(
        self,
        area_id: int,
        max_history: int = 100
    ) -> np.ndarray:
        """
        Accumulate all changes over time for an area.
        
        Args:
            area_id: ID of the area
            max_history: Maximum number of events to accumulate
        
        Returns:
            Cumulative change mask
        """
        if area_id not in self.change_history:
            return np.zeros((256, 256), dtype=np.uint8)
        
        events = self.change_history[area_id][-max_history:]
        
        if not events:
            return np.zeros((256, 256), dtype=np.uint8)
        
        # Get the shape from the first event
        shape = events[0]["change_mask"].shape
        cumulative = np.zeros(shape, dtype=np.uint8)
        
        for event in events:
            # Resize if necessary
            mask = event["change_mask"]
            if mask.shape != shape:
                from skimage.transform import resize
                mask = (resize(mask, shape, preserve_range=True) > 0.5).astype(np.uint8)
            
            # Logical OR to accumulate changes
            cumulative = np.logical_or(cumulative, mask).astype(np.uint8)
        
        return cumulative
    
    def get_change_hotspots(
        self,
        area_id: int,
        threshold: float = 0.7,
        grid_size: int = 8
    ) -> List[Dict]:
        """
        Identify hotspots of repeated changes.
        
        Args:
            area_id: ID of the area
            threshold: Threshold for hotspot detection
            grid_size: Size of grid cells for analysis
        
        Returns:
            List of hotspot coordinates and intensities
        """
        cumulative = self.accumulate_changes(area_id)
        
        if cumulative.shape[0] < grid_size or cumulative.shape[1] < grid_size:
            return []
        
        # Divide into grid cells
        h, w = cumulative.shape
        cell_h, cell_w = h // grid_size, w // grid_size
        
        hotspots = []
        
        for i in range(grid_size):
            for j in range(grid_size):
                # Extract cell
                cell = cumulative[
                    i * cell_h:(i + 1) * cell_h,
                    j * cell_w:(j + 1) * cell_w
                ]
                
                # Calculate change density
                density = np.sum(cell) / cell.size
                
                if density > threshold:
                    hotspots.append({
                        "grid_row": i,
                        "grid_col": j,
                        "density": float(density),
                        "center": {
                            "x": j * cell_w + cell_w // 2,
                            "y": i * cell_h + cell_h // 2
                        }
                    })
        
        # Sort by density
        hotspots.sort(key=lambda x: x["density"], reverse=True)
        
        return hotspots
    
    def predict_future_changes(
        self,
        area_id: int,
        days_ahead: int = 30
    ) -> Dict:
        """
        Predict future changes based on historical patterns.
        
        Args:
            area_id: ID of the area
            days_ahead: Number of days to predict ahead
        
        Returns:
            Dict with prediction results
        """
        if area_id not in self.change_history:
            return {"predicted_area": 0.0, "confidence": 0.0}
        
        events = self.change_history[area_id]
        
        if len(events) < 3:
            return {"predicted_area": 0.0, "confidence": 0.0}
        
        # Extract change areas and timestamps
        change_areas = [e["change_area"] for e in events]
        timestamps = [e["timestamp"] for e in events]
        
        # Calculate time differences in days
        time_diffs = [
            (timestamps[i] - timestamps[i-1]).total_seconds() / 86400
            for i in range(1, len(timestamps))
        ]
        
        # Average change rate per day
        avg_change_per_day = np.mean([
            change_areas[i] / time_diffs[i-1]
            for i in range(1, len(change_areas))
        ])
        
        # Predict future change
        predicted_area = avg_change_per_day * days_ahead
        
        # Calculate confidence based on variance
        if len(change_areas) >= 3:
            variance =np.var(change_areas)
            confidence = max(0.0, min(1.0, 1.0 - variance / (np.mean(change_areas) + 1e-6)))
        else:
            confidence = 0.5
        
        return {
            "predicted_area": float(predicted_area),
            "confidence": float(confidence),
            "days_ahead": days_ahead,
            "avg_change_per_day": float(avg_change_per_day)
        }
    
    def get_seasonal_pattern(
        self,
        area_id: int,
        num_bins: int = 12
    ) -> Dict:
        """
        Analyze seasonal patterns in changes.
        
        Args:
            area_id: ID of the area
            num_bins: Number of time bins (e.g., 12 for months)
        
        Returns:
            Dict with seasonal analysis
        """
        if area_id not in self.change_history:
            return {"pattern": [], "peak_season": None}
        
        events = self.change_history[area_id]
        
        if len(events) < num_bins:
            return {"pattern": [], "peak_season": None}
        
        # Bin events by time of year
        bins = [[] for _ in range(num_bins)]
        
        for event in events:
            # Get day of year (0-365)
            day_of_year = event["timestamp"].timetuple().tm_yday
            bin_idx = int((day_of_year / 365) * num_bins) % num_bins
            bins[bin_idx].append(event["change_area"])
        
        # Calculate average change per bin
        pattern = [
            np.mean(bin_changes) if bin_changes else 0.0
            for bin_changes in bins
        ]
        
        # Find peak season
        peak_idx = np.argmax(pattern)
        peak_season = {
            "bin": peak_idx,
            "avg_change": float(pattern[peak_idx])
        }
        
        return {
            "pattern": [float(p) for p in pattern],
            "peak_season": peak_season,
            "num_bins": num_bins
        }
    
    def generate_temporal_report(
        self,
        area_id: int
    ) -> Dict:
        """Generate a comprehensive temporal analysis report"""
        change_rate = self.get_change_rate(area_id)
        acceleration = self.detect_acceleration(area_id)
        hotspots = self.get_change_hotspots(area_id)
        prediction = self.predict_future_changes(area_id)
        seasonal = self.get_seasonal_pattern(area_id)
        
        return {
            "area_id": area_id,
            "change_rate": change_rate,
            "acceleration": acceleration,
            "hotspots": hotspots,
            "prediction": prediction,
            "seasonal_pattern": seasonal,
            "total_events": len(self.change_history.get(area_id, [])),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def export_history(self, area_id: int) -> str:
        """Export change history as JSON"""
        if area_id not in self.change_history:
            return json.dumps({"area_id": area_id, "events": []})
        
        events = []
        for event in self.change_history[area_id]:
            events.append({
                "timestamp": event["timestamp"].isoformat(),
                "change_area": float(event["change_area"]),
                "metadata": event["metadata"]
            })
        
        return json.dumps({"area_id": area_id, "events": events})
