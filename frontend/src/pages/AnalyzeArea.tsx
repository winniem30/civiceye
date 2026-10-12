import { useState, useEffect } from 'react';
import { Map, Calendar, Play, Loader2, Layers } from 'lucide-react';
import { satelliteService, SatelliteImage, Observation } from '../services/satelliteService';
import { changeDetectionService } from '../services/changeDetectionService';
import type { Bounds, ChangeEvent } from '../types';

const AnalyzeArea = () => {
  const [step, setStep] = useState(1);
  const [bounds, setBounds] = useState<Bounds | null>(null);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [images, setImages] = useState<SatelliteImage[]>([]);
  const [selectedImage1, setSelectedImage1] = useState<SatelliteImage | null>(null);
  const [selectedImage2, setSelectedImage2] = useState<SatelliteImage | null>(null);
  const [observation1, setObservation1] = useState<Observation | null>(null);
  const [observation2, setObservation2] = useState<Observation | null>(null);
  const [processing, setProcessing] = useState(false);
  const [selectedLayer, setSelectedLayer] = useState<string>('ndvi');
  const [layerImageUrl, setLayerImageUrl] = useState<string | null>(null);
  const [changeEvent, setChangeEvent] = useState<ChangeEvent | null>(null);

  // Load bounds from sessionStorage if available (from ExploreMap)
  useEffect(() => {
    const storedBounds = sessionStorage.getItem('selectedBounds');
    if (storedBounds) {
      setBounds(JSON.parse(storedBounds));
      sessionStorage.removeItem('selectedBounds');
      setStep(2);
    }
  }, []);

  // Poll observation status if processing
  useEffect(() => {
    const obs1Processing = observation1 && observation1.processing_status === 'processing';
    const obs2Processing = observation2 && observation2.processing_status === 'processing';

    if (obs1Processing || obs2Processing) {
      const interval = setInterval(async () => {
        try {
          if (obs1Processing && observation1) {
            const updated = await satelliteService.getObservation(observation1.id);
            setObservation1(updated);
          }
          if (obs2Processing && observation2) {
            const updated = await satelliteService.getObservation(observation2.id);
            setObservation2(updated);
          }

          // Check if both are completed
          const obs1Complete = observation1?.processing_status === 'completed';
          const obs2Complete = observation2?.processing_status === 'completed';

          if (obs1Complete && obs2Complete) {
            clearInterval(interval);
            // Load default layer from observation 1
            if (observation1) {
              loadLayerImage(observation1.id, selectedLayer);
            }
          } else if (observation1?.processing_status === 'failed' || observation2?.processing_status === 'failed') {
            clearInterval(interval);
            const errorMsg = observation1?.error_message || observation2?.error_message;
            alert(`Processing failed: ${errorMsg}`);
          }
        } catch (error) {
          console.error('Failed to poll observation status:', error);
        }
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [observation1, observation2, selectedLayer]);

  const loadLayerImage = async (observationId: number, layerName: string) => {
    try {
      const blob = await satelliteService.getRasterTile(observationId, layerName);
      const url = URL.createObjectURL(blob);
      setLayerImageUrl(url);
    } catch (error) {
      console.error('Failed to load layer image:', error);
    }
  };

  const handleSearchImages = async () => {
    if (!bounds) return;
    
    setProcessing(true);
    try {
      const searchResults = await satelliteService.searchObservations({
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
    } finally {
      setProcessing(false);
    }
  };

  const handleProcessObservation = async (image: SatelliteImage, obsNum: 1 | 2) => {
    setProcessing(true);
    try {
      const obs = await satelliteService.processObservation({
        stac_id: image.stac_id,
        aoi_bounds: bounds || undefined,
        clip_to_aoi: true
      });

      if (obsNum === 1) {
        setObservation1(obs);
      } else {
        setObservation2(obs);
      }

      if (obs.processing_status === 'completed') {
        loadLayerImage(obs.id, selectedLayer);
      }
    } catch (error) {
      console.error('Failed to process observation:', error);
      alert('Failed to process observation');
    } finally {
      setProcessing(false);
    }
  };

  const handleRunChangeDetection = async () => {
    if (!observation1 || !observation2) {
      alert('Please process two observations first');
      return;
    }

    setProcessing(true);
    try {
      const event = await changeDetectionService.detectChange({
        observation_t1_id: observation1.id,
        observation_t2_id: observation2.id,
        method: 'baseline'
      });
      setChangeEvent(event);
      alert(`Change detection started! Event ID: ${event.id}. Check the Dashboard for results.`);
    } catch (error) {
      console.error('Failed to run change detection:', error);
      alert('Failed to run change detection');
    } finally {
      setProcessing(false);
    }
  };

  const handleLayerChange = (layerName: string) => {
    setSelectedLayer(layerName);
    if (observation && observation.processing_status === 'completed') {
      loadLayerImage(observation.id, layerName);
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
        <StepIndicator step={4} currentStep={step} label="Process" />
        <div className="flex-1 h-1 bg-gray-200 mx-4" />
        <StepIndicator step={5} currentStep={step} label="Change Detection" />
      </div>

      {/* Step 1: Select Area */}
      {step === 1 && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Map className="w-5 h-5 mr-2" />
            Select Area of Interest
          </h2>
          <p className="text-gray-600 mb-4">
            Enter the bounding box coordinates for your area of interest, or use the map to select.
          </p>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium mb-1">Min X (Longitude)</label>
              <input
                type="number"
                step="any"
                className="input-field"
                placeholder="-180"
                value={bounds?.min_x || ''}
                onChange={(e) => setBounds({ ...bounds!, min_x: parseFloat(e.target.value) } as Bounds)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Min Y (Latitude)</label>
              <input
                type="number"
                step="any"
                className="input-field"
                placeholder="-90"
                value={bounds?.min_y || ''}
                onChange={(e) => setBounds({ ...bounds!, min_y: parseFloat(e.target.value) } as Bounds)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Max X (Longitude)</label>
              <input
                type="number"
                step="any"
                className="input-field"
                placeholder="180"
                value={bounds?.max_x || ''}
                onChange={(e) => setBounds({ ...bounds!, max_x: parseFloat(e.target.value) } as Bounds)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Max Y (Latitude)</label>
              <input
                type="number"
                step="any"
                className="input-field"
                placeholder="90"
                value={bounds?.max_y || ''}
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
            Select the date range for searching Sentinel-2 observations.
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
            <button onClick={handleSearchImages} className="btn-primary" disabled={processing}>
              {processing ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Searching...
                </>
              ) : (
                'Search Observations'
              )}
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Select Images */}
      {step === 3 && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Select Two Sentinel-2 Observations</h2>
          <p className="text-gray-600 mb-4">
            Select two observations (time 1 and time 2) to compare for change detection.
          </p>
          {images.length === 0 ? (
            <p className="text-gray-500">No observations found for the selected criteria.</p>
          ) : (
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium mb-2">Time 1 (Earlier)</label>
                <select
                  className="input-field"
                  value={selectedImage1?.id || ''}
                  onChange={(e) => {
                    const img = images.find(i => i.id === parseInt(e.target.value));
                    if (img) setSelectedImage1(img);
                  }}
                >
                  <option value="">Select observation...</option>
                  {images.map((img) => (
                    <option key={img.id} value={img.id}>
                      {new Date(img.acquisition_date).toLocaleDateString()} - Cloud: {img.cloud_cover?.toFixed(1)}%
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Time 2 (Later)</label>
                <select
                  className="input-field"
                  value={selectedImage2?.id || ''}
                  onChange={(e) => {
                    const img = images.find(i => i.id === parseInt(e.target.value));
                    if (img) setSelectedImage2(img);
                  }}
                >
                  <option value="">Select observation...</option>
                  {images.map((img) => (
                    <option key={img.id} value={img.id}>
                      {new Date(img.acquisition_date).toLocaleDateString()} - Cloud: {img.cloud_cover?.toFixed(1)}%
                    </option>
                  ))}
                </select>
              </div>
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

      {/* Step 4: Process Observations */}
      {step === 4 && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Layers className="w-5 h-5 mr-2" />
            Process Observations
          </h2>

          <div className="grid grid-cols-2 gap-6 mb-6">
            {/* Observation 1 */}
            <div>
              <h3 className="font-medium mb-2">Time 1: {selectedImage1 ? new Date(selectedImage1.acquisition_date).toLocaleDateString() : 'Not selected'}</h3>
              {observation1 ? (
                <div className="text-sm">
                  <p className="mb-2">
                    Status: <span className={`font-medium ${
                      observation1.processing_status === 'completed' ? 'text-green-600' :
                      observation1.processing_status === 'processing' ? 'text-yellow-600' :
                      observation1.processing_status === 'failed' ? 'text-red-600' : 'text-gray-600'
                    }`}>
                      {observation1.processing_status}
                    </span>
                  </p>
                  {observation1.error_message && (
                    <p className="text-red-600 text-sm">Error: {observation1.error_message}</p>
                  )}
                  {observation1.processing_status !== 'completed' && observation1.processing_status !== 'processing' && (
                    <button
                      onClick={() => handleProcessObservation(selectedImage1!, 1)}
                      className="btn-primary text-sm"
                      disabled={processing}
                    >
                      {processing ? 'Processing...' : 'Process'}
                    </button>
                  )}
                </div>
              ) : (
                <button
                  onClick={() => handleProcessObservation(selectedImage1!, 1)}
                  className="btn-primary text-sm"
                  disabled={processing}
                >
                  {processing ? 'Processing...' : 'Process'}
                </button>
              )}
            </div>

            {/* Observation 2 */}
            <div>
              <h3 className="font-medium mb-2">Time 2: {selectedImage2 ? new Date(selectedImage2.acquisition_date).toLocaleDateString() : 'Not selected'}</h3>
              {observation2 ? (
                <div className="text-sm">
                  <p className="mb-2">
                    Status: <span className={`font-medium ${
                      observation2.processing_status === 'completed' ? 'text-green-600' :
                      observation2.processing_status === 'processing' ? 'text-yellow-600' :
                      observation2.processing_status === 'failed' ? 'text-red-600' : 'text-gray-600'
                    }`}>
                      {observation2.processing_status}
                    </span>
                  </p>
                  {observation2.error_message && (
                    <p className="text-red-600 text-sm">Error: {observation2.error_message}</p>
                  )}
                  {observation2.processing_status !== 'completed' && observation2.processing_status !== 'processing' && (
                    <button
                      onClick={() => handleProcessObservation(selectedImage2!, 2)}
                      className="btn-primary text-sm"
                      disabled={processing}
                    >
                      {processing ? 'Processing...' : 'Process'}
                    </button>
                  )}
                </div>
              ) : (
                <button
                  onClick={() => handleProcessObservation(selectedImage2!, 2)}
                  className="btn-primary text-sm"
                  disabled={processing}
                >
                  {processing ? 'Processing...' : 'Process'}
                </button>
              )}
            </div>
          </div>

          <div className="flex space-x-4">
            <button onClick={() => setStep(3)} className="btn-secondary">
              Back
            </button>
            <button
              onClick={() => setStep(5)}
              className="btn-primary"
              disabled={!observation1 || !observation2 ||
                       observation1.processing_status !== 'completed' ||
                       observation2.processing_status !== 'completed'}
            >
              Continue to Change Detection
            </button>
          </div>
        </div>
      )}

      {/* Step 5: Change Detection */}
      {step === 5 && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Play className="w-5 h-5 mr-2" />
            Run Change Detection
          </h2>

          <div className="mb-6">
            <p className="text-gray-600 mb-4">
              Compare the two processed observations to detect changes between time 1 and time 2.
            </p>
            <div className="grid grid-cols-2 gap-4 text-sm mb-4">
              <div>
                <p className="font-medium">Time 1:</p>
                <p className="text-gray-600">{new Date(selectedImage1!.acquisition_date).toLocaleDateString()}</p>
              </div>
              <div>
                <p className="font-medium">Time 2:</p>
                <p className="text-gray-600">{new Date(selectedImage2!.acquisition_date).toLocaleDateString()}</p>
              </div>
            </div>
          </div>

          {changeEvent ? (
            <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="font-medium text-green-800 mb-2">Change Detection Started!</p>
              <p className="text-sm text-green-700">Event ID: {changeEvent.id}</p>
              <p className="text-sm text-green-700">Check the Dashboard for results once processing completes.</p>
            </div>
          ) : (
            <button
              onClick={handleRunChangeDetection}
              className="btn-primary"
              disabled={processing}
            >
              {processing ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Running Change Detection...
                </>
              ) : (
                'Run Change Detection'
              )}
            </button>
          )}

          <div className="flex space-x-4 mt-6">
            <button onClick={() => setStep(4)} className="btn-secondary">
              Back
            </button>
            <button onClick={() => setStep(1)} className="btn-primary">
              New Analysis
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

  // Ensure step number is displayed correctly
  const displayStep = step;

  return (
    <div className="flex flex-col items-center">
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
          isComplete ? 'bg-green-500 text-white' : isCurrent ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-600'
        }`}
      >
        {isComplete ? '✓' : displayStep}
      </div>
      <span className={`text-xs mt-1 ${isCurrent ? 'font-medium' : 'text-gray-500'}`}>{label}</span>
    </div>
  );
};

export default AnalyzeArea;
