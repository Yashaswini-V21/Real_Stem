import React, { useState, useEffect, useRef } from 'react';
import { 
  Users, 
  MessageSquare, 
  ShieldCheck, 
  AlertTriangle, 
  XCircle, 
  CheckCircle2, 
  BrainCircuit, 
  Timer,
  Scale,
  Award,
  Vote,
  Search,
  Send,
  UserPlus
} from 'lucide-react';

// --- Types ---

type DebatePhase = 'RECRUITING' | 'RESEARCH' | 'DEBATE' | 'RESULTS';
type ArgumentSide = 'PRO' | 'CON';
type ClaimStability = 'VERIFIED' | 'DISPUTED' | 'FALSE';

interface Participant {
  id: string;
  name: string;
  avatar: string;
  side: ArgumentSide | null;
}

interface Argument {
  id: string;
  author: string;
  side: ArgumentSide;
  text: string;
  timestamp: Date;
  factCheck?: {
    status: ClaimStability;
    reasoning: string;
  };
  score?: {
    logic: number;
    evidence: number;
    fallacies: string[];
  };
}

interface DebateArenaProps {
  topic: string;
  lessonId: number;
}

// --- Component ---

const DebateArena: React.FC<DebateArenaProps> = ({ topic, lessonId }) => {
  const [phase, setPhase] = useState<DebatePhase>('RECRUITING');
  const [proTeam, setProTeam] = useState<Participant[]>([]);
  const [conTeam, setConTeam] = useState<Participant[]>([]);
  const [argumentsList, setArgumentsList] = useState<Argument[]>([]);
  const [currentText, setCurrentText] = useState('');
  const [timeLeft, setTimeLeft] = useState(300); // 5 min for research
  const [viewers, setViewers] = useState(42);
  const [userSide, setUserSide] = useState<ArgumentSide | null>(null);
  
  const scrollRef = useRef<HTMLDivElement>(null);

  // Phase transition simulation (would be WebSocket driven)
  useEffect(() => {
    if (phase === 'RESEARCH' || phase === 'DEBATE') {
      const timer = setInterval(() => {
        setTimeLeft(prev => {
          if (prev <= 1) {
            if (phase === 'RESEARCH') setPhase('DEBATE');
            else setPhase('RESULTS');
            return 180; // Reset for next phase
          }
          return prev - 1;
        });
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [phase]);

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  const handleJoin = (side: ArgumentSide) => {
    setUserSide(side);
    const mockUser = { id: 'me', name: 'You', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Lucky', side };
    if (side === 'PRO') setProTeam([...proTeam, mockUser]);
    else setConTeam([...conTeam, mockUser]);
    
    if (proTeam.length + conTeam.length >= 1) { // Simplified transition
        setTimeout(() => setPhase('RESEARCH'), 1000);
    }
  };

  const submitArgument = () => {
    if (!currentText.trim() || !userSide) return;
    
    const newArg: Argument = {
      id: Date.now().toString(),
      author: 'You',
      side: userSide,
      text: currentText,
      timestamp: new Date(),
      factCheck: {
        status: 'VERIFIED',
        reasoning: 'AI verified claim against recent NASA datasets.'
      },
      score: {
        logic: 8,
        evidence: 9,
        fallacies: []
      }
    };
    
    setArgumentsList([...argumentsList, newArg]);
    setCurrentText('');
    setTimeout(() => {
        scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
    }, 100);
  };

  return (
    <div className="flex flex-col h-[800px] bg-slate-950 rounded-3xl overflow-hidden border border-slate-800 shadow-2xl relative">
      {/* Header HUD */}
      <div className="bg-slate-900 border-b border-white/5 p-6 flex items-center justify-between backdrop-blur-3xl">
        <div className="flex items-center gap-4">
          <div className="bg-indigo-600 p-2.5 rounded-2xl shadow-lg shadow-indigo-500/20">
            <Scale className="text-white" size={24} />
          </div>
          <div>
            <h2 className="text-white font-black text-xl tracking-tighter uppercase leading-none mb-1">Debate Arena Alpha</h2>
            <p className="text-slate-400 text-xs font-bold uppercase tracking-widest">{topic}</p>
          </div>
        </div>
        
        <div className="flex items-center gap-6">
          <div className="text-right sr-only md:not-sr-only">
            <span className="block text-[10px] font-black text-slate-500 uppercase">Live Audience</span>
            <div className="flex items-center gap-2 text-white font-mono font-bold">
              <Users size={14} className="text-indigo-400" /> {viewers}
            </div>
          </div>
          <div className="h-10 w-px bg-white/10" />
          <div className="flex items-center gap-3 bg-white/5 px-4 py-2 rounded-2xl border border-white/10">
            <Timer size={20} className={timeLeft < 60 ? 'text-red-500 animate-pulse' : 'text-indigo-400'} />
            <span className="text-white font-mono text-xl font-bold">{formatTime(timeLeft)}</span>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-grow flex overflow-hidden">
        {/* Teams Sidebars */}
        <div className="w-1/4 border-r border-white/5 p-4 flex flex-col gap-6 bg-slate-900/30">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-blue-400 font-black uppercase text-xs tracking-tighter">Team PRO</h3>
              <span className="text-[10px] bg-blue-500/10 text-blue-400 px-2 rounded-full border border-blue-500/20">Affirmative</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {proTeam.map(p => (
                <img key={p.id} src={p.avatar} alt={p.name} className="w-8 h-8 rounded-full border border-blue-500/30 ring-2 ring-blue-500/10" />
              ))}
              {phase === 'RECRUITING' && !userSide && (
                <button 
                  onClick={() => handleJoin('PRO')}
                  className="w-8 h-8 rounded-full border-2 border-dashed border-slate-700 flex items-center justify-center text-slate-500 hover:border-blue-500 hover:text-blue-500 transition-all"
                >
                  <UserPlus size={14} />
                </button>
              )}
            </div>
          </div>
          
          <div className="flex-grow bg-blue-500/5 rounded-2xl border border-blue-500/10 p-4 relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <Search size={40} className="text-blue-400" />
            </div>
            <h4 className="text-blue-400 text-[10px] font-black uppercase mb-3 tracking-widest">Research Feed</h4>
            {phase === 'RESEARCH' ? (
              <ul className="text-xs text-slate-400 space-y-3 leading-relaxed">
                <li className="p-2 bg-slate-800/40 rounded-lg">Study: High-altitude carbon capture shows 40% efficiency boost.</li>
                <li className="p-2 bg-slate-800/40 rounded-lg">NASA Dataset: 2026 atmospheric trends supporting ion-exchange models.</li>
              </ul>
            ) : (
              <p className="text-[10px] text-slate-600 italic">Phase locked</p>
            )}
          </div>
        </div>

        {/* Debate Thread */}
        <div className="flex-grow flex flex-col bg-slate-950/50 relative">
          <div ref={scrollRef} className="flex-grow overflow-y-auto p-6 space-y-6 scrollbar-hide">
            {argumentsList.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-12">
                {phase === 'RECRUITING' && (
                  <>
                    <Users className="text-slate-800 mb-6" size={64} />
                    <h3 className="text-xl font-bold text-slate-400 mb-2">Awaiting Competitors</h3>
                    <p className="text-slate-600 text-sm max-w-xs">Join a side to begin the research phase of this global STEM debate.</p>
                  </>
                )}
                {phase === 'RESEARCH' && (
                  <>
                    <BrainCircuit className="text-indigo-500/50 mb-6 animate-pulse" size={64} />
                    <h3 className="text-xl font-bold text-slate-400 mb-2">Research Phase Active</h3>
                    <p className="text-slate-600 text-sm max-w-xs">Review the AI-curated evidence in your team's research feed before arguments begin.</p>
                  </>
                )}
              </div>
            ) : (
              argumentsList.map(arg => (
                <div key={arg.id} className={`flex flex-col ${arg.side === 'PRO' ? 'items-start' : 'items-end'}`}>
                  <div className={`max-w-[80%] rounded-2xl p-4 border transition-all ${
                    arg.side === 'PRO' 
                      ? 'bg-blue-600/10 border-blue-600/20 text-blue-50' 
                      : 'bg-red-600/10 border-red-600/20 text-red-50'
                  }`}>
                    <div className="flex items-center gap-2 mb-2">
                       <span className="text-[10px] font-black uppercase tracking-widest opacity-60">{arg.author}</span>
                       <span className="text-[10px] opacity-30 font-mono">{new Date(arg.timestamp).toLocaleTimeString()}</span>
                    </div>
                    <p className="text-sm leading-relaxed mb-4">{arg.text}</p>
                    
                    {/* AI Fact Check Module */}
                    {arg.factCheck && (
                      <div className={`mt-2 p-2 rounded-lg text-[10px] flex items-start gap-2 ${
                        arg.factCheck.status === 'VERIFIED' ? 'bg-green-500/10 text-green-400 border border-green-500/20' :
                        arg.factCheck.status === 'DISPUTED' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                        'bg-red-500/10 text-red-400 border border-red-500/20'
                      }`}>
                        {arg.factCheck.status === 'VERIFIED' ? <ShieldCheck size={14} className="shrink-0" /> :
                         arg.factCheck.status === 'DISPUTED' ? <AlertTriangle size={14} className="shrink-0" /> :
                         <XCircle size={14} className="shrink-0" />}
                        <div>
                          <span className="font-black uppercase tracking-tighter mr-2">AI Fact-Check: {arg.factCheck.status}</span>
                          <span className="opacity-80">{arg.factCheck.reasoning}</span>
                        </div>
                      </div>
                    )}
                  </div>
                  
                  {/* Moderator Evaluation */}
                  {arg.score && phase === 'DEBATE' && (
                    <div className="mt-2 flex gap-3 px-2">
                      <div className="flex items-center gap-1 text-[10px] font-black text-indigo-400 uppercase">
                        <Scale size={10} /> Logic: {arg.score.logic}/10
                      </div>
                      <div className="flex items-center gap-1 text-[10px] font-black text-indigo-400 uppercase">
                        <Vote size={10} /> Evidence: {arg.score.evidence}/10
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>

          {/* Interactive Input HUD */}
          <div className="p-6 bg-slate-900 border-t border-white/5">
            <div className="relative group">
              <textarea 
                value={currentText}
                onChange={(e) => setCurrentText(e.target.value)}
                placeholder={phase === 'DEBATE' ? "Construct your argument with evidence..." : "Debate locked until phase transition..."}
                disabled={phase !== 'DEBATE' || !userSide}
                className="w-full bg-slate-950 border border-white/10 rounded-2xl p-4 pr-16 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500 transition-all resize-none h-24 shadow-inner"
              />
              <button 
                onClick={submitArgument}
                disabled={!currentText.trim() || phase !== 'DEBATE'}
                className="absolute bottom-4 right-4 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-600 p-2.5 rounded-xl text-white transition-all shadow-lg active:scale-95"
              >
                <Send size={20} />
              </button>
            </div>
            <div className="mt-3 flex items-center justify-between text-[10px] uppercase font-black tracking-widest">
                <span className="text-slate-500">Live AI Moderation Enabled</span>
                <span className="text-indigo-400 flex items-center gap-1">
                   {phase === 'DEBATE' && userSide ? `Representing: ${userSide}` : 'Select a team to interact'}
                </span>
            </div>
          </div>
        </div>

        {/* Opponent Sidebar */}
        <div className="w-1/4 border-l border-white/5 p-4 flex flex-col gap-6 bg-slate-900/30 text-right">
          <div className="space-y-4">
             <div className="flex items-center justify-between flex-row-reverse">
              <h3 className="text-red-400 font-black uppercase text-xs tracking-tighter">Team CON</h3>
              <span className="text-[10px] bg-red-500/10 text-red-400 px-2 rounded-full border border-red-500/20">Negative</span>
            </div>
            <div className="flex flex-wrap gap-2 justify-end">
              {conTeam.map(p => (
                <img key={p.id} src={p.avatar} alt={p.name} className="w-8 h-8 rounded-full border border-red-500/30 ring-2 ring-red-500/10" />
              ))}
               {phase === 'RECRUITING' && !userSide && (
                <button 
                  onClick={() => handleJoin('CON')}
                  className="w-8 h-8 rounded-full border-2 border-dashed border-slate-700 flex items-center justify-center text-slate-500 hover:border-red-500 hover:text-red-500 transition-all"
                >
                  <UserPlus size={14} />
                </button>
              )}
            </div>
          </div>

          <div className="flex-grow bg-red-500/5 rounded-2xl border border-red-500/10 p-4 relative overflow-hidden group text-left">
            <div className="absolute top-0 left-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <Search size={40} className="text-red-400" />
            </div>
            <h4 className="text-red-400 text-[10px] font-black uppercase mb-3 tracking-widest">Research Feed</h4>
            {phase === 'RESEARCH' ? (
              <ul className="text-xs text-slate-400 space-y-3 leading-relaxed">
                <li className="p-2 bg-slate-800/40 rounded-lg">Counter-Study: Regional pressure variations negate long-term stability.</li>
                <li className="p-2 bg-slate-800/40 rounded-lg">Cost-Benefit Analysis: Deployment costs 3x higher than reforestation.</li>
              </ul>
            ) : (
              <p className="text-[10px] text-slate-600 italic">Phase locked</p>
            )}
          </div>
        </div>
      </div>

      {/* Results View Modal (Overlay) */}
      {phase === 'RESULTS' && (
        <div className="absolute inset-0 z-50 bg-slate-950/90 backdrop-blur-md flex items-center justify-center p-12">
           <div className="bg-slate-900 border border-white/10 p-12 rounded-[40px] max-w-2xl w-full text-center shadow-2xl">
              <Award className="mx-auto text-amber-500 mb-8" size={80} />
              <h2 className="text-4xl font-black text-white mb-2 uppercase italic">Debate Concluded</h2>
              <p className="text-slate-400 mb-12 uppercase tracking-[0.2em] font-bold text-xs">Final Merit Evaluation</p>
              
              <div className="grid grid-cols-2 gap-8 mb-12">
                 <div className="p-6 bg-blue-600/10 border border-blue-600/20 rounded-3xl">
                    <span className="text-blue-400 text-xs font-black uppercase">Affirmative</span>
                    <div className="text-4xl font-black text-white mt-2">84.2</div>
                 </div>
                 <div className="p-6 bg-red-600/10 border border-red-600/20 rounded-3xl">
                    <span className="text-red-400 text-xs font-black uppercase">Negative</span>
                    <div className="text-4xl font-black text-white mt-2">78.5</div>
                 </div>
              </div>

              <div className="bg-white/5 p-6 rounded-3xl text-left border border-white/10 mb-8">
                 <h4 className="text-indigo-400 text-[10px] font-black uppercase mb-3 flex items-center gap-2">
                    <CheckCircle2 size={12} /> AI Moderator Key Insight
                 </h4>
                 <p className="text-sm text-slate-300 italic">"The Affirmative team provided superior empirical data from the NASA dataset, successfully neutralizing the cost-benefit counter-arguments."</p>
              </div>

              <button 
                onClick={() => setPhase('RECRUITING')}
                className="bg-indigo-600 hover:bg-indigo-500 text-white px-12 py-4 rounded-full font-black uppercase tracking-tighter text-sm transition-all hover:scale-105 active:scale-95"
              >
                Proceed to Dashboard
              </button>
           </div>
        </div>
      )}
    </div>
  );
};

export default DebateArena;
