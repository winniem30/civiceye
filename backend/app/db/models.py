from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.db.database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="citizen")  # admin, analyst, citizen
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    verifications = relationship("Verification", back_populates="user")
    investigations = relationship("Investigation", back_populates="user")


class Area(Base):
    __tablename__ = "areas"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    geometry = Column(Geometry('POLYGON'))
    bounds = Column(JSON)  # {min_x, min_y, max_x, max_y}
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    change_events = relationship("ChangeEvent", back_populates="area")


class SatelliteImage(Base):
    __tablename__ = "satellite_images"
    
    id = Column(Integer, primary_key=True, index=True)
    satellite_name = Column(String, index=True)  # sentinel-2, landsat-8, etc.
    acquisition_date = Column(DateTime, index=True)
    cloud_cover = Column(Float)
    geometry = Column(Geometry('POLYGON'))
    bounds = Column(JSON)
    file_path = Column(String)
    preview_path = Column(String)
    metadata = Column(JSON)
    bands = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    change_events_t1 = relationship("ChangeEvent", foreign_keys="ChangeEvent.image_t1_id", back_populates="image_t1")
    change_events_t2 = relationship("ChangeEvent", foreign_keys="ChangeEvent.image_t2_id", back_populates="image_t2")


class ChangeEvent(Base):
    __tablename__ = "change_events"
    
    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id"))
    image_t1_id = Column(Integer, ForeignKey("satellite_images.id"))
    image_t2_id = Column(Integer, ForeignKey("satellite_images.id"))
    
    # Change detection results
    change_area = Column(Float)  # in square meters
    change_percentage = Column(Float)
    confidence = Column(Float)
    change_mask_path = Column(String)
    bounding_geometry = Column(Geometry('POLYGON'))
    
    # Classification
    is_human_induced = Column(Boolean)
    human_confidence = Column(Float)
    activity_type = Column(String)  # building, road, construction, etc.
    activity_confidence = Column(Float)
    
    # Temporal
    first_detected = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    area = relationship("Area", back_populates="change_events")
    image_t1 = relationship("SatelliteImage", foreign_keys=[image_t1_id], back_populates="change_events_t1")
    image_t2 = relationship("SatelliteImage", foreign_keys=[image_t2_id], back_populates="change_events_t2")
    change_dna = relationship("ChangeDNA", back_populates="change_event", uselist=False)
    risk_assessment = relationship("RiskAssessment", back_populates="change_event", uselist=False)
    alert = relationship("Alert", back_populates="change_event", uselist=False)
    verifications = relationship("Verification", back_populates="change_event")


class ChangeDNA(Base):
    __tablename__ = "change_dna"
    
    id = Column(Integer, primary_key=True, index=True)
    change_event_id = Column(Integer, ForeignKey("change_events.id"), unique=True)
    
    # DNA components
    human_activity_probability = Column(Float)
    growth_rate = Column(String)  # low, medium, high
    persistence = Column(String)
    frequency = Column(String)
    environmental_proximity = Column(String)
    historical_activity = Column(String)
    
    # Normalized DNA vector
    dna_vector = Column(JSON)
    
    # Relationships
    change_event = relationship("ChangeEvent", back_populates="change_dna")


class GISFeature(Base):
    __tablename__ = "gis_features"
    
    id = Column(Integer, primary_key=True, index=True)
    feature_type = Column(String, index=True)  # water, road, residential, forest, etc.
    name = Column(String)
    geometry = Column(Geometry('GEOMETRY'))
    properties = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    change_event_id = Column(Integer, ForeignKey("change_events.id"), unique=True)
    
    risk_score = Column(Float)  # 0-100
    risk_level = Column(String)  # LOW, MEDIUM, HIGH, CRITICAL
    
    # Risk factors
    change_type_risk = Column(Float)
    area_risk = Column(Float)
    velocity_risk = Column(Float)
    environmental_risk = Column(Float)
    vegetation_loss_risk = Column(Float)
    water_proximity_risk = Column(Float)
    flood_risk = Column(Float)
    historical_risk = Column(Float)
    
    # Explainability
    shap_values = Column(JSON)
    explanation = Column(Text)
    
    # Model info
    model_type = Column(String)  # rule_based, xgboost, etc.
    model_version = Column(String)
    
    # Relationships
    change_event = relationship("ChangeEvent", back_populates="risk_assessment")


class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    change_event_id = Column(Integer, ForeignKey("change_events.id"))
    
    prediction_type = Column(String)  # future_change, what_if
    target_date = Column(DateTime)
    predicted_area = Column(Float)
    predicted_risk_score = Column(Float)
    confidence = Column(Float)
    prediction_data = Column(JSON)
    
    model_type = Column(String)
    model_version = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    change_event_id = Column(Integer, ForeignKey("change_events.id"), unique=True)
    
    alert_type = Column(String)  # standard, unreported_change
    severity = Column(String)  # critical, high, medium, low
    status = Column(String, default="open")  # open, investigating, resolved, dismissed
    
    title = Column(String)
    description = Column(Text)
    location = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    change_event = relationship("ChangeEvent", back_populates="alert")
    verifications = relationship("Verification", back_populates="alert")


class Verification(Base):
    __tablename__ = "verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    change_event_id = Column(Integer, ForeignKey("change_events.id"))
    alert_id = Column(Integer, ForeignKey("alerts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    status = Column(String)  # confirmed, rejected, needs_investigation
    comment = Column(Text)
    evidence_path = Column(String)
    
    verified_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    change_event = relationship("ChangeEvent", back_populates="verifications")
    alert = relationship("Alert", back_populates="verifications")
    user = relationship("User", back_populates="verifications")


class Investigation(Base):
    __tablename__ = "investigations"
    
    id = Column(Integer, primary_key=True, index=True)
    change_event_id = Column(Integer, ForeignKey("change_events.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    report = Column(Text)
    ai_summary = Column(Text)
    findings = Column(JSON)
    
    status = Column(String, default="in_progress")  # in_progress, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="investigations")


class ModelVersion(Base):
    __tablename__ = "model_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, index=True)
    version = Column(String, index=True)
    model_type = Column(String)
    
    file_path = Column(String)
    parameters = Column(JSON)
    
    training_dataset = Column(String)
    training_date = Column(DateTime)
    
    # Metrics
    metrics = Column(JSON)  # iou, precision, recall, f1, etc.
    
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
