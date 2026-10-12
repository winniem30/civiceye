import { useState, useRef } from 'react';
import { MapContainer, TileLayer, Polygon, Marker, useMapEvents } from 'react-leaflet';
import { Icon, LatLng } from 'leaflet';
import { Map as MapIcon, Layers, Calendar, Search } from 'lucide-react';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icon in Leaflet with React
const customIcon = new Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

interface PolygonPoint {
  lng: number;
  lat: number;
}

interface MapClickHandlerProps {
  isDrawing: boolean;
  onMapClick: (latlng: LatLng) => void;
}

const MapClickHandler = ({ isDrawing, onMapClick }: MapClickHandlerProps) => {
  useMapEvents({
    click(e) {
      if (isDrawing) {
        onMapClick(e.latlng);
      }
    },
    contextmenu(e) {
      if (isDrawing) {
        e.originalEvent.preventDefault();
      }
    }
  });
  return null;
};

const ExploreMap = () => {
  const [selectedBounds, setSelectedBounds] = useState<any>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [drawingPoints, setDrawingPoints] = useState<PolygonPoint[]>([]);
  const [mapCenter, setMapCenter] = useState<[number, number]>([20, 0]);
  const [mapZoom, setMapZoom] = useState(2);

  const handleMapClick = (latlng: LatLng) => {
    if (!isDrawing) return;
    
    const newPoint = { lng: latlng.lng, lat: latlng.lat };
    setDrawingPoints([...drawingPoints, newPoint]);
  };

  const handleRightClick = () => {
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
      sessionStorage.setItem('selectedBounds', JSON.stringify(selectedBounds));
      window.location.href = '/analyze';
    }
  };

  const handleDrawToggle = () => {
    setIsDrawing(!isDrawing);
    if (!isDrawing) {
      setDrawingPoints([]);
    }
  };

  const drawingPolygonPositions = drawingPoints.map(p => [p.lat, p.lng] as [number, number]);
  const selectedPolygonPositions = selectedBounds ? [
    [selectedBounds.min_y, selectedBounds.min_x],
    [selectedBounds.min_y, selectedBounds.max_x],
    [selectedBounds.max_y, selectedBounds.max_x],
    [selectedBounds.max_y, selectedBounds.min_x],
    [selectedBounds.min_y, selectedBounds.min_x]
  ] as [number, number][] : [];

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
        <MapContainer
          center={mapCenter}
          zoom={mapZoom}
          style={{ width: '100%', height: '100%' }}
          className="z-0"
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          
          <MapClickHandler isDrawing={isDrawing} onMapClick={handleMapClick} />

          {/* Drawing points markers */}
          {drawingPoints.map((point, index) => (
            <Marker
              key={index}
              position={[point.lat, point.lng]}
              icon={customIcon}
            />
          ))}

          {/* Drawing polygon */}
          {drawingPoints.length > 2 && (
            <Polygon
              positions={drawingPolygonPositions}
              pathOptions={{ color: '#2563eb', weight: 3, dashArray: '5, 5' }}
            />
          )}

          {/* Selected area polygon */}
          {selectedBounds && (
            <Polygon
              positions={selectedPolygonPositions}
              pathOptions={{ color: '#2563eb', weight: 3, fillColor: '#2563eb', fillOpacity: 0.2 }}
            />
          )}
        </MapContainer>

        {/* Layer Control Panel */}
        <div className="absolute top-4 right-4 bg-white rounded-lg shadow-lg p-4 w-64 z-10">
          <h3 className="font-semibold mb-3 flex items-center">
            <Layers className="w-4 h-4 mr-2" />
            Layers
          </h3>
          <div className="space-y-2">
            <LayerCheckbox label="OpenStreetMap" checked={true} />
            <LayerCheckbox label="Change Detection" checked={false} />
            <LayerCheckbox label="Human Activity" checked={false} />
            <LayerCheckbox label="Water Bodies" checked={false} />
            <LayerCheckbox label="Vegetation" checked={false} />
          </div>
        </div>

        {/* Search Panel */}
        <div className="absolute top-4 left-4 bg-white rounded-lg shadow-lg p-4 w-80 z-10">
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
          <div className="absolute bottom-4 left-4 bg-white rounded-lg shadow-lg p-4 z-10">
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
          <div className="absolute top-20 left-4 bg-white rounded-lg shadow-lg p-4 w-64 z-10">
            <h3 className="font-semibold mb-2 text-primary-600">Drawing Mode</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Click to add points</li>
              <li>• Click "Stop Drawing" to complete polygon</li>
              <li>• Minimum 3 points required</li>
            </ul>
            <p className="text-xs text-gray-400 mt-2">Points: {drawingPoints.length}</p>
            <button
              onClick={handleRightClick}
              className="mt-3 w-full px-3 py-2 bg-primary-600 text-white rounded-lg text-sm hover:bg-primary-700 transition-colors"
            >
              Complete Polygon
            </button>
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
