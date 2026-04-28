import React, { useState, useRef, useEffect } from 'react';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  Volume2, 
  VolumeX, 
  Settings, 
  Maximize, 
  Minimize,
  BookOpen,
  CheckCircle,
  Clock
} from 'lucide-react';

// --- Types ---

interface TranscriptLine {
  id: number;
  startTime: number;
  endTime: number;
  text: string;
}

interface VideoPlayerProps {
  videoUrl: string;
  transcript: TranscriptLine[];
  onComplete?: () => void;
}

// --- Component ---

const VideoPlayer: React.FC<VideoPlayerProps> = ({ videoUrl, transcript, onComplete }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const transcriptScrollRef = useRef<HTMLDivElement>(null);

  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [showControls, setShowControls] = useState(true);
  const [activeLineId, setActiveLineId] = useState<number | null>(null);

  // Auto-scroll transcript and track active line
  useEffect(() => {
    const active = transcript.find(line => currentTime >= line.startTime && currentTime <= line.endTime);
    if (active && active.id !== activeLineId) {
        setActiveLineId(active.id);
        const element = document.getElementById(`transcript-line-${active.id}`);
        if (element && transcriptScrollRef.current) {
            transcriptScrollRef.current.scrollTo({
                top: element.offsetTop - 100,
                behavior: 'smooth'
            });
        }
    }
  }, [currentTime, transcript, activeLineId]);

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) videoRef.current.pause();
      else videoRef.current.play();
      setIsPlaying(!isPlaying);
    }
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      const current = videoRef.current.currentTime;
      const dur = videoRef.current.duration;
      setCurrentTime(current);
      setProgress((current / dur) * 100);
      
      if (current >= dur && onComplete) onComplete();
    }
  };

  const handleLoadedMetadata = () => {
    if (videoRef.current) setDuration(videoRef.current.duration);
  };

  const seek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value);
    if (videoRef.current) {
      const time = (val / 100) * duration;
      videoRef.current.currentTime = time;
      setProgress(val);
    }
  };

  const formatTime = (time: number) => {
    const m = Math.floor(time / 60);
    const s = Math.floor(time % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  const toggleFullscreen = () => {
    if (!isFullscreen) {
      containerRef.current?.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
    setIsFullscreen(!isFullscreen);
  };

  const jumpToLine = (time: number) => {
    if (videoRef.current) {
        videoRef.current.currentTime = time;
        videoRef.current.play();
        setIsPlaying(true);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full max-h-[700px]">
      {/* Video Side */}
      <div className="lg:col-span-2 flex flex-col gap-4">
        <div 
          ref={containerRef}
          className="relative group bg-black rounded-3xl overflow-hidden shadow-2xl aspect-video border border-white/10"
          onMouseMove={() => { setShowControls(true); }}
          onMouseLeave={() => { if (isPlaying) setShowControls(false); }}
        >
          <video
            ref={videoRef}
            src={videoUrl}
            className="w-full h-full cursor-pointer"
            onClick={togglePlay}
            onTimeUpdate={handleTimeUpdate}
            onLoadedMetadata={handleLoadedMetadata}
          />

          {/* Overlay UI */}
          <div className={`absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent transition-opacity duration-300 flex flex-col justify-end p-6 ${showControls ? 'opacity-100' : 'opacity-0'}`}>
            {/* Progress Bar */}
            <div className="relative w-full mb-6 group/progress">
              <input
                type="range"
                min="0"
                max="100"
                step="0.1"
                value={progress}
                onChange={seek}
                className="w-full h-1.5 bg-white/20 rounded-full appearance-none cursor-pointer accent-indigo-500 hover:h-2 transition-all"
              />
              <div 
                className="absolute left-0 top-0 h-1.5 bg-indigo-500 rounded-full pointer-events-none" 
                style={{ width: `${progress}%` }}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-6">
                <button onClick={togglePlay} className="text-white hover:scale-110 transition-transform">
                  {isPlaying ? <Pause size={28} fill="currentColor" /> : <Play size={28} fill="currentColor" />}
                </button>
                <button onClick={() => videoRef.current && (videoRef.current.currentTime -= 10)} className="text-white/80 hover:text-white">
                  <RotateCcw size={22} />
                </button>
                <div className="flex items-center gap-3 group/vol">
                  <button onClick={() => setIsMuted(!isMuted)} className="text-white/80 hover:text-white">
                    {isMuted || volume === 0 ? <VolumeX size={22} /> : <Volume2 size={22} />}
                  </button>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={isMuted ? 0 : volume}
                    onChange={(e) => setVolume(parseFloat(e.target.value))}
                    className="w-0 group-hover/vol:w-20 transition-all duration-300 h-1 appearance-none bg-white/20 rounded-full accent-white"
                  />
                </div>
                <div className="text-white/80 font-mono text-xs">
                  {formatTime(currentTime)} / {formatTime(duration)}
                </div>
              </div>

              <div className="flex items-center gap-4">
                <button className="text-white/80 hover:text-white"><Settings size={20} /></button>
                <button onClick={toggleFullscreen} className="text-white/80 hover:text-white">
                  {isFullscreen ? <Minimize size={20} /> : <Maximize size={20} />}
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div className="flex items-center justify-between bg-slate-900/50 p-4 rounded-2xl border border-white/5">
            <div className="flex items-center gap-3">
                <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">Quality: 4K Ultra HD</span>
            </div>
            <div className="flex gap-2">
                <span className="px-3 py-1 bg-indigo-500/10 text-indigo-400 rounded-full text-[10px] font-black uppercase border border-indigo-500/20">Stem Accredited</span>
                <span className="px-3 py-1 bg-white/5 text-slate-400 rounded-full text-[10px] font-black uppercase border border-white/10">English CC</span>
            </div>
        </div>
      </div>

      {/* Transcript Side */}
      <div className="flex flex-col bg-slate-950 rounded-3xl border border-white/10 overflow-hidden shadow-xl">
        <div className="p-5 border-b border-white/5 bg-slate-900/50 flex items-center justify-between">
            <div className="flex items-center gap-2">
                <BookOpen size={18} className="text-indigo-400" />
                <h3 className="text-white font-bold text-sm uppercase tracking-tight">Interactive Transcript</h3>
            </div>
            <CheckCircle size={16} className="text-slate-600" />
        </div>

        <div 
            ref={transcriptScrollRef}
            className="flex-grow overflow-y-auto p-4 space-y-4 scrollbar-hide bg-gradient-to-b from-transparent to-slate-950/50"
        >
            {transcript.map((line) => (
                <div 
                    key={line.id}
                    id={`transcript-line-${line.id}`}
                    onClick={() => jumpToLine(line.startTime)}
                    className={`p-3 rounded-2xl transition-all cursor-pointer border ${
                        activeLineId === line.id 
                        ? 'bg-indigo-600/10 border-indigo-600/30 text-white' 
                        : 'border-transparent text-slate-500 hover:text-slate-300'
                    }`}
                >
                    <div className="flex items-center gap-2 mb-1">
                        <Clock size={10} className={activeLineId === line.id ? 'text-indigo-400' : 'text-slate-700'} />
                        <span className="text-[10px] font-mono opacity-50">{formatTime(line.startTime)}</span>
                    </div>
                    <p className={`text-sm leading-relaxed ${activeLineId === line.id ? 'font-medium' : 'font-normal'}`}>
                        {line.text}
                    </p>
                </div>
            ))}
        </div>

        <div className="p-4 bg-slate-900/80 border-t border-white/5">
            <button className="w-full py-3 bg-white/5 hover:bg-white/10 text-white rounded-xl text-xs font-black uppercase tracking-widest transition-all border border-white/10">
                Download Study Notes
            </button>
        </div>
      </div>
    </div>
  );
};

export default VideoPlayer;
