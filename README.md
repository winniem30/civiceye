# CIVIC-EYE

**AI-Powered Geospatial Change Intelligence Platform**

CIVIC-EYE transforms satellite imagery from passive observation into proactive detection, contextual risk assessment and early warning of human-induced environmental and infrastructure changes.

## Vision

> "What changed?"

CIVIC-EYE answers:
- **What changed** → Was it caused by humans → What type of activity is it → How fast is it changing → What is the surrounding impact/risk → What evidence supports the alert → What could happen next?

## Architecture

```
Sentinel-2 STAC API (Real Satellite Data)
↓
Image Preprocessing (Band Download, AOI Clipping)
↓
Spectral Indices (NDVI, NDWI, NDBI)
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
- Leaflet + OpenStreetMap (No Mapbox token required)
- Recharts

### Backend
- Python + FastAPI
- PostgreSQL + PostGIS
- Redis + Celery

### Satellite Data
- Sentinel-2 Level-2A via STAC API (AWS Earth Search)
- Real-time band download and processing
- Georeferenced raster storage

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
│   │   │   ├── satellite.py    # Sentinel-2 search & processing
│   │   │   ├── raster.py        # Raster visualization
│   │   │   └── ...
│   │   ├── core/           # Configuration, security
│   │   ├── db/             # Database models (Observation, SatelliteImage)
│   │   ├── ml/             # ML models and pipelines
│   │   ├── satellite/      # STAC provider implementation
│   │   ├── preprocessing/  # Band download, clipping, indices
│   │   ├── gis/            # GIS context analysis
│   │   └── services/       # Business logic
│   ├── data/
│   │   ├── rasters/        # Processed GeoTIFF storage
│   │   ├── satellite/      # Downloaded bands
│   │   └── cache/
│   ├── tests/
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   │   ├── ExploreMap.tsx    # Leaflet map with AOI selection
│   │   │   └── AnalyzeArea.tsx   # Satellite search & processing UI
│   │   ├── services/
│   │   │   └── satelliteService.ts  # API integration
│   │   └── types/
│   └── package.json
├── ml/                     # ML training scripts
├── docker/
├── docs/
└── docker-compose.yml
```

## Real Sentinel-2 Pipeline

### Data Source
- **Provider**: AWS Earth Search STAC API (public, no authentication required)
- **Collection**: sentinel-2-l2a (Level-2A, atmospherically corrected)
- **Bands**: B02 (Blue), B03 (Green), B04 (Red), B08 (NIR), B11 (SWIR1), B12 (SWIR2)

### Processing Workflow
1. **Search**: Query STAC API for observations matching AOI, date range, cloud cover
2. **Download**: Download required bands from public URLs
3. **Clip**: Clip bands to AOI bounds (preserves CRS and georeferencing)
4. **Calculate**: Compute NDVI, NDWI, NDBI indices with proper divide-by-zero handling
5. **Store**: Save georeferenced GeoTIFFs to filesystem (not database)
6. **Serve**: Provide raster tiles via API for visualization

### Spectral Indices
- **NDVI** (Normalized Difference Vegetation Index): (B08 - B04) / (B08 + B04)
- **NDWI** (Normalized Difference Water Index): (B03 - B08) / (B03 + B08)
- **NDBI** (Normalized Difference Built-up Index): (B11 - B08) / (B11 + B08)

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
STAC_ENDPOINT=https://earth-search.aws.element84.com/v1
SENTINEL_COLLECTION=sentinel-2-l2a
```

**Note**: No Mapbox token required. OpenStreetMap is used for the basemap.

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

## Using the Real Sentinel-2 Pipeline

### Example AOI for Testing
Use these bounds for San Francisco Bay Area:
```json
{
  "min_x": -122.5,
  "min_y": 37.7,
  "max_x": -122.3,
  "max_y": 37.8
}
```

### Step-by-Step Workflow

1. **Select Area**
   - Navigate to Explore Map
   - Draw polygon or enter bounds manually
   - Click "Analyze This Area"

2. **Choose Date Range**
   - Select start and end dates
   - Recommended: 1-3 month range for best results
   - Click "Search Observations"

3. **Select Observation**
   - Review available Sentinel-2 observations
   - Check cloud cover percentage
   - Select observation with lowest cloud cover
   - Click "Process Observation"

4. **View Processed Layers**
   - Wait for processing to complete (downloads bands, clips to AOI, calculates indices)
   - Select layer to visualize: NDVI, NDWI, or NDBI
   - View georeferenced raster tiles

### API Endpoints

- `POST /satellite/search` - Search Sentinel-2 observations
- `POST /satellite/process` - Process observation (download, clip, calculate indices)
- `GET /satellite/observations` - List processed observations
- `GET /satellite/observations/{id}` - Get observation details
- `GET /satellite/observations/{id}/layers` - Get available layers
- `GET /raster/raster/{observation_id}/{layer_name}` - Get raster tile as PNG

## Important Notes

- **No Mapbox Account Required**: Uses OpenStreetMap basemap via Leaflet
- **Real Satellite Data**: Downloads actual Sentinel-2 bands from AWS
- **Processing Time**: First observation may take 2-5 minutes (band downloads)
- **Resumable**: Already-processed observations are not re-downloaded
- **Storage**: Rasters stored in `backend/data/rasters/` by observation ID
- **Error Handling**: Failed processing records error message for debugging

## License

MIT License - CSE Major Project
