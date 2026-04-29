import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Globe,
  Users,
  Video,
  MessageSquare,
  FileText,
  Upload,
  CheckCircle2,
  Trophy,
  MapPin,
  Clock,
  Plus,
  LogIn,
  Send,
  Phone,
  Settings,
  Share2,
  Download,
  Eye,
  Star,
  TrendingUp,
  Paperclip,
  X,
  Calendar
} from 'lucide-react';

// --- Types ---

type ChallengeStatus = 'recruiting' | 'in-progress' | 'judging' | 'completed';
type UserRole = 'member' | 'team-lead' | 'judge' | 'organizer';
type LanguageCode = 'en' | 'es' | 'fr' | 'de' | 'zh' | 'ja' | 'ar' | 'pt';

interface Challenge {
  id: string;
  title: string;
  description: string;
  startDate: Date;
  endDate: Date;
  countries: string[];
  status: ChallengeStatus;
  teamsRegistered: number;
  maxTeams: number;
}

interface TeamMember {
  id: string;
  name: string;
  country: string;
  role: UserRole;
  avatar: string;
  status: 'online' | 'offline';
  lastSeen: Date;
}

interface Team {
  id: string;
  name: string;
  country: string;
  members: TeamMember[];
  challengeId: string;
  openings: number;
  score?: number;
  submissionStatus: 'pending' | 'submitted' | 'evaluated';
}

interface ChatMessage {
  id: string;
  sender: TeamMember;
  text: string;
  timestamp: Date;
  language: LanguageCode;
  translatedText?: string;
}

interface Milestone {
  id: string;
  title: string;
  description: string;
  dueDate: Date;
  completed: boolean;
  assignee?: TeamMember;
}

interface Submission {
  id: string;
  teamId: string;
  projectFile: string;
  videoPresentation: string;
  writtenReport: string;
  submittedAt: Date;
  score?: number;
  feedback?: string;
}

interface LeaderboardEntry {
  rank: number;
  teamId: string;
  teamName: string;
  country: string;
  score: number;
  members: number;
  status: 'pending' | 'submitted' | 'evaluated';
}

interface GlobalCollaborationProps {
  challengeId: string;
  currentUserId: string;
  currentUserTeam?: Team;
}

// --- Subcomponents ---

const ChallengeOverview: React.FC<{ challenge: Challenge }> = ({ challenge }) => {
  const progress = Math.round((new Date().getTime() - challenge.startDate.getTime()) / 
    (challenge.endDate.getTime() - challenge.startDate.getTime()) * 100);

  return (
    <div className="bg-white rounded-3xl border border-slate-200 p-8 shadow-sm">
      <div className="mb-6">
        <h2 className="text-3xl font-black text-slate-900 mb-2">{challenge.title}</h2>
        <p className="text-slate-600 text-lg">{challenge.description}</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-slate-50 p-4 rounded-2xl">
          <p className="text-xs text-slate-500 font-bold uppercase">Teams Registered</p>
          <p className="text-2xl font-black text-indigo-600 mt-1">{challenge.teamsRegistered}/{challenge.maxTeams}</p>
        </div>
        <div className="bg-slate-50 p-4 rounded-2xl">
          <p className="text-xs text-slate-500 font-bold uppercase">Status</p>
          <p className="text-sm font-black text-slate-900 mt-1 capitalize">{challenge.status}</p>
        </div>
        <div className="bg-slate-50 p-4 rounded-2xl">
          <p className="text-xs text-slate-500 font-bold uppercase">Start</p>
          <p className="text-sm font-black text-slate-900 mt-1">{challenge.startDate.toLocaleDateString()}</p>
        </div>
        <div className="bg-slate-50 p-4 rounded-2xl">
          <p className="text-xs text-slate-500 font-bold uppercase">End</p>
          <p className="text-sm font-black text-slate-900 mt-1">{challenge.endDate.toLocaleDateString()}</p>
        </div>
      </div>

      {/* Simple world map visualization with participating countries */}
      <div className="bg-slate-50 rounded-2xl p-6">
        <h3 className="font-bold text-slate-900 mb-3 flex items-center gap-2">
          <Globe size={20} className="text-indigo-600" />
          Participating Regions
        </h3>
        <div className="flex flex-wrap gap-2">
          {challenge.countries.map(country => (
            <span key={country} className="bg-indigo-100 text-indigo-700 px-3 py-1 rounded-full text-sm font-bold">
              {country}
            </span>
          ))}
        </div>
      </div>

      {/* Progress bar */}
      <div className="mt-6">
        <div className="flex justify-between items-center mb-2">
          <p className="text-xs font-bold text-slate-600 uppercase">Challenge Progress</p>
          <p className="text-xs font-black text-indigo-600">{Math.max(0, Math.min(100, progress))}%</p>
        </div>
        <div className="w-full bg-slate-200 h-3 rounded-full overflow-hidden">
          <div 
            className="bg-indigo-600 h-full transition-all duration-500" 
            style={{ width: `${Math.max(0, Math.min(100, progress))}%` }}
          />
        </div>
      </div>
    </div>
  );
};

