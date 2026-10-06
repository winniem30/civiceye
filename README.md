# CIVIC-EYE

**AI-Powered Geospatial Change Intelligence Platform**

CIVIC-EYE transforms satellite imagery from passive observation into proactive detection, contextual risk assessment and early warning of human-induced environmental and infrastructure changes.

## Vision

> "What changed?"

CIVIC-EYE answers:
- **What changed** → Was it caused by humans → What type of activity is it → How fast is it changing → What is the surrounding impact/risk → What evidence supports the alert → What could happen next?

## Architecture

```
Satellite / Remote Sensing Data
↓
Image Preprocessing
↓
Multi-temporal Change Detection
↓
Human vs Natural Change Classification
↓
Human Activity Classification
↓
Temporal Change Tracking
↓
GIS Context Analysis
↓
Risk Assessment
↓
Explainable AI
↓
Future Change Prediction
↓
Alert / Investigation System
↓
Interactive GIS Dashboard
```

## Technology Stack

### Frontend
- React + TypeScript
- Tailwind CSS
- Mapbox GL JS
- Recharts

### Backend
- Python + FastAPI
- PostgreSQL + PostGIS
- Redis + Celery

### AI/ML
- PyTorch
- scikit-learn
- XGBoost
- OpenCV
- SHAP

### Geospatial
- Rasterio
- GDAL
- GeoPandas
- Shapely
- NumPy
## Key Features

- **Area of Interest (AOI) Selection** – Select a specific geographic area for monitoring and analysis.
- **Satellite Image Comparison** – Compare satellite imagery from different dates to identify changes over time.
- **AI-Based Change Detection** – Detect significant changes in land, infrastructure and other geographic features.
- **Human vs Natural Change Classification** – Identify whether detected changes are likely to be caused by human activity or natural processes.
- **Human Activity Classification** – Classify detected human-induced changes into relevant activity categories.
- **GIS Context Analysis** – Analyze nearby roads, buildings, water bodies and other geographic features to understand the surrounding impact.
- **Risk Assessment** – Evaluate the potential environmental and infrastructure risks associated with detected changes.
- **Explainable AI** – Provide supporting information to help users understand why an alert was generated.
- **Temporal Change Tracking** – Track how detected changes develop over time.
- **Interactive GIS Dashboard** – Present detected changes, risk information and investigation results through an interactive map-based interface.
- **Alerts and Investigations** – Help users identify important changes and investigate them using available evidence.
- **Future Change Prediction** – Use historical change patterns to estimate possible future developments.
## Project Structure

```
civiceye/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Configuration, security
│   │   ├── db/             # Database models
│   │   ├── ml/             # ML models and pipelines
│   │   ├── satellite/      # Satellite data providers
│   │   ├── preprocessing/  # Image preprocessing
│   │   ├── gis/            # GIS context analysis
│   │   └── services/       # Business logic
│   ├── tests/
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── types/
│   └── package.json
├── ml/                     # ML training scripts
├── data/                   # Data storage
│   ├── satellite/
│   ├── models/
│   └── cache/
├── docker/
├── docs/
└── docker-compose.yml
```

## Development Phases

### Phase 1 — Working Foundation
- Repository structure
- Database setup
- Backend API foundation
- Frontend foundation
- Map integration
- AOI selection

### Phase 2 — Satellite Pipeline
- Satellite data provider
- Preprocessing pipeline
- Imagery storage
- Before/after comparison

### Phase 3 — Core AI
- Baseline change detection
- Deep learning change detection
- Human/natural classification
- Activity classification

### Phase 4 — Intelligence
- Temporal tracking
- Change DNA
- GIS context
- Risk engine
- Explainability

### Phase 5 — Advanced Features
- Future prediction
- What-if simulation
- Unreported change detection
- Human verification
- Evidence chain
- AI investigation assistant

### Phase 6 — Productization
- Authentication
- Role-based access
- Alerts
- Reports
- Testing
- Docker
- Deployment

## Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+ with PostGIS
- Redis

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd frontend
npm install
```

### Database Setup
```bash
# Create database
createdb civiceye
psql civiceye -c "CREATE EXTENSION postgis;"
```

### Environment Variables
Create `.env` file in backend directory:
```
DATABASE_URL=postgresql://user:password@localhost/civiceye
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
MAPBOX_TOKEN=your-mapbox-token
```

## Running the Application

### Backend
```bash
cd backend
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm run dev
```

### With Docker
```bash
docker-compose up
```

## License

MIT License - CSE Major Project
