import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  Settings, 
  Play, 
  Pause, 
  RotateCcw, 
  Camera, 
  Info, 
  ChevronDown, 
  ChevronUp,
  RefreshCw,
  CheckCircle2,
  Maximize2
} from 'lucide-react';

// --- Types ---

export interface SimulationParam {
  id: string;
  label: string;
  type: 'number' | 'boolean' | 'select';
  value: any;
  min?: number;
  max?: number;
  step?: number;
  options?: { label: string; value: any }[];
  default: any;
}

interface SimulationProps {
  simulationUrl: string;
  type: 'physics' | 'chemistry' | 'biology' | 'math';
  parameters?: SimulationParam[];
  onComplete?: () => void;
}

// --- Component ---

const Simulation: React.FC<SimulationProps> = ({ 
  simulationUrl, 
  type, 
  parameters: initialParams = [], 
  onComplete 
}) => {
  const [params, setParams] = useState<SimulationParam[]>(initialParams);
  const [isPlaying, setIsPlaying] = useState(true);
  const [showInstructions, setShowInstructions] = useState(true);
  const [isCompleted, setIsCompleted] = useState(false);
  const [touchedParams, setTouchedParams] = useState<Set<string>>(new Set());
  const iframeRef = useRef<HTMLIFrameElement>(null);

  // Sync parameters with iframe
  const sendToIframe = useCallback((data: any) => {
    if (iframeRef.current?.contentWindow) {
      iframeRef.current.contentWindow.postMessage(data, '*');
    }
  }, []);

  const handleParamChange = (id: string, value: any) => {
    setParams(prev => prev.map(p => p.id === id ? { ...p, value } : p));
    setTouchedParams(prev => new Set(prev).add(id));
    sendToIframe({ type: 'UPDATE_PARAM', id, value });
  };

  const handleReset = () => {
    const resetParams = params.map(p => ({ ...p, value: p.default }));
    setParams(resetParams);
    setTouchedParams(new Set());
    sendToIframe({ type: 'RESET' });
  };

  const togglePlayback = () => {
    setIsPlaying(!isPlaying);
    sendToIframe({ type: isPlaying ? 'PAUSE' : 'PLAY' });
  };

  const captureScreenshot = () => {
    sendToIframe({ type: 'CAPTURE_SCREENSHOT' });
    // In a real app, the iframe would send back a data URL via message
    alert('Screenshot captured and saved to your project gallery!');
  };

  // Track completion
  useEffect(() => {
    if (!isCompleted && touchedParams.size === params.length && params.length > 0) {
      setIsCompleted(true);
      if (onComplete) onComplete();
    }
  }, [touchedParams, params.length, isCompleted, onComplete]);

  return (
    <div className="flex flex-col lg:flex-row gap-6 bg-slate-50 p-4 rounded-3xl min-h-[600px]">
      {/* Simulation Main Area */}
      <div className="flex-grow flex flex-col gap-4">
        <div className="relative aspect-video bg-slate-900 rounded-2xl overflow-hidden shadow-2xl border border-slate-800">
          <iframe
            ref={iframeRef}
            src={simulationUrl}
            className="w-full h-full border-none"
            title={`STEM Simulation: ${type}`}
            sandbox="allow-scripts allow-same-origin"
          />
          
          {/* Simulation Overlay HUD */}
          <div className="absolute top-4 left-4 flex gap-2">
            <div className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest flex items-center gap-2 backdrop-blur-md border border-white/20 ${
              type === 'physics' ? 'bg-blue-500/80 text-white' : 
              type === 'chemistry' ? 'bg-purple-500/80 text-white' : 
              'bg-green-500/80 text-white'
            }`}>
              <div className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
              {type} Lab
            </div>
            {isCompleted && (
              <div className="bg-green-500/90 text-white px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest flex items-center gap-2 backdrop-blur-md border border-white/20">
                <CheckCircle2 size={12} /> Experiment Recorded
              </div>
            )}
          </div>

          {/* Quick HUD Controls */}
          <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-slate-900/80 backdrop-blur-xl border border-slate-700/50 p-2 rounded-2xl flex items-center gap-4 shadow-2xl">
            <button 
              onClick={togglePlayback}
              className="w-10 h-10 flex items-center justify-center bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl transition-all hover:scale-105 active:scale-95"
            >
              {isPlaying ? <Pause size={20} fill="currentColor" /> : <Play size={20} fill="currentColor" className="ml-0.5" />}
            </button>
            <div className="h-6 w-px bg-slate-700" />
            <button 
              onClick={handleReset}
              className="text-slate-400 hover:text-white transition-colors p-2"
              title="Reset Simulation"
            >
              <RotateCcw size={20} />
            </button>
            <button 
              onClick={captureScreenshot}
              className="text-slate-400 hover:text-white transition-colors p-2"
              title="Capture Observation"
            >
              <Camera size={20} />
            </button>
            <button className="text-slate-400 hover:text-white transition-colors p-2">
              <Maximize2 size={18} />
            </button>
          </div>
        </div>

        {/* Instructions Panel */}
        <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden transition-all shadow-sm">
          <button 
            onClick={() => setShowInstructions(!showInstructions)}
            className="w-full px-6 py-4 flex items-center justify-between hover:bg-slate-50 transition-colors"
          >
            <div className="flex items-center gap-3 text-slate-900 font-bold">
              <div className="p-1.5 bg-indigo-100 text-indigo-600 rounded-lg">
                <Info size={18} />
              </div>
              Learning Objectives & Instructions
            </div>
            {showInstructions ? <ChevronUp size={20} className="text-slate-400" /> : <ChevronDown size={20} className="text-slate-400" />}
          </button>
          {showInstructions && (
            <div className="px-6 pb-6 text-slate-600 text-sm leading-relaxed border-t border-slate-100 mt-0 pt-4">
              <p className="mb-4">In this simulation, you will explore the relationship between catalyst concentration and reaction surface area. Your goal is to achieve an efficient 95% yield without causing thermal runaway.</p>
              <ul className="space-y-2 list-disc pl-4">
                <li>Adjust the <strong>Temperature</strong> to 325K to initialize the baseline.</li>
                <li>Slowly increment the <strong>Catalyst Flow</strong> while monitoring the byproduct pressure.</li>
                <li>Use the <strong>Camera</strong> icon to record your peak efficiency for the final report.</li>
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Control Panel Sidebar */}
      <div className="w-full lg:w-80 flex flex-col gap-4">
        <div className="bg-slate-900 text-white p-6 rounded-3xl shadow-xl flex flex-col h-full border border-slate-800">
          <div className="flex items-center gap-3 mb-8">
            <div className="p-2 bg-indigo-600/20 text-indigo-400 rounded-xl">
              <Settings size={20} />
            </div>
            <h3 className="font-black uppercase tracking-tighter text-lg">Lab Controls</h3>
          </div>

          <div className="space-y-8 flex-grow">
            {params.map(param => (
              <div key={param.id} className="space-y-3">
                <div className="flex justify-between items-center px-1">
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-widest">{param.label}</label>
                  {param.type === 'number' && (
                    <span className="text-xs font-mono bg-slate-800 px-2 py-0.5 rounded text-indigo-400 font-bold">
                      {param.value}{param.id === 'temp' ? 'K' : ''}
                    </span>
                  )}
                </div>

                {param.type === 'number' && (
                  <input
                    type="range"
                    min={param.min}
                    max={param.max}
                    step={param.step}
                    value={param.value}
                    onChange={(e) => handleParamChange(param.id, parseFloat(e.target.value))}
                    className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                  />
                )}

                {param.type === 'boolean' && (
                  <button
                    onClick={() => handleParamChange(param.id, !param.value)}
                    className={`w-full p-3 rounded-xl flex items-center justify-between transition-all border ${
                      param.value 
                        ? 'bg-indigo-600/10 border-indigo-600/50 text-indigo-400' 
                        : 'bg-slate-800/50 border-slate-700 text-slate-500 hover:text-slate-400'
                    }`}
                  >
                    <span className="text-sm font-bold">{param.value ? 'Enabled' : 'Disabled'}</span>
                    <div className={`w-8 h-4 rounded-full p-1 transition-colors ${param.value ? 'bg-indigo-500' : 'bg-slate-700'}`}>
                      <div className={`w-2 h-2 bg-white rounded-full transition-transform ${param.value ? 'translate-x-4' : 'translate-x-0'}`} />
                    </div>
                  </button>
                )}

                {param.type === 'select' && (
                  <select
                    value={param.value}
                    onChange={(e) => handleParamChange(param.id, e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 text-slate-300 p-3 rounded-xl text-sm font-bold focus:outline-none focus:border-indigo-500"
                  >
                    {param.options?.map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                )}
              </div>
            ))}
          </div>

          <div className="mt-12 space-y-3 pt-6 border-t border-slate-800">
            {isCompleted ? (
              <button 
                onClick={() => {
                  handleReset();
                  setIsCompleted(false);
                }}
                className="w-full bg-slate-800 hover:bg-slate-700 text-white font-bold py-4 rounded-2xl transition-all flex items-center justify-center gap-3 active:scale-95"
              >
                <RefreshCw size={20} />
                Try Again
              </button>
            ) : (
              <div className="p-4 bg-indigo-600/5 rounded-2xl border border-indigo-500/20 text-center">
                <p className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest mb-2">Completion Progress</p>
                <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
                  <div 
                    className="bg-indigo-500 h-full transition-all duration-500" 
                    style={{ width: `${(touchedParams.size / params.length) * 100}%` }} 
                  />
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Simulation;
