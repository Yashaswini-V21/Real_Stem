import React, { useState, useEffect } from 'react';
import { 
  Play, 
  Gamepad2, 
  BookOpen, 
  Pickaxe, 
  Trophy, 
  Briefcase,
  CheckCircle2,
  Download,
  RotateCcw,
  Share2,
  ArrowRight,
  Star,
  Users,
  Timer,
  Scale
} from 'lucide-react';
import { Lesson } from '../types/lesson';
import VideoPlayer from './VideoPlayer';
import Simulation from './Simulation';
import DebateArena from './DebateArena';

// --- Types ---

type AcademicLevel = 'elementary' | 'middle' | 'high' | 'advanced' | 'college';
type TabId = 'video' | 'simulation' | 'debate' | 'learn' | 'projects' | 'challenge' | 'careers';

interface LessonViewerProps {
  lesson: Lesson;
}

// --- Components ---

const ProgressBar: React.FC<{ progress: number }> = ({ progress }) => (
  <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
    <div 
      className="bg-indigo-600 h-full transition-all duration-500" 
      style={{ width: `${progress}%` }} 
    />
  </div>
);

const LessonViewer: React.FC<LessonViewerProps> = ({ lesson }) => {
  const [activeLevel, setActiveLevel] = useState<AcademicLevel>('high');
  const [activeTab, setActiveTab] = useState<TabId>('video');
  const [completedSections, setCompletedSections] = useState<Set<string>>(new Set());
  const [timeSpent, setTimeSpent] = useState(0);

  // Timer logic
  useEffect(() => {
    const timer = setInterval(() => setTimeSpent(prev => prev + 1), 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const levels: { id: AcademicLevel; label: string }[] = [
    { id: 'elementary', label: 'Elementary' },
    { id: 'middle', label: 'Middle School' },
    { id: 'high', label: 'High School' },
    { id: 'advanced', label: 'Advanced' },
    { id: 'college', label: 'College' }
  ];

  const tabs: { id: TabId; label: string; icon: React.ReactNode }[] = [
    { id: 'video', label: 'Video', icon: <Play size={18} /> },
    { id: 'simulation', label: 'Simulation', icon: <Gamepad2 size={18} /> },
    { id: 'debate', label: 'Arena', icon: <Scale size={18} /> },
    { id: 'learn', label: 'Learn', icon: <BookOpen size={18} /> },
    { id: 'projects', label: 'Projects', icon: <Pickaxe size={18} /> },
    { id: 'challenge', label: 'Challenge', icon: <Trophy size={18} /> },
    { id: 'careers', label: 'Careers', icon: <Briefcase size={18} /> },
  ];

  // Mock data for new components
  const mockTranscript = [
    { id: 1, startTime: 0, endTime: 12, text: "Introduction to atmospheric pressure and its role in modern climate engineering." },
    { id: 2, startTime: 13, endTime: 25, text: "Wait, isn't that just a fancy way of saying cloud seeding? Not quite, let's look at the chemistry." },
    { id: 3, startTime: 26, endTime: 45, text: "By injecting silver iodide into sub-zero clouds, we accelerate the formation of ice crystals." }
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'video':
        return (
          <div className="bg-white rounded-3xl p-2 h-full min-h-[600px]">
            <VideoPlayer 
              videoUrl="https://example.com/mock-video.mp4" 
              transcript={mockTranscript}
              onComplete={() => setCompletedSections(prev => new Set(prev).add('video'))}
            />
          </div>
        );
      case 'debate':
        return <DebateArena topic={lesson.title} lessonId={lesson.id} />;
      case 'simulation':
        return (
          <div className="bg-white rounded-3xl p-4 border border-slate-200 h-[700px]">
            <Simulation 
              simulationUrl="https://example-sim.com/pathway"
              parameters={[{ name: 'Inflow', min: 0, max: 100, unit: 'L/s', defaultValue: 50 }]}
              onComplete={() => setCompletedSections(prev => new Set(prev).add('simulation'))}
            />
          </div>
        );
      default:
        return (
          <div className="bg-white rounded-3xl p-12 border border-slate-200 flex flex-col items-center justify-center text-center">
            <BookOpen size={48} className="text-slate-300 mb-4" />
            <h3 className="text-xl font-bold text-slate-900 mb-2">Content Loading</h3>
            <p className="text-slate-500 max-w-sm">This module is currently being optimized for the {activeLevel} level. Please check back shortly.</p>
          </div>
        );
    }
  };

  const progress = (completedSections.size / tabs.length) * 100;

  return (
    <div className="max-w-6xl mx-auto px-4 py-6 bg-slate-50 min-h-screen">
      {/* Header Section */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 mb-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="bg-indigo-100 text-indigo-700 text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider">
                {lesson.topic}
              </span>
              <div className="flex items-center gap-1 text-slate-500 text-xs font-medium">
                <Timer size={14} />
                {formatTime(timeSpent)}
              </div>
            </div>
            <h1 className="text-3xl font-black text-slate-900 leading-tight">
              {lesson.title}
            </h1>
          </div>
          <div className="flex items-center gap-2">
            <button className="p-2 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors">
              <Share2 size={20} className="text-slate-600" />
            </button>
            <button className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-bold transition-all shadow-sm">
              <CheckCircle2 size={18} />
              Mark Complete
            </button>
          </div>
        </div>

        {/* Level Selector */}
        <div className="flex flex-wrap gap-2 p-1 bg-slate-100 rounded-xl w-fit">
          {levels.map(level => (
            <button
              key={level.id}
              onClick={() => setActiveLevel(level.id)}
              className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${
                activeLevel === level.id 
                  ? 'bg-white text-indigo-600 shadow-sm' 
                  : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              {level.label}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Navigation Sidebar */}
        <div className="lg:col-span-1 space-y-4">
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="p-4 border-b border-slate-100">
              <h3 className="font-bold text-slate-900 flex items-center gap-2">
                Your Progress
                <span className="text-xs font-normal text-slate-500 ml-auto">{Math.round(progress)}%</span>
              </h3>
              <div className="mt-3">
                <ProgressBar progress={progress} />
              </div>
            </div>
            <nav className="p-2">
              {tabs.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all mb-1 ${
                    activeTab === tab.id 
                      ? 'bg-indigo-50 text-indigo-600' 
                      : 'text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  <span className={activeTab === tab.id ? 'text-indigo-600' : 'text-slate-400'}>
                    {tab.icon}
                  </span>
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="lg:col-span-3 space-y-6">
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8 min-h-[600px]">
            {activeTab === 'video' && (
              <div className="space-y-6">
                <div className="aspect-video bg-black rounded-xl border border-slate-800 flex items-center justify-center">
                  <Play size={64} className="text-slate-700 opacity-20" />
                </div>
                <div className="flex items-center justify-between">
                  <h3 className="text-xl font-bold text-slate-900">Transcript</h3>
                  <button className="flex items-center gap-2 text-indigo-600 font-bold text-sm hover:underline">
                    <Download size={16} /> Download .pdf
                  </button>
                </div>
                <div className="prose prose-slate max-w-none text-slate-600 leading-relaxed bg-slate-50 p-6 rounded-xl border border-slate-100">
                   <p className="italic text-slate-400">[00:00] Scientist: "To understand how the CRISPR mechanism works, we first need to look at..."</p>
                   <p className="mt-4">The core principle involves a guide RNA and the Cas9 enzyme which acts like molecular scissors...</p>
                </div>
              </div>
            )}

            {activeTab === 'simulation' && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h3 className="text-xl font-bold text-slate-900">Interactive Lab</h3>
                  <button className="flex items-center gap-2 bg-slate-100 hover:bg-slate-200 text-slate-600 px-3 py-1.5 rounded-lg text-sm font-bold transition-colors">
                    <RotateCcw size={16} /> Reset Lab
                  </button>
                </div>
                <div className="aspect-video bg-slate-900 rounded-xl flex items-center justify-center">
                  <p className="text-slate-500 font-medium">STEM Simulation Environment...</p>
                </div>
              </div>
            )}

            {activeTab === 'learn' && (
              <div className="space-y-8">
                <div className="prose prose-slate lg:prose-lg max-w-none">
                  <h2 className="text-2xl font-black text-slate-900 mb-6">Expert Briefing</h2>
                  <div className="text-slate-600 leading-loose space-y-4">
                    <p>{lesson.content || "Expert content loading from Real-STEM AI..."}</p>
                    <div className="bg-indigo-50 border-l-4 border-indigo-600 p-6 my-8 rounded-r-xl">
                      <h4 className="text-indigo-900 font-bold mb-2 flex items-center gap-2">
                        <Star size={18} fill="currentColor" /> Core Concept: Reaction Catalysis
                      </h4>
                      <p className="text-indigo-800 text-sm">A catalyst increases the reaction rate by lowering the activation energy through an alternative pathway.</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'projects' && (
              <div className="space-y-8">
                <div className="bg-slate-900 rounded-2xl p-8 text-white">
                  <h3 className="text-2xl font-black mb-2 uppercase tracking-tight">Citizen Scientist Project</h3>
                  <p className="text-slate-300 mb-6 max-w-xl">Build your own atmospheric sensor to participate in our global climate dataset.</p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   {['Arduino Uno', 'DHT22 Sensor'].map(item => (
                      <div key={item} className="p-3 bg-slate-50 rounded-lg border border-slate-100 font-medium text-slate-700">
                        • {item}
                      </div>
                   ))}
                </div>
                <button className="bg-indigo-600 text-white font-bold py-3 px-6 rounded-xl shadow-lg">
                  Upload Submission
                </button>
              </div>
            )}

            {activeTab === 'challenge' && (
              <div className="space-y-8 text-center scroll-py-8">
                  <Trophy size={48} className="mx-auto text-amber-500" />
                  <h2 className="text-3xl font-black text-slate-900">The Global Carbon Race</h2>
                  <p className="text-slate-600 mb-8 max-w-lg mx-auto">Compete with students globally to design the most efficient sequestration model.</p>
                  <button className="bg-slate-900 text-white px-8 py-3 rounded-xl font-bold flex items-center gap-2 mx-auto">
                    <Users size={20} /> Join Official Team
                  </button>
              </div>
            )}

            {activeTab === 'careers' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[
                  { title: 'Genetic Architect', salary: '$145k+' },
                  { title: 'Sustainability Auditor', salary: '$92k+' }
                ].map(career => (
                  <div key={career.title} className="bg-white border-2 border-slate-100 p-6 rounded-2xl hover:border-indigo-600 transition-all cursor-pointer group">
                    <h4 className="text-lg font-bold text-slate-900 mb-2">{career.title}</h4>
                    <p className="text-slate-500 text-sm mb-4 font-bold">{career.salary} Avg. Salary</p>
                    <button className="w-full flex items-center justify-center gap-2 bg-slate-50 text-slate-800 font-bold py-2 rounded-lg text-sm group-hover:bg-indigo-600 group-hover:text-white transition-all">
                      "Try It" <ArrowRight size={14} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Rating Widget */}
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
              <div>
                <h4 className="font-bold text-slate-900 mb-1">Rate this Lesson</h4>
                <p className="text-sm text-slate-500">How would you grade this content's alignment with STEM standards?</p>
              </div>
              <div className="flex items-center gap-1">
                {[1, 2, 3, 4, 5].map(star => (
                  <Star 
                    key={star}
                    size={28} 
                    className={`${rating >= star ? 'text-amber-400 fill-amber-400' : 'text-slate-200'} cursor-pointer hover:scale-110 transition-transform`}
                    onClick={() => setRating(star)}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LessonViewer;

