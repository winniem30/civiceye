import { useState, useEffect } from 'react';
import { Map, Calendar, Play, Loader2 } from 'lucide-react';
import { satelliteService } from '../services/satelliteService';
import { changeDetectionService } from '../services/changeDetectionService';
import type { SatelliteImage, Bounds } from '../types';

const AnalyzeArea = () => {
  const [step, setStep] = useState(1);
  const [bounds, setBounds] = useState<Bounds | null>(null);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [images, setImages] = useState<SatelliteImage[]>([]);
  const [selectedImage1, setSelectedImage1] = useState<SatelliteImage | null>(null);
  const [selectedImage2, setSelectedImage2] = useState<SatelliteImage | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<any>(null);

  // Load bounds from sessionStorage if available (from ExploreMap)
  useEffect(() => {
    const storedBounds = sessionStorage.getItem('selectedBounds');
    if (storedBounds) {
      setBounds(JSON.parse(storedBounds));
      sessionStorage.removeItem('selectedBounds');
      setStep(2);
    }
  }, []);

  const handleSearchImages = async () => {
    if (!bounds) return;
    
    try {
      const searchResults = await satelliteService.searchImages({
        bounds,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        max_cloud_cover: 20,
        satellite: 'sentinel-2'
      });
      setImages(searchResults);
      setStep(3);
    } catch (error) {
      console.error('Failed to search images:', error);
      alert('Failed to search for satellite images');
    }
  };

  const handleRunAnalysis = async () => {
    if (!selectedImage1 || !selectedImage2) return;
    
    setAnalyzing(true);
    try {
      const result = await changeDetectionService.detectChange({
        image_t1_id: selectedImage1.id,
        image_t2_id: selectedImage2.id,
        method: 'baseline'
      });
      setResult(result);
      setStep(5);
    } catch (error) {
      console.error('Analysis failed:', error);
      alert('Change detection analysis failed');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Analyze Area</h1>

      {/* Progress Steps */}
      <div className="flex items-center justify-between mb-8">
        <StepIndicator step={1} currentStep={step} label="Select Area" />
        <div className="flex-1 h-1 bg-gray-200 mx-4" />
        <StepIndicator step={2} currentStep={step} label="Choose Dates" />
        <div className="flex-1 h-1 bg-gray-200 mx-4" />
        <StepIndicator step={3} currentStep={step} label="Select Images" />
        <div className="flex-1 h-1 bg-gray-200 mx-4" />
        <StepIndicator step={4} currentStep={step} label="Run Analysis" />
        <div className="flex-1 h-1 bg-gray-200 mx-4" />
        <StepIndicator step={5} currentStep={step} label="View Results" />
      </div>

      {/* Step 1: Select Area */}
      {step === 1 && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Map className="w-5 h-5 mr-2" />
            Select Area of Interest
          </h2>
          <p className="text-gray-600 mb-4">
            Use the map to select an area for analysis. For this demo, enter bounds manually.
          </p>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium mb-1">Min X (Longitude)</label>
              <input
                type="number"
                className="input-field"
                placeholder="-180"
                onChange={(e) => setBounds({ ...bounds!, min_x: parseFloat(e.target.value) } as Bounds)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Min Y (Latitude)</label>
              <input
                type="number"
                className="input-field"
                placeholder="-90"
                onChange={(e) => setBounds({ ...bounds!, min_y: parseFloat(e.target.value) } as Bounds)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Max X (Longitude)</label>
              <input
                type="number"
                className="input-field"
                placeholder="180"
                onChange={(e) => setBounds({ ...bounds!, max_x: parseFloat(e.target.value) } as Bounds)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Max Y (Latitude)</label>
              <input
                type="number"
                className="input-field"
                placeholder="90"
                onChange={(e) => setBounds({ ...bounds!, max_y: parseFloat(e.target.value) } as Bounds)}
              />
            </div>
          </div>
          <button
            onClick={() => setStep(2)}
            className="btn-primary"
            disabled={!bounds}
          >
            Continue
          </button>
        </div>
      )}

      {/* Step 2: Choose Dates */}
      {step === 2 && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Calendar className="w-5 h-5 mr-2" />
            Choose Date Range
          </h2>
          <p className="text-gray-600 mb-4">
            Select the date range for satellite imagery comparison.
          </p>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium mb-1">Start Date</label>
              <input
                type="date"
                className="input-field"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">End Date</label>
              <input
                type="date"
                className="input-field"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
          </div>
          <div className="flex space-x-4">
            <button onClick={() => setStep(1)} className="btn-secondary">
              Back
            </button>
            <button onClick={handleSearchImages} className="btn-primary">
              Search Images
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Select Images */}
      {step === 3 && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Select Satellite Images</h2>
          <p className="text-gray-600 mb-4">
            Select two images to compare for change detection.
          </p>
          {images.length === 0 ? (
            <p className="text-gray-500">No images found for the selected criteria.</p>
          ) : (
            <div className="grid grid-cols-2 gap-4 mb-4">
              <ImageSelector
                images={images}
                selected={selectedImage1}
                onSelect={setSelectedImage1}
                label="Image 1 (Before)"
              />
              <ImageSelector
                images={images}
                selected={selectedImage2}
                onSelect={setSelectedImage2}
                label="Image 2 (After)"
              />
            </div>
          )}
          <div className="flex space-x-4">
            <button onClick={() => setStep(2)} className="btn-secondary">
              Back
            </button>
            <button
              onClick={() => setStep(4)}
              className="btn-primary"
              disabled={!selectedImage1 || !selectedImage2}
            >
              Continue
            </button>
          </div>
        </div>
      )}

      {/* Step 4: Run Analysis */}
      {step === 4 && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Play className="w-5 h-5 mr-2" />
            Run Change Detection
          </h2>
          <div className="mb-6">
            <h3 className="font-medium mb-2">Selected Images</h3>
            <div className="grid grid-cols-2 gap-4">
              <ImageSummary image={selectedImage1} label="Before" />
              <ImageSummary image={selectedImage2} label="After" />
            </div>
          </div>
          <div className="flex space-x-4">
            <button onClick={() => setStep(3)} className="btn-secondary">
              Back
            </button>
            <button
              onClick={handleRunAnalysis}
              className="btn-primary"
              disabled={analyzing}
            >
              {analyzing ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Analyzing...
                </>
              ) : (
                'Run Analysis'
              )}
            </button>
          </div>
        </div>
      )}

      {/* Step 5: View Results */}
      {step === 5 && result && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Analysis Results</h2>
          <AnalysisResult result={result} />
          <div className="flex space-x-4 mt-6">
            <button onClick={() => setStep(1)} className="btn-secondary">
              New Analysis
            </button>
            <button className="btn-primary">
              View Full Details
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

const StepIndicator = ({ step, currentStep, label }: { step: number; currentStep: number; label: string }) => {
  const isComplete = step < currentStep;
  const isCurrent = step === currentStep;
  const isPending = step > currentStep;

  return (
    <div className="flex flex-col items-center">
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
          isComplete ? 'bg-green-500 text-white' : isCurrent ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-600'
        }`}
      >
        {isComplete ? '✓' : step}
      </div>
      <span className={`text-xs mt-1 ${isCurrent ? 'font-medium' : 'text-gray-500'}`}>{label}</span>
    </div>
  );
};

const ImageSelector = ({
  label,
  images,
  selected,
  onSelect,
}: {
  label: string;
  images: SatelliteImage[];
  selected: SatelliteImage | null;
  onSelect: (image: SatelliteImage | null) => void;
}) => {
  return (
    <div className="border rounded-xl p-4 bg-white shadow-sm">
      <h3 className="font-semibold text-lg mb-3">{label}</h3>

      <select
        value={selected?.id ?? ''}
        onChange={(e) => {
          const image = images.find(
            (img) => img.id === Number(e.target.value)
          );
          onSelect(image ?? null);
        }}
        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
      >
        <option value="">Select satellite image</option>

        {images.map((image) => (
          <option key={image.id} value={image.id}>
            {image.satellite_name} — {image.acquisition_date}
          </option>
        ))}
      </select>

      {selected && (
        <div className="mt-4 space-y-2 text-sm">
          {selected.preview_path && (
            <img
              src={selected.preview_path}
              alt={`Satellite image from ${selected.acquisition_date}`}
              className="w-full h-40 object-cover rounded-lg border"
            />
          )}

          <div className="grid grid-cols-2 gap-2">
            <div className="bg-gray-50 rounded-lg p-2">
              <p className="text-gray-500">Satellite</p>
              <p className="font-medium">
                {selected.satellite_name}
              </p>
            </div>

            <div className="bg-gray-50 rounded-lg p-2">
              <p className="text-gray-500">Date</p>
              <p className="font-medium">
                {selected.acquisition_date}
              </p>
            </div>

            <div className="bg-gray-50 rounded-lg p-2">
              <p className="text-gray-500">Cloud Cover</p>
              <p className="font-medium">
                {selected.cloud_cover !== undefined
                  ? `${selected.cloud_cover}%`
                  : 'Not available'}
              </p>
            </div>

            <div className="bg-gray-50 rounded-lg p-2">
              <p className="text-gray-500">Image ID</p>
              <p className="font-medium">
                #{selected.id}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const ImageSummary = ({ image, label }: { image: SatelliteImage | null; label: string }) => {
  if (!image) return null;
  return (
    <div className="border rounded-lg p-4">
      <h4 className="font-medium mb-2">{label}</h4>
      <p className="text-sm text-gray-600">Date: {new Date(image.acquisition_date).toLocaleDateString()}</p>
      <p className="text-sm text-gray-600">Satellite: {image.satellite_name}</p>
      <p className="text-sm text-gray-600">Cloud Cover: {image.cloud_cover}%</p>
    </div>
  );
};

const AnalysisResult = ({ result }: { result: any }) => {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-4">
        <ResultCard label="Change Area" value={`${result.change_area.toFixed(2)} px²`} />
        <ResultCard label="Change Percentage" value={`${result.change_percentage.toFixed(2)}%`} />
        <ResultCard label="Confidence" value={`${(result.confidence * 100).toFixed(1)}%`} />
      </div>
      {result.is_human_induced !== undefined && (
        <div className="border rounded-lg p-4">
          <h3 className="font-medium mb-2">Classification</h3>
          <p className="text-sm text-gray-600">
            Type: {result.is_human_induced ? 'Human-Induced' : 'Natural'}
          </p>
          <p className="text-sm text-gray-600">
            Activity: {result.activity_type || 'N/A'}
          </p>
        </div>
      )}
    </div>
  );
};

const ResultCard = ({ label, value }: { label: string; value: string }) => {
  return (
    <div className="border rounded-lg p-4 text-center">
      <p className="text-sm text-gray-600">{label}</p>
      <p className="text-xl font-semibold">{value}</p>
    </div>
  );
};

export default AnalyzeArea;
