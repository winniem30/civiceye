import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import json


class VerificationStatus(Enum):
    """Verification status for change events"""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"
    CORRECTED = "corrected"


class VerificationAction(Enum):
    """Actions a verifier can take"""
    CONFIRM = "confirm"
    REJECT = "reject"
    MODIFY = "modify"
    FLAG_FOR_REVIEW = "flag_for_review"


@dataclass
class VerificationRecord:
    """Record of a human verification action"""
    
    # Change event info
    change_event_id: int
    original_detection: Dict
    
    # Verification info
    status: VerificationStatus
    action: VerificationAction
    verifier_id: int
    verification_date: str
    
    # Corrections (if any)
    corrected_change_mask: Optional[List[List[int]]]
    corrected_change_area: Optional[float]
    corrected_classification: Optional[Dict]
    
    # Feedback
    feedback: str
    confidence: float
    
    # Metadata
    verification_method: str
    time_spent_seconds: Optional[float]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "change_event_id": self.change_event_id,
            "original_detection": self.original_detection,
            "status": self.status.value,
            "action": self.action.value,
            "verifier_id": self.verifier_id,
            "verification_date": self.verification_date,
            "corrected_change_mask": self.corrected_change_mask,
            "corrected_change_area": self.corrected_change_area,
            "corrected_classification": self.corrected_classification,
            "feedback": self.feedback,
            "confidence": self.confidence,
            "verification_method": self.verification_method,
            "time_spent_seconds": self.time_spent_seconds
        }


@dataclass
class VerificationQueue:
    """Queue of change events pending verification"""
    
    queue_id: str
    area_id: int
    pending_events: List[int]
    priority: str
    created_at: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "queue_id": self.queue_id,
            "area_id": self.area_id,
            "pending_events": self.pending_events,
            "priority": self.priority,
            "created_at": self.created_at
        }


