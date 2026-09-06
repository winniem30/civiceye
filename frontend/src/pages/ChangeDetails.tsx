import { useParams } from 'react-router-dom';
import { useState, useEffect, useRef } from 'react';
import { changeDetectionService } from '../services/changeDetectionService';
import type { ChangeEvent } from '../types';

const ChangeDetails = () => {
  const { id } = useParams<{ id: string }>();
  const [changeEvent, setChangeEvent] = useState<ChangeEvent | null>(null);
  const [loading, setLoading] = useState(true);
  const [sliderPosition, setSliderPosition] = useState(50);

  useEffect(() => {
    loadChangeEvent();
  }, [id]);

  const loadChangeEvent = async () => {
    try {
      if (id) {
        const event = await changeDetectionService.getChangeEvent(parseInt(id));
        setChangeEvent(event);
      }
    } catch (error) {
      console.error('Failed to load change event:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">Loading change details...</div>
      </div>
    );
  }

  if (!changeEvent) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center text-gray-500">Change event not found</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Change Details #{changeEvent.id}</h1>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Left Column */}
        <div className="space-y-6">
          {/* Before/After Comparison */}
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Before/After Comparison</h2>
            <p className="text-sm text-gray-600 mb-4">Drag the slider to compare before and after images</p>
            <ImageComparisonSlider
              beforeImage={`Image ${changeEvent.image_t1_id}`}
              afterImage={`Image ${changeEvent.image_t2_id}`}
              sliderPosition={sliderPosition}
              onSliderChange={setSliderPosition}
            />
          </div>

          {/* Change Mask */}
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Change Mask</h2>
            <div className="bg-gray-100 h-64 flex items-center justify-center text-gray-400">
              Change mask visualization
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Change Statistics */}
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Change Statistics</h2>
            <div className="space-y-3">
              <StatRow label="Change Area" value={`${changeEvent.change_area.toFixed(2)} px²`} />
              <StatRow label="Change Percentage" value={`${changeEvent.change_percentage.toFixed(2)}%`} />
              <StatRow label="Confidence" value={`${(changeEvent.confidence * 100).toFixed(1)}%`} />
              <StatRow label="First Detected" value={new Date(changeEvent.first_detected).toLocaleString()} />
              <StatRow label="Last Updated" value={new Date(changeEvent.last_updated).toLocaleString()} />
            </div>
          </div>

          {/* Classification */}
          {changeEvent.is_human_induced !== undefined && (
            <div className="card">
              <h2 className="text-xl font-semibold mb-4">Classification</h2>
              <div className="space-y-3">
                <StatRow
                  label="Type"
                  value={changeEvent.is_human_induced ? 'Human-Induced' : 'Natural'}
                />
                {changeEvent.human_confidence && (
                  <StatRow
                    label="Human Confidence"
                    value={`${(changeEvent.human_confidence * 100).toFixed(1)}%`}
                  />
                )}
                {changeEvent.activity_type && (
                  <StatRow
                    label="Activity Type"
                    value={changeEvent.activity_type}
                  />
                )}
                {changeEvent.activity_confidence && (
                  <StatRow
                    label="Activity Confidence"
                    value={`${(changeEvent.activity_confidence * 100).toFixed(1)}%`}
                  />
                )}
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Actions</h2>
            <div className="space-y-3">
              <button className="btn-primary w-full">Generate Report</button>
              <button className="btn-secondary w-full">Start Investigation</button>
              <button className="btn-secondary w-full">Verify Change</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const StatRow = ({ label, value }: { label: string; value: string }) => {
  return (
    <div className="flex justify-between py-2 border-b border-gray-100">
      <span className="text-gray-600">{label}</span>
      <span className="font-medium">{value}</span>
    </div>
  );
};

const ImageComparisonSlider = ({
  beforeImage,
  afterImage,
  sliderPosition,
  onSliderChange,
}: {
  beforeImage: string;
  afterImage: string;
  sliderPosition: number;
  onSliderChange: (position: number) => void;
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  const handleSliderMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = (x / rect.width) * 100;
    onSliderChange(Math.max(0, Math.min(100, percentage)));
  };

  return (
    <div
      ref={containerRef}
      className="relative w-full h-64 bg-gray-100 rounded-lg overflow-hidden cursor-ew-resize"
      onMouseMove={handleSliderMove}
    >
      {/* Before Image (Left) */}
      <div className="absolute inset-0 bg-blue-100 flex items-center justify-center">
        <span className="text-gray-600">{beforeImage}</span>
      </div>

      {/* After Image (Right - clipped) */}
      <div
        className="absolute inset-0 bg-green-100 flex items-center justify-center"
        style={{ clipPath: `inset(0 0 0 ${sliderPosition}%)` }}
      >
        <span className="text-gray-600">{afterImage}</span>
      </div>

      {/* Slider Line */}
      <div
        className="absolute top-0 bottom-0 w-1 bg-white shadow-lg"
        style={{ left: `${sliderPosition}%` }}
      >
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-8 h-8 bg-white rounded-full shadow-lg flex items-center justify-center">
          <div className="w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-600" />
        </div>
      </div>

      {/* Labels */}
      <div className="absolute top-2 left-2 bg-black bg-opacity-50 text-white px-2 py-1 rounded text-xs">
        Before
      </div>
      <div className="absolute top-2 right-2 bg-black bg-opacity-50 text-white px-2 py-1 rounded text-xs">
        After
      </div>
    </div>
  );
};

export default ChangeDetails;
