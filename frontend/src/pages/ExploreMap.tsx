import { useState, useRef } from 'react';
import MapGL, { MapRef, ViewState, Marker, Source, Layer } from 'react-map-gl';
import { Map as MapIcon, Layers, Calendar, Search } from 'lucide-react';

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN || '';

interface PolygonPoint {
  lng: number;
  lat: number;
}

const ExploreMap = () => {
  const mapRef = useRef<MapRef>(null);
  const [viewState, setViewState] = useState<ViewState>({
    longitude: 0,
    latitude: 20,
    zoom: 2,
  });
  const [selectedBounds, setSelectedBounds] = useState<any>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [drawingPoints, setDrawingPoints] = useState<PolygonPoint[]>([]);

  const handleMapClick = (event: any) => {
    if (!isDrawing) return;
    
    const { lng, lat } = event.lngLat;
    const newPoint = { lng, lat };
    setDrawingPoints([...drawingPoints, newPoint]);
  };

  const handleRightClick = (event: any) => {
    if (!isDrawing || drawingPoints.length < 3) return;
    
    // Complete the polygon
    const bounds = calculateBounds(drawingPoints);
    setSelectedBounds(bounds);
    setIsDrawing(false);
    setDrawingPoints([]);
  };

  const calculateBounds = (points: PolygonPoint[]) => {
    const lngs = points.map(p => p.lng);
    const lats = points.map(p => p.lat);
    return {
      min_x: Math.min(...lngs),
      max_x: Math.max(...lngs),
      min_y: Math.min(...lats),
      max_y: Math.max(...lats),
    };
  };

  const handleClearSelection = () => {
    setSelectedBounds(null);
    setDrawingPoints([]);
  };

  const handleAnalyzeArea = () => {
    if (selectedBounds) {
      // Store bounds in sessionStorage for AnalyzeArea to use
      sessionStorage.setItem('selectedBounds', JSON.stringify(selectedBounds));
      window.location.href = '/analyze';
    }
  };

  const handleDrawToggle = () => {
    setIsDrawing(!isDrawing);
  };

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="bg-white border-b px-4 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <MapIcon className="w-5 h-5 text-primary-600" />
          <h1 className="text-xl font-semibold">Explore Map</h1>
        </div>
        <div className="flex items-center space-x-4">
          <button
            onClick={handleDrawToggle}
            className={`px-4 py-2 rounded-lg transition-colors ${
              isDrawing ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-800'
            }`}
          >
            {isDrawing ? 'Stop Drawing' : 'Draw Area'}
          </button>
        </div>
      </div>

      {/* Map Container */}
      <div className="flex-1 relative">
        {MAPBOX_TOKEN ? (
          <MapGL
            ref={mapRef}
            {...viewState}
            onMove={evt => setViewState(evt.viewState)}
            onClick={handleMapClick}
            onContextMenu={handleRightClick}
            style={{ width: '100%', height: '100%' }}
            mapStyle="mapbox://styles/mapbox/satellite-v9"
            mapboxAccessToken={MAPBOX_TOKEN}
          >
            {/* Drawing points markers */}
            {drawingPoints.map((point, index) => (
              <Marker key={index} longitude={point.lng} latitude={point.lat}>
                <div className="w-4 h-4 bg-primary-600 rounded-full border-2 border-white shadow-lg" />
              </Marker>
            ))}

            {/* Drawing lines */}
            {drawingPoints.length > 1 && (
              <Source
                id="drawing-line"
                type="geojson"
                data={{
                  type: 'Feature',
                  geometry: {
                    type: 'LineString',
                    coordinates: drawingPoints.map(p => [p.lng, p.lat]),
                  },
                }}
              >
                <Layer
                  id="drawing-line-layer"
                  type="line"
                  paint={{
                    'line-color': '#2563eb',
                    'line-width': 3,
                    'line-dasharray': [2, 2],
                  }}
                />
              </Source>
            )}

            {/* Selected area polygon */}
            {selectedBounds && (
              <Source
                id="selected-area"
                type="geojson"
                data={{
                  type: 'Feature',
                  geometry: {
                    type: 'Polygon',
                    coordinates: [[
                      [selectedBounds.min_x, selectedBounds.min_y],
                      [selectedBounds.max_x, selectedBounds.min_y],
                      [selectedBounds.max_x, selectedBounds.max_y],
                      [selectedBounds.min_x, selectedBounds.max_y],
                      [selectedBounds.min_x, selectedBounds.min_y],
                    ]],
                  },
                }}
              >
                <Layer
                  id="selected-area-fill"
                  type="fill"
                  paint={{
                    'fill-color': '#2563eb',
                    'fill-opacity': 0.2,
                  }}
                />
                <Layer
                  id="selected-area-border"
                  type="line"
                  paint={{
                    'line-color': '#2563eb',
                    'line-width': 3,
                  }}
                />
              </Source>
            )}
          </MapGL>
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gray-100">
            <div className="text-center">
              <MapIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-2">Mapbox token not configured</p>
              <p className="text-sm text-gray-400">Add VITE_MAPBOX_TOKEN to your environment variables</p>
            </div>
          </div>
        )}

        {/* Layer Control Panel */}
        <div className="absolute top-4 right-4 bg-white rounded-lg shadow-lg p-4 w-64">
          <h3 className="font-semibold mb-3 flex items-center">
            <Layers className="w-4 h-4 mr-2" />
            Layers
          </h3>
          <div className="space-y-2">
            <LayerCheckbox label="Satellite Imagery" checked={true} />
            <LayerCheckbox label="Change Detection" checked={true} />
            <LayerCheckbox label="Human Activity" checked={false} />
            <LayerCheckbox label="Buildings" checked={false} />
            <LayerCheckbox label="Roads" checked={false} />
            <LayerCheckbox label="Water Bodies" checked={true} />
            <LayerCheckbox label="Vegetation" checked={false} />
            <LayerCheckbox label="Risk Zones" checked={true} />
          </div>
        </div>

        {/* Search Panel */}
        <div className="absolute top-4 left-4 bg-white rounded-lg shadow-lg p-4 w-80">
          <div className="flex items-center space-x-2 mb-3">
            <Search className="w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search location..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Calendar className="w-4 h-4" />
            <span>Select date range for comparison</span>
          </div>
        </div>

        {/* Selected Area Info */}
        {selectedBounds && (
          <div className="absolute bottom-4 left-4 bg-white rounded-lg shadow-lg p-4">
            <h3 className="font-semibold mb-2">Selected Area</h3>
            <div className="text-sm text-gray-600 mb-3">
              <p>Min: {selectedBounds.min_y.toFixed(4)}, {selectedBounds.min_x.toFixed(4)}</p>
              <p>Max: {selectedBounds.max_y.toFixed(4)}, {selectedBounds.max_x.toFixed(4)}</p>
            </div>
            <div className="flex space-x-2">
              <button onClick={handleClearSelection} className="px-3 py-2 bg-gray-200 text-gray-800 rounded-lg text-sm hover:bg-gray-300 transition-colors">
                Clear
              </button>
              <button onClick={handleAnalyzeArea} className="btn-primary text-sm">
                Analyze This Area
              </button>
            </div>
          </div>
        )}

        {/* Drawing Instructions */}
        {isDrawing && (
          <div className="absolute top-20 left-4 bg-white rounded-lg shadow-lg p-4 w-64">
            <h3 className="font-semibold mb-2 text-primary-600">Drawing Mode</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Click to add points</li>
              <li>• Right-click to complete polygon</li>
              <li>• Minimum 3 points required</li>
            </ul>
            <p className="text-xs text-gray-400 mt-2">Points: {drawingPoints.length}</p>
          </div>
        )}
      </div>
    </div>
  );
};

const LayerCheckbox = ({ label, checked }: { label: string; checked: boolean }) => {
  return (
    <label className="flex items-center space-x-2 cursor-pointer">
      <input type="checkbox" defaultChecked={checked} className="rounded text-primary-600" />
      <span className="text-sm">{label}</span>
    </label>
  );
};

export default ExploreMap;