class HumanVerificationSystem:
    """System for human-in-the-loop verification of change detections"""
    
    def __init__(self):
        self.verification_records = {}
        self.verification_queues = {}
        self.verifier_stats = {}
    
    def add_to_verification_queue(
        self,
        change_event_id: int,
        area_id: int,
        priority: str = "normal",
        detection_data: Optional[Dict] = None
    ) -> str:
        """
        Add a change event to the verification queue.
        
        Args:
            change_event_id: ID of the change event
            area_id: ID of the area
            priority: Priority level (low, normal, high, urgent)
            detection_data: Original detection data
        
        Returns:
            Queue ID
        """
        queue_id = f"queue_{area_id}_{datetime.utcnow().timestamp()}"
        
        if area_id not in self.verification_queues:
            self.verification_queues[area_id] = []
        
        self.verification_queues[area_id].append({
            "queue_id": queue_id,
            "change_event_id": change_event_id,
            "priority": priority,
            "detection_data": detection_data,
            "added_at": datetime.utcnow().isoformat(),
            "status": VerificationStatus.PENDING.value
        })
        
        return queue_id
    
    def get_next_verification_item(
        self,
        verifier_id: int,
        area_id: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Get the next item for a verifier to review.
        
        Args:
            verifier_id: ID of the verifier
            area_id: Optional area ID to filter by
        
        Returns:
            Next verification item or None
        """
        # Sort by priority
        priority_order = {"urgent": 0, "high": 1, "normal": 2, "low": 3}
        
        all_items = []
        for area, items in self.verification_queues.items():
            if area_id is not None and area != area_id:
                continue
            for item in items:
                if item["status"] == VerificationStatus.PENDING.value:
                    all_items.append((item, priority_order.get(item["priority"], 2)))
        
        if not all_items:
            return None
        
        # Sort by priority
        all_items.sort(key=lambda x: x[1])
        
        next_item = all_items[0][0]
        
        # Mark as in progress
        next_item["status"] = VerificationStatus.NEEDS_REVIEW.value
        next_item["assigned_to"] = verifier_id
        next_item["assigned_at"] = datetime.utcnow().isoformat()
        
        return next_item
    
    def submit_verification(
        self,
        change_event_id: int,
        verifier_id: int,
        action: str,
        feedback: str,
        confidence: float,
        corrections: Optional[Dict] = None,
        time_spent: Optional[float] = None
    ) -> VerificationRecord:
        """
        Submit a verification result.
        
        Args:
            change_event_id: ID of the change event
            verifier_id: ID of the verifier
            action: Action taken (confirm, reject, modify, flag_for_review)
            feedback: Verifier's feedback
            confidence: Verifier's confidence in their decision
            corrections: Optional corrections to the detection
            time_spent: Time spent on verification in seconds
        
        Returns:
            VerificationRecord object
        """
        # Get original detection (simplified - in production would fetch from DB)
        original_detection = {
            "change_event_id": change_event_id,
            "change_area": 1000,  # Placeholder
            "change_percentage": 5.0,
            "confidence": 0.8
        }
        
        # Determine status based on action
        action_enum = VerificationAction(action)
        if action_enum == VerificationAction.CONFIRM:
            status = VerificationStatus.VERIFIED
        elif action_enum == VerificationAction.REJECT:
            status = VerificationStatus.REJECTED
        elif action_enum == VerificationAction.MODIFY:
            status = VerificationStatus.CORRECTED
        elif action_enum == VerificationAction.FLAG_FOR_REVIEW:
            status = VerificationStatus.NEEDS_REVIEW
        else:
            status = VerificationStatus.PENDING
        
        # Extract corrections if provided
        corrected_mask = None
        corrected_area = None
        corrected_classification = None
        
        if corrections:
            corrected_mask = corrections.get("change_mask")
            corrected_area = corrections.get("change_area")
            corrected_classification = corrections.get("classification")
        
        # Create verification record
        record = VerificationRecord(
            change_event_id=change_event_id,
            original_detection=original_detection,
            status=status,
            action=action_enum,
            verifier_id=verifier_id,
            verification_date=datetime.utcnow().isoformat(),
            corrected_change_mask=corrected_mask,
            corrected_change_area=corrected_area,
            corrected_classification=corrected_classification,
            feedback=feedback,
            confidence=confidence,
            verification_method="manual",
            time_spent_seconds=time_spent
        )
        
        # Store record
        self.verification_records[change_event_id] = record
        
        # Update verifier stats
        self._update_verifier_stats(verifier_id, action, confidence, time_spent)
        
        # Update queue status
        self._update_queue_status(change_event_id, status)
        
        return record
    
    def _update_verifier_stats(
        self,
        verifier_id: int,
        action: str,
        confidence: float,
        time_spent: Optional[float]
    ):
        """Update verifier statistics"""
        if verifier_id not in self.verifier_stats:
            self.verifier_stats[verifier_id] = {
                "total_verifications": 0,
                "actions": {},
                "average_confidence": 0.0,
                "total_time_spent": 0.0,
                "average_time_spent": 0.0
            }
        
        stats = self.verifier_stats[verifier_id]
        stats["total_verifications"] += 1
        
        if action not in stats["actions"]:
            stats["actions"][action] = 0
        stats["actions"][action] += 1
        
        # Update average confidence
        old_avg = stats["average_confidence"]
        new_avg = (old_avg * (stats["total_verifications"] - 1) + confidence) / stats["total_verifications"]
        stats["average_confidence"] = new_avg
        
        # Update time stats
        if time_spent:
            stats["total_time_spent"] += time_spent
            stats["average_time_spent"] = stats["total_time_spent"] / stats["total_verifications"]
    
    def _update_queue_status(
        self,
        change_event_id: int,
        status: VerificationStatus
    ):
        """Update queue status for a change event"""
        for area_items in self.verification_queues.values():
            for item in area_items:
                if item["change_event_id"] == change_event_id:
                    item["status"] = status.value
                    item["completed_at"] = datetime.utcnow().isoformat()
                    break
    
    def get_verification_record(
        self,
        change_event_id: int
    ) -> Optional[VerificationRecord]:
        """Get verification record for a change event"""
        return self.verification_records.get(change_event_id)
    
    def get_verifier_stats(
        self,
        verifier_id: int
    ) -> Optional[Dict]:
        """Get statistics for a verifier"""
        return self.verifier_stats.get(verifier_id)
    
    def get_queue_status(
        self,
        area_id: Optional[int] = None
    ) -> Dict:
        """
        Get status of verification queues.
        
        Args:
            area_id: Optional area ID to filter by
        
        Returns:
            Dict with queue status
        """
        total_pending = 0
        total_in_review = 0
        total_completed = 0
        
        priority_counts = {"urgent": 0, "high": 0, "normal": 0, "low": 0}
        
        for area, items in self.verification_queues.items():
            if area_id is not None and area != area_id:
                continue
            
            for item in items:
                status = item["status"]
                priority = item["priority"]
                
                if status == VerificationStatus.PENDING.value:
                    total_pending += 1
                    priority_counts[priority] = priority_counts.get(priority, 0) + 1
                elif status == VerificationStatus.NEEDS_REVIEW.value:
                    total_in_review += 1
                elif status in [VerificationStatus.VERIFIED.value, VerificationStatus.REJECTED.value, VerificationStatus.CORRECTED.value]:
                    total_completed += 1
        
        return {
            "area_id": area_id,
            "total_pending": total_pending,
            "total_in_review": total_in_review,
            "total_completed": total_completed,
            "priority_breakdown": priority_counts,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def get_verification_accuracy(
        self,
        verifier_id: Optional[int] = None
    ) -> Dict:
        """
        Calculate verification accuracy metrics.
        
        Args:
            verifier_id: Optional verifier ID to filter by
        
        Returns:
            Dict with accuracy metrics
        """
        # Filter records by verifier if specified
        records = list(self.verification_records.values())
        if verifier_id is not None:
            records = [r for r in records if r.verifier_id == verifier_id]
        
        if not records:
            return {
                "total_verifications": 0,
                "accuracy": 0.0,
                "confirmation_rate": 0.0,
                "rejection_rate": 0.0,
                "modification_rate": 0.0
            }
        
        total = len(records)
        confirmed = sum(1 for r in records if r.action == VerificationAction.CONFIRM)
        rejected = sum(1 for r in records if r.action == VerificationAction.REJECT)
        modified = sum(1 for r in records if r.action == VerificationAction.MODIFY)
        
        # Calculate accuracy (simplified - in production would compare with ground truth)
        accuracy = (confirmed + modified) / total if total > 0 else 0
        
        return {
            "total_verifications": total,
            "accuracy": float(accuracy),
            "confirmation_rate": float(confirmed / total) if total > 0 else 0,
            "rejection_rate": float(rejected / total) if total > 0 else 0,
            "modification_rate": float(modified / total) if total > 0 else 0,
            "average_confidence": float(np.mean([r.confidence for r in records])),
            "average_time_spent": float(np.mean([r.time_spent_seconds or 0 for r in records]))
        }
    
    def generate_verification_report(
        self,
        area_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict:
        """
        Generate a comprehensive verification report.
        
        Args:
            area_id: Optional area ID to filter by
            start_date: Optional start date for report
            end_date: Optional end date for report
        
        Returns:
            Dict with verification report
        """
        # Filter records by criteria
        records = list(self.verification_records.values())
        
        if area_id is not None:
            # In production, would filter by area_id
            pass
        
        if start_date or end_date:
            # Filter by date range
            start = datetime.fromisoformat(start_date) if start_date else datetime.min
            end = datetime.fromisoformat(end_date) if end_date else datetime.max
            
            records = [
                r for r in records
                if start <= datetime.fromisoformat(r.verification_date) <= end
            ]
        
        # Calculate statistics
        total = len(records)
        status_counts = {}
        action_counts = {}
        
        for record in records:
            status_counts[record.status.value] = status_counts.get(record.status.value, 0) + 1
            action_counts[record.action.value] = action_counts.get(record.action.value, 0) + 1
        
        # Calculate correction impact
        corrections = [r for r in records if r.status == VerificationStatus.CORRECTED]
        avg_area_correction = 0
        if corrections:
            area_corrections = [
                abs((r.corrected_change_area or 0) - r.original_detection.get("change_area", 0))
                for r in corrections
            ]
            avg_area_correction = np.mean(area_corrections)
        
        return {
            "area_id": area_id,
            "date_range": {
                "start": start_date,
                "end": end_date
            },
            "total_verifications": total,
            "status_breakdown": status_counts,
            "action_breakdown": action_counts,
            "correction_impact": {
                "total_corrections": len(corrections),
                "average_area_correction": float(avg_area_correction)
            },
            "verifier_performance": self._get_all_verifier_performance(),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _get_all_verifier_performance(self) -> Dict:
        """Get performance metrics for all verifiers"""
        performance = {}
        
        for verifier_id, stats in self.verifier_stats.items():
            performance[verifier_id] = {
                "total_verifications": stats["total_verifications"],
                "average_confidence": stats["average_confidence"],
                "average_time_spent": stats["average_time_spent"],
                "actions_breakdown": stats["actions"]
            }
        
        return performance
    
    def export_verification_record(self, record: VerificationRecord) -> str:
        """Export verification record as JSON"""
        return json.dumps(record.to_dict(), indent=2)
    
    def import_verification_record(self, json_data: str) -> VerificationRecord:
        """Import verification record from JSON"""
        data = json.loads(json_data)
        return VerificationRecord(
            change_event_id=data["change_event_id"],
            original_detection=data["original_detection"],
            status=VerificationStatus(data["status"]),
            action=VerificationAction(data["action"]),
            verifier_id=data["verifier_id"],
            verification_date=data["verification_date"],
            corrected_change_mask=data.get("corrected_change_mask"),
            corrected_change_area=data.get("corrected_change_area"),
            corrected_classification=data.get("corrected_classification"),
            feedback=data["feedback"],
            confidence=data["confidence"],
            verification_method=data["verification_method"],
            time_spent_seconds=data.get("time_spent_seconds")
        )