const TeamBrowser: React.FC<{ teams: Team[]; onJoin: (teamId: string) => void }> = ({ teams, onJoin }) => {
  const [filter, setFilter] = useState<string>('all');

  const filteredTeams = useMemo(() => {
    return teams.filter(t => filter === 'all' || t.country === filter);
  }, [teams, filter]);

  return (
    <div className="bg-white rounded-3xl border border-slate-200 p-8 shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-black text-slate-900 flex items-center gap-2">
          <Users className="text-indigo-600" /> Team Browser
        </h2>
        <select 
          value={filter} 
          onChange={(e) => setFilter(e.target.value)}
          className="px-4 py-2 border border-slate-300 rounded-xl font-bold text-slate-700"
        >
          <option value="all">All Countries</option>
          {Array.from(new Set(teams.map(t => t.country))).map(country => (
            <option key={country} value={country}>{country}</option>
          ))}
        </select>
      </div>

      <div className="space-y-3">
        {filteredTeams.map(team => (
          <div key={team.id} className="bg-slate-50 p-4 rounded-2xl border border-slate-200 flex items-center justify-between">
            <div className="flex-1">
              <h3 className="font-black text-slate-900">{team.name}</h3>
              <div className="flex items-center gap-4 mt-2 text-sm">
                <span className="flex items-center gap-1 text-slate-600">
                  <MapPin size={16} /> {team.country}
                </span>
                <span className="flex items-center gap-1 text-slate-600">
                  <Users size={16} /> {team.members.length} members
                </span>
                <span className="bg-amber-100 text-amber-700 font-bold px-2 py-1 rounded">
                  {team.openings} opening{team.openings !== 1 ? 's' : ''}
                </span>
              </div>
            </div>
            {team.openings > 0 && (
              <button 
                onClick={() => onJoin(team.id)}
                className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-bold transition-all"
              >
                <LogIn size={18} /> Join
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

const TeamWorkspace: React.FC<{ team: Team; messages: ChatMessage[] }> = ({ team, messages }) => {
  const [newMessage, setNewMessage] = useState('');
  const [showTranslation, setShowTranslation] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState<LanguageCode>('en');

  const handleSendMessage = useCallback(() => {
    if (newMessage.trim()) {
      // Emit WebSocket message
      setNewMessage('');
    }
  }, [newMessage]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Team Members */}
      <div className="bg-white rounded-3xl border border-slate-200 p-6 shadow-sm">
        <h3 className="text-xl font-black text-slate-900 mb-4 flex items-center gap-2">
          <Users className="text-indigo-600" /> Team Members
        </h3>
        <div className="space-y-3">
          {team.members.map(member => (
            <div key={member.id} className="flex items-center gap-3">
              <div className="relative">
                <img src={member.avatar} alt={member.name} className="w-10 h-10 rounded-full" />
                <div className={`absolute bottom-0 right-0 w-3 h-3 rounded-full ${
                  member.status === 'online' ? 'bg-green-500' : 'bg-slate-300'
                }`} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-bold text-slate-900 truncate">{member.name}</p>
                <p className="text-xs text-slate-500">{member.role}</p>
              </div>
              <span className="text-xs font-bold bg-indigo-100 text-indigo-700 px-2 py-1 rounded">
                {member.country}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Chat & Workspace */}
      <div className="lg:col-span-2 bg-white rounded-3xl border border-slate-200 p-6 shadow-sm flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-black text-slate-900 flex items-center gap-2">
            <MessageSquare className="text-indigo-600" /> Discussion Board
          </h3>
          <div className="flex items-center gap-2">
            <button 
              onClick={() => setShowTranslation(!showTranslation)}
              className={`px-3 py-1 rounded-lg font-bold text-sm transition-all ${
                showTranslation 
                  ? 'bg-indigo-600 text-white' 
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              Translate
            </button>
            <select 
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value as LanguageCode)}
              className="px-2 py-1 border border-slate-300 rounded-lg text-sm font-bold"
            >
              <option value="en">English</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
              <option value="de">German</option>
              <option value="zh">Chinese</option>
              <option value="ja">Japanese</option>
            </select>
          </div>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto space-y-3 mb-4 bg-slate-50 p-4 rounded-2xl max-h-64">
          {messages.map(msg => (
            <div key={msg.id} className="bg-white p-3 rounded-xl border border-slate-200">
              <div className="flex items-center gap-2 mb-2">
                <img src={msg.sender.avatar} alt={msg.sender.name} className="w-6 h-6 rounded-full" />
                <span className="font-bold text-slate-900 text-sm">{msg.sender.name}</span>
                <span className="text-xs text-slate-500">{msg.timestamp.toLocaleTimeString()}</span>
              </div>
              <p className="text-slate-700 text-sm">{msg.text}</p>
              {showTranslation && msg.translatedText && (
                <p className="text-xs text-slate-500 italic mt-2 p-2 bg-slate-100 rounded border-l-2 border-indigo-300">
                  {msg.translatedText}
                </p>
              )}
            </div>
          ))}
        </div>

        {/* Message Input */}
        <div className="flex gap-2">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Type a message..."
            className="flex-1 px-4 py-3 border border-slate-300 rounded-xl font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-600"
          />
          <button 
            onClick={handleSendMessage}
            className="px-4 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-bold transition-all"
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

const Milestones: React.FC<{ milestones: Milestone[] }> = ({ milestones }) => {
  const progress = useMemo(() => {
    const completed = milestones.filter(m => m.completed).length;
    return milestones.length > 0 ? Math.round((completed / milestones.length) * 100) : 0;
  }, [milestones]);

  return (
    <div className="bg-white rounded-3xl border border-slate-200 p-8 shadow-sm">
      <h2 className="text-2xl font-black text-slate-900 mb-6 flex items-center gap-2">
        <CheckCircle2 className="text-indigo-600" /> Project Milestones
      </h2>

      {/* Progress bar */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <p className="text-sm font-bold text-slate-600">Overall Progress</p>
          <p className="text-sm font-black text-indigo-600">{progress}%</p>
        </div>
        <div className="w-full bg-slate-200 h-3 rounded-full overflow-hidden">
          <div 
            className="bg-indigo-600 h-full transition-all duration-500" 
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Milestones list */}
      <div className="space-y-3">
        {milestones.map((milestone, idx) => (
          <div 
            key={milestone.id} 
            className={`p-4 rounded-2xl border-2 transition-all ${
              milestone.completed
                ? 'bg-green-50 border-green-300'
                : 'bg-slate-50 border-slate-200'
            }`}
          >
            <div className="flex items-start gap-3">
              <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 mt-1 ${
                milestone.completed
                  ? 'bg-green-500 border-green-500'
                  : 'border-slate-300'
              }`}>
                {milestone.completed && <CheckCircle2 size={16} className="text-white" />}
              </div>
              <div className="flex-1">
                <h3 className="font-black text-slate-900">{idx + 1}. {milestone.title}</h3>
                <p className="text-sm text-slate-600 mt-1">{milestone.description}</p>
                <div className="flex items-center gap-4 mt-2 text-xs">
                  <span className="flex items-center gap-1 text-slate-500">
                    <Calendar size={14} /> Due: {milestone.dueDate.toLocaleDateString()}
                  </span>
                  {milestone.assignee && (
                    <span className="bg-indigo-100 text-indigo-700 px-2 py-1 rounded font-bold">
                      Assigned to {milestone.assignee.name}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const SubmissionPortal: React.FC<{ submission?: Submission; onSubmit: (files: any) => void }> = ({ submission, onSubmit }) => {
  const [files, setFiles] = useState<{ project?: File; video?: File; report?: File }>({});

  return (
    <div className="bg-white rounded-3xl border border-slate-200 p-8 shadow-sm">
      <h2 className="text-2xl font-black text-slate-900 mb-6 flex items-center gap-2">
        <Upload className="text-indigo-600" /> Project Submission
      </h2>

      {submission && submission.submittedAt ? (
        <div className="bg-green-50 border-2 border-green-300 rounded-2xl p-6">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle2 size={24} className="text-green-600" />
            <h3 className="text-lg font-black text-green-900">Submitted Successfully!</h3>
          </div>
          <p className="text-green-800 text-sm">Submitted on {submission.submittedAt.toLocaleString()}</p>
          {submission.score && (
            <p className="text-green-800 text-sm mt-2">Score: <span className="font-black text-lg">{submission.score}/100</span></p>
          )}
          {submission.feedback && (
            <div className="mt-4 p-3 bg-white rounded-xl border border-green-300">
              <p className="text-xs font-bold text-slate-600 mb-1">Expert Feedback:</p>
              <p className="text-slate-700">{submission.feedback}</p>
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          <div className="p-4 bg-slate-50 rounded-2xl border-2 border-dashed border-slate-300 text-center">
            <Paperclip className="mx-auto text-slate-400 mb-2" size={32} />
            <p className="font-bold text-slate-700">Project File</p>
            <input 
              type="file" 
              onChange={(e) => setFiles({...files, project: e.target.files?.[0]})}
              className="mt-2 mx-auto block text-sm"
            />
            {files.project && <p className="text-xs text-indigo-600 font-bold mt-1">✓ {files.project.name}</p>}
          </div>

          <div className="p-4 bg-slate-50 rounded-2xl border-2 border-dashed border-slate-300 text-center">
            <Video className="mx-auto text-slate-400 mb-2" size={32} />
            <p className="font-bold text-slate-700">Video Presentation</p>
            <input 
              type="file" 
              onChange={(e) => setFiles({...files, video: e.target.files?.[0]})}
              className="mt-2 mx-auto block text-sm"
            />
            {files.video && <p className="text-xs text-indigo-600 font-bold mt-1">✓ {files.video.name}</p>}
          </div>

          <div className="p-4 bg-slate-50 rounded-2xl border-2 border-dashed border-slate-300 text-center">
            <FileText className="mx-auto text-slate-400 mb-2" size={32} />
            <p className="font-bold text-slate-700">Written Report</p>
            <input 
              type="file" 
              onChange={(e) => setFiles({...files, report: e.target.files?.[0]})}
              className="mt-2 mx-auto block text-sm"
            />
            {files.report && <p className="text-xs text-indigo-600 font-bold mt-1">✓ {files.report.name}</p>}
          </div>

          <button 
            onClick={() => onSubmit(files)}
            className="w-full px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-2xl font-black uppercase tracking-tight transition-all"
          >
            Submit Project
          </button>
        </div>
      )}
    </div>
  );
};

const Leaderboard: React.FC<{ entries: LeaderboardEntry[] }> = ({ entries }) => {
  const [filter, setFilter] = useState<string>('all');

  const filtered = useMemo(() => {
    return filter === 'all' ? entries : entries.filter(e => e.country === filter);
  }, [entries, filter]);

  return (
    <div className="bg-white rounded-3xl border border-slate-200 p-8 shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-black text-slate-900 flex items-center gap-2">
          <Trophy className="text-amber-500" /> Live Leaderboard
        </h2>
        <select 
          value={filter} 
          onChange={(e) => setFilter(e.target.value)}
          className="px-4 py-2 border border-slate-300 rounded-xl font-bold text-slate-700"
        >
          <option value="all">All Countries</option>
          {Array.from(new Set(entries.map(e => e.country))).map(country => (
            <option key={country} value={country}>{country}</option>
          ))}
        </select>
      </div>

      <div className="space-y-2">
        {filtered.map((entry, idx) => (
          <div 
            key={entry.teamId} 
            className={`p-4 rounded-2xl border-2 transition-all ${
              idx === 0
                ? 'bg-amber-50 border-amber-300'
                : idx === 1
                ? 'bg-slate-100 border-slate-300'
                : idx === 2
                ? 'bg-orange-50 border-orange-300'
                : 'bg-slate-50 border-slate-200'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center font-black text-lg ${
                  idx === 0
                    ? 'bg-amber-400 text-amber-900'
                    : idx === 1
                    ? 'bg-slate-400 text-white'
                    : idx === 2
                    ? 'bg-orange-400 text-white'
                    : 'bg-slate-300 text-slate-700'
                }`}>
                  {entry.rank}
                </div>
                <div>
                  <h3 className="font-black text-slate-900">{entry.teamName}</h3>
                  <p className="text-xs text-slate-500">{entry.country} • {entry.members} members</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-2xl font-black text-indigo-600">{entry.score}</p>
                <p className="text-xs font-bold text-slate-500 capitalize">{entry.status}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// --- Main Component ---

const GlobalCollaboration: React.FC<GlobalCollaborationProps> = ({ 
  challengeId, 
  currentUserId,
  currentUserTeam 
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'teams' | 'workspace' | 'submissions' | 'leaderboard'>('overview');
  const [teams, setTeams] = useState<Team[]>([]);
  const [challenge, setChallenge] = useState<Challenge | null>(null);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [milestones, setMilestones] = useState<Milestone[]>([]);

  useEffect(() => {
    // Mock data loading - replace with API calls to /api/challenges/{challengeId}
    setChallenge({
      id: challengeId,
      title: 'Global Climate Action Challenge 2026',
      description: 'Create innovative solutions to combat climate change across borders',
      startDate: new Date('2026-04-01'),
      endDate: new Date('2026-06-30'),
      countries: ['USA', 'China', 'India', 'Germany', 'Brazil', 'UK', 'Japan', 'Australia'],
      status: 'in-progress',
      teamsRegistered: 45,
      maxTeams: 100
    });

    setTeams([
      {
        id: 't1',
        name: 'Green Innovators',
        country: 'USA',
        members: [
          {
            id: 'm1',
            name: 'Alex Johnson',
            country: 'USA',
            role: 'team-lead',
            avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Alex',
            status: 'online',
            lastSeen: new Date()
          }
        ],
        challengeId,
        openings: 0,
        score: 92,
        submissionStatus: 'evaluated'
      },
      {
        id: 't2',
        name: 'Climate Warriors',
        country: 'Germany',
        members: [
          {
            id: 'm2',
            name: 'Sarah Mueller',
            country: 'Germany',
            role: 'team-lead',
            avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah',
            status: 'online',
            lastSeen: new Date()
          }
        ],
        challengeId,
        openings: 2,
        submissionStatus: 'pending'
      }
    ]);

    setMilestones([
      {
        id: 'ml1',
        title: 'Research & Planning',
        description: 'Complete market research and create project plan',
        dueDate: new Date('2026-04-30'),
        completed: true
      },
      {
        id: 'ml2',
        title: 'Prototype Development',
        description: 'Build working prototype of solution',
        dueDate: new Date('2026-05-31'),
        completed: false
      },
      {
        id: 'ml3',
        title: 'Final Submission',
        description: 'Submit project files and documentation',
        dueDate: new Date('2026-06-30'),
        completed: false
      }
    ]);

    setMessages([
      {
        id: 'msg1',
        sender: {
          id: 'm1',
          name: 'Alex Johnson',
          country: 'USA',
          role: 'team-lead',
          avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Alex',
          status: 'online',
          lastSeen: new Date()
        },
        text: 'Great progress on the prototype! Should we schedule a video call to discuss next steps?',
        timestamp: new Date(Date.now() - 15 * 60000),
        language: 'en'
      }
    ]);

    setLeaderboard([
      { rank: 1, teamId: 't1', teamName: 'Green Innovators', country: 'USA', score: 92, members: 5, status: 'evaluated' },
      { rank: 2, teamId: 't2', teamName: 'Climate Warriors', country: 'Germany', score: 88, members: 4, status: 'submitted' },
      { rank: 3, teamId: 't3', teamName: 'EcoTech Hub', country: 'India', score: 85, members: 6, status: 'submitted' }
    ]);
  }, [challengeId]);

  if (!challenge) {
    return (
      <div className="flex items-center justify-center h-screen bg-slate-50">
        <div className="text-center">
          <div className="animate-spin w-16 h-16 border-4 border-indigo-200 border-t-indigo-600 rounded-full mx-auto mb-4"></div>
          <p className="text-slate-600 font-bold">Loading challenge...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-slate-50 min-h-screen p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center gap-3 mb-8">
          <Globe className="text-indigo-600" size={40} />
          <h1 className="text-4xl font-black text-slate-900">Global Collaboration Hub</h1>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 overflow-x-auto pb-2">
          {(['overview', 'teams', 'workspace', 'submissions', 'leaderboard'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-3 rounded-xl font-bold uppercase tracking-tight transition-all whitespace-nowrap ${
                activeTab === tab
                  ? 'bg-indigo-600 text-white shadow-lg'
                  : 'bg-white text-slate-700 border border-slate-200 hover:bg-slate-50'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="space-y-6">
          {activeTab === 'overview' && (
            <>
              <ChallengeOverview challenge={challenge} />
              <TeamBrowser 
                teams={teams} 
                onJoin={(teamId) => console.log('Joined team:', teamId)}
              />
            </>
          )}

          {activeTab === 'teams' && (
            <TeamBrowser 
              teams={teams} 
              onJoin={(teamId) => console.log('Joined team:', teamId)}
            />
          )}

          {activeTab === 'workspace' && currentUserTeam && (
            <>
              <TeamWorkspace team={currentUserTeam} messages={messages} />
              <Milestones milestones={milestones} />
            </>
          )}

          {activeTab === 'submissions' && (
            <>
              <SubmissionPortal 
                onSubmit={(files) => console.log('Submitting:', files)}
              />
              <Leaderboard entries={leaderboard} />
            </>
          )}

          {activeTab === 'leaderboard' && (
            <Leaderboard entries={leaderboard} />
          )}
        </div>

        {/* Video Meeting CTA */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-3xl p-8 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-2xl font-black mb-2">Schedule Team Meeting</h3>
              <p className="text-indigo-100">Connect with your team members via video conference</p>
            </div>
            <button className="flex items-center gap-2 px-6 py-3 bg-white text-indigo-600 rounded-2xl font-black hover:bg-indigo-50 transition-all">
              <Video size={20} /> Start Meeting
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GlobalCollaboration;
