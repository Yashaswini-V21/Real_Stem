import React, { useState, useEffect, useMemo } from 'react';
import {
  Trophy,
  Globe,
  Zap,
  Users,
  Download,
  Share2,
  Calendar,
  MapPin,
  Star,
  Briefcase,
  Award,
  TrendingUp,
  Image as ImageIcon,
  ExternalLink,
  Lock,
  BookOpen,
  MessageSquare,
  GraduationCap
} from 'lucide-react';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';
import { ImpactData, ImpactLevel, SkillCategory } from '../types/impact';

interface ImpactDashboardProps {
  userId?: string;
}

const impactLevelColors = {
  local: 'bg-blue-100 text-blue-700 border-blue-300',
  regional: 'bg-green-100 text-green-700 border-green-300',
  national: 'bg-purple-100 text-purple-700 border-purple-300',
  global: 'bg-red-100 text-red-700 border-red-300'
};

const ImpactDashboard: React.FC<ImpactDashboardProps> = ({ userId = 'me' }) => {
  const [impactData, setImpactData] = useState<ImpactData | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedProject, setExpandedProject] = useState<string | null>(null);
  const [showShareModal, setShowShareModal] = useState(false);

  // Mock data loading (replace with API call)
  useEffect(() => {
    const fetchImpactData = async () => {
      try {
        // const response = await fetch(`/api/users/${userId}/impact`);
        // const data = await response.json();
        // setImpactData(data);
        
        // Mock data for demonstration
        setImpactData({
          lessonsCompleted: 24,
          countriesCollaborated: 8,
          challengesWon: 5,
          conceptsMastered: 47,
          joinDate: new Date('2025-09-01'),
          achievements: [
            {
              id: '1',
              title: 'Tree-Planting Proposal Adopted',
              description: 'Your tree-planting proposal was reviewed and adopted by City Council',
              date: new Date('2026-03-15'),
              impactLevel: 'regional',
              proofLinks: ['https://example.com/council-vote'],
              photos: ['https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=500'],
              metricsImpact: { label: 'Trees Planted', value: 500 }
            },
            {
              id: '2',
              title: 'Climate Change Research Contribution',
              description: 'Your data analysis contributed to peer-reviewed climate study',
              date: new Date('2026-02-20'),
              impactLevel: 'national',
              proofLinks: ['https://doi.org/10.1234/climate-2026'],
              photos: [],
              metricsImpact: { label: 'Research Citations', value: 12 }
            },
            {
              id: '3',
              title: 'Global STEM Challenge Winner',
              description: 'Won international AI ethics design challenge',
              date: new Date('2026-01-10'),
              impactLevel: 'global',
              proofLinks: ['https://example.com/challenge-results'],
              photos: ['https://images.unsplash.com/photo-1552664730-d307ca884978?w=500'],
              metricsImpact: { label: 'Prize Awarded', value: 5000 }
            }
          ],
          connections: [
            {
              id: '1',
              name: 'Dr. Sarah Chen',
              role: 'Quantum Computing Researcher',
              avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah',
              type: 'mentor',
              country: 'USA',
              sessions: 8
            },
            {
              id: '2',
              name: 'Marco Rossi',
              role: 'High School Student',
              avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Marco',
              type: 'peer',
              country: 'Italy'
            },
            {
              id: '3',
              name: 'Prof. Aisha Okafor',
              role: 'Environmental Scientist',
              avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Aisha',
              type: 'mentor',
              country: 'Nigeria',
              sessions: 5
            }
          ],
          careerExperiences: [
            { id: '1', careerTitle: 'Data Scientist', simulationScore: 92, dateCompleted: new Date('2026-02-01'), interestLevel: 85 },
            { id: '2', careerTitle: 'Climate Engineer', simulationScore: 88, dateCompleted: new Date('2026-01-15'), interestLevel: 78 },
            { id: '3', careerTitle: 'AI Researcher', simulationScore: 95, dateCompleted: new Date('2026-03-01'), interestLevel: 90 }
          ],
          skills: [
            { skill: 'critical_thinking', label: 'Critical Thinking', value: 82 },
            { skill: 'problem_solving', label: 'Problem Solving', value: 88 },
            { skill: 'collaboration', label: 'Collaboration', value: 75 },
            { skill: 'communication', label: 'Communication', value: 80 },
            { skill: 'technical', label: 'Technical Skills', value: 86 }
          ],
          badges: [
            { id: '1', name: 'Trailblazer', icon: '🚀', description: 'Completed first 5 lessons', unlockedAt: new Date('2025-09-15') },
            { id: '2', name: 'Global Collaborator', icon: '🌍', description: 'Connected with peers from 5+ countries', unlockedAt: new Date('2025-11-20') },
            { id: '3', name: 'Problem Solver', icon: '💡', description: 'Won 3 challenges', unlockedAt: new Date('2026-01-10') },
            { id: '4', name: 'Change Maker', icon: '🌟', description: 'Real-world impact project adopted', unlockedAt: new Date('2026-03-15') }
          ],
          portfolio: [
            {
              id: '1',
              title: 'Smart Water Management System',
              description: 'IoT-based system for agricultural water optimization',
              thumbnail: 'https://images.unsplash.com/photo-1581092918056-0c4c3acd3789?w=500',
              videoUrl: 'https://example.com/video1',
              results: 'Reduced water consumption by 35% in pilot study',
              category: 'IoT',
              completedAt: new Date('2026-03-01'),
              impactLevel: 'regional'
            },
            {
              id: '2',
              title: 'AI Bias Detection Tool',
              description: 'Machine learning model to detect bias in AI systems',
              thumbnail: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=500',
              results: 'Adopted by 3 tech companies for internal testing',
              category: 'AI/ML',
              completedAt: new Date('2026-02-15'),
              impactLevel: 'national'
            },
            {
              id: '3',
              title: 'Carbon Footprint Calculator',
              description: 'Web app for individuals to track personal carbon emissions',
              thumbnail: 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=500',
              results: 'Used by 10,000+ users globally',
              category: 'Web App',
              completedAt: new Date('2026-01-20'),
              impactLevel: 'global'
            }
          ]
        });
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch impact data:', error);
        setLoading(false);
      }
    };

    fetchImpactData();
  }, [userId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-slate-50">
        <div className="text-center">
          <div className="animate-spin w-16 h-16 border-4 border-indigo-200 border-t-indigo-600 rounded-full mx-auto mb-4"></div>
          <p className="text-slate-600 font-bold">Loading your impact dashboard...</p>
        </div>
      </div>
    );
  }

  if (!impactData) {
    return <div className="p-8 text-center text-slate-500">No impact data available</div>;
  }

  // Calculate current career interest (average of top interests)
  const currentCareerInterest = Math.round(
    impactData.careerExperiences.reduce((sum, c) => sum + c.interestLevel, 0) / impactData.careerExperiences.length
  );

  return (
    <div className="bg-slate-50 min-h-screen p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8">
          <div>
            <h1 className="text-4xl font-black text-slate-900 tracking-tight flex items-center gap-3">
              <Trophy className="text-amber-500" size={40} />
              Your Impact Story
            </h1>
            <p className="text-slate-500 mt-2 font-medium">Real-world contributions since {impactData.joinDate.toLocaleDateString()}</p>
          </div>
          <div className="flex gap-3">
            <button 
              onClick={() => setShowShareModal(true)}
              className="flex items-center gap-2 px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-2xl font-black uppercase tracking-tight transition-all shadow-lg hover:scale-105"
            >
              <Share2 size={20} /> Share Impact
            </button>
            <button className="flex items-center gap-2 px-6 py-3 bg-white border-2 border-slate-200 text-slate-700 rounded-2xl font-black uppercase tracking-tight hover:bg-slate-50 transition-all">
              <Download size={20} /> Export PDF
            </button>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <BookOpen className="text-blue-600" size={32} />
              <span className="text-xs font-black bg-blue-100 text-blue-700 px-3 py-1 rounded-full">Achievement</span>
            </div>
            <h3 className="text-4xl font-black text-slate-900">{impactData.lessonsCompleted}</h3>
            <p className="text-slate-500 font-bold uppercase text-xs tracking-widest mt-2">Lessons Completed</p>
          </div>

          <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <Globe className="text-green-600" size={32} />
              <span className="text-xs font-black bg-green-100 text-green-700 px-3 py-1 rounded-full">Global</span>
            </div>
            <h3 className="text-4xl font-black text-slate-900">{impactData.countriesCollaborated}</h3>
            <p className="text-slate-500 font-bold uppercase text-xs tracking-widest mt-2">Countries Collaborated</p>
          </div>

          <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <Trophy className="text-amber-600" size={32} />
              <span className="text-xs font-black bg-amber-100 text-amber-700 px-3 py-1 rounded-full">Winner</span>
            </div>
            <h3 className="text-4xl font-black text-slate-900">{impactData.challengesWon}</h3>
            <p className="text-slate-500 font-bold uppercase text-xs tracking-widest mt-2">Challenges Won</p>
          </div>

          <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <Zap className="text-purple-600" size={32} />
              <span className="text-xs font-black bg-purple-100 text-purple-700 px-3 py-1 rounded-full">Mastery</span>
            </div>
            <h3 className="text-4xl font-black text-slate-900">{impactData.conceptsMastered}</h3>
            <p className="text-slate-500 font-bold uppercase text-xs tracking-widest mt-2">Concepts Mastered</p>
          </div>
        </div>

        {/* Skills Radar & Career Interest */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Skills Radar */}
          <div className="lg:col-span-2 bg-white p-8 rounded-3xl border border-slate-200 shadow-sm">
            <h2 className="text-2xl font-black text-slate-900 mb-6 flex items-center gap-2">
              <TrendingUp className="text-indigo-600" /> Skills Development
            </h2>
            <ResponsiveContainer width="100%" height={400}>
              <RadarChart data={impactData.skills}>
                <PolarGrid stroke="#e2e8f0" />
                <PolarAngleAxis dataKey="label" tick={{ fontSize: 12, fontWeight: 700, fill: '#64748b' }} />
                <PolarRadiusAxis angle={90} domain={[0, 100]} />
                <Radar name="Your Score" dataKey="value" stroke="#4f46e5" fill="#4f46e5" fillOpacity={0.4} />
                <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }} />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* Career Interests */}
          <div className="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm">
            <h2 className="text-2xl font-black text-slate-900 mb-6 flex items-center gap-2">
              <Briefcase className="text-indigo-600" /> Career Path
            </h2>
            <div className="space-y-4">
              <div>
                <p className="text-xs font-black uppercase text-slate-400 mb-2">Current Interest Level</p>
                <div className="flex items-end gap-3">
                  <div className="text-4xl font-black text-indigo-600">{currentCareerInterest}%</div>
                  <div className="flex-grow bg-slate-100 rounded-full h-2 mb-2">
                    <div className="bg-indigo-600 h-full rounded-full" style={{ width: `${currentCareerInterest}%` }}></div>
                  </div>
                </div>
              </div>

              <div className="mt-6 space-y-3">
                <p className="text-xs font-black uppercase text-slate-400 mb-3">Simulations Completed</p>
                {impactData.careerExperiences.slice(0, 3).map(career => (
                  <div key={career.id} className="flex items-center justify-between p-3 bg-slate-50 rounded-2xl border border-slate-100">
                    <span className="font-bold text-sm text-slate-700">{career.careerTitle}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-black bg-green-100 text-green-700 px-2 py-1 rounded">{career.simulationScore}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Achievement Timeline */}
        <div className="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm">
          <h2 className="text-2xl font-black text-slate-900 mb-8 flex items-center gap-2">
            <Calendar className="text-indigo-600" /> Real-World Impact Timeline
          </h2>
          <div className="space-y-6">
            {impactData.achievements.map((achievement, idx) => (
              <div key={achievement.id} className="flex gap-6 pb-6 border-b border-slate-100 last:border-b-0">
                <div className="flex flex-col items-center">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-white ${
                    achievement.impactLevel === 'local' ? 'bg-blue-500' :
                    achievement.impactLevel === 'regional' ? 'bg-green-500' :
                    achievement.impactLevel === 'national' ? 'bg-purple-500' :
                    'bg-red-500'
                  }`}>
                    {idx + 1}
                  </div>
                  {idx !== impactData.achievements.length - 1 && <div className="w-1 h-20 bg-slate-200 mt-2" />}
                </div>
                
                <div className="flex-grow">
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <div>
                      <h3 className="text-lg font-black text-slate-900">{achievement.title}</h3>
                      <p className="text-slate-600 text-sm mt-1">{achievement.description}</p>
                    </div>
                    <span className={`text-xs font-black uppercase px-3 py-1.5 rounded-full border whitespace-nowrap ${impactLevelColors[achievement.impactLevel]}`}>
                      {achievement.impactLevel}
                    </span>
                  </div>

                  <div className="flex items-center gap-4 mb-4 flex-wrap">
                    <span className="text-xs font-bold text-slate-500">
                      📅 {achievement.date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                    </span>
                    {achievement.metricsImpact && (
                      <span className="text-xs font-bold text-indigo-600 bg-indigo-50 px-3 py-1 rounded-full">
                        🎯 {achievement.metricsImpact.label}: {achievement.metricsImpact.value.toLocaleString()}
                      </span>
                    )}
                  </div>

                  <div className="flex flex-wrap gap-3">
                    {achievement.photos.map((photo, pidx) => (
                      <a key={pidx} href={photo} target="_blank" rel="noopener noreferrer" className="group">
                        <img src={photo} alt={`Achievement ${pidx}`} className="h-20 rounded-lg object-cover group-hover:opacity-80 transition-opacity" />
                      </a>
                    ))}
                    {achievement.proofLinks.map((link, lidx) => (
                      <a key={lidx} href={link} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-lg transition-colors">
                        <ExternalLink size={14} /> Proof
                      </a>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Connections Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Mentors & Peers */}
          <div className="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm">
            <h2 className="text-2xl font-black text-slate-900 mb-6 flex items-center gap-2">
              <Users className="text-indigo-600" /> Global Network
            </h2>
            <div className="space-y-4">
              {impactData.connections.map(conn => (
                <div key={conn.id} className={`p-5 rounded-2xl border-2 ${conn.type === 'mentor' ? 'bg-indigo-50 border-indigo-200' : 'bg-green-50 border-green-200'}`}>
                  <div className="flex items-start gap-4">
                    <img src={conn.avatar} alt={conn.name} className="w-12 h-12 rounded-full" />
                    <div className="flex-grow">
                      <h3 className="font-black text-slate-900">{conn.name}</h3>
                      <p className="text-xs font-bold text-slate-600 uppercase tracking-widest">{conn.role}</p>
                      <div className="flex items-center gap-3 mt-2 flex-wrap">
                        {conn.country && <span className="text-xs font-bold bg-white px-2 py-1 rounded">🌍 {conn.country}</span>}
                        <span className={`text-[10px] font-black uppercase px-2 py-1 rounded ${conn.type === 'mentor' ? 'bg-indigo-200 text-indigo-700' : 'bg-green-200 text-green-700'}`}>
                          {conn.type}
                        </span>
                        {conn.sessions && <span className="text-xs font-bold bg-white px-2 py-1 rounded">💬 {conn.sessions} sessions</span>}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Badges */}
          <div className="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm">
            <h2 className="text-2xl font-black text-slate-900 mb-6 flex items-center gap-2">
              <Award className="text-amber-500" /> Badges & Achievements
            </h2>
            <div className="grid grid-cols-2 gap-4">
              {impactData.badges.map(badge => (
                <div key={badge.id} className="flex flex-col items-center text-center p-4 bg-amber-50 rounded-2xl border-2 border-amber-200">
                  <span className="text-5xl mb-2">{badge.icon}</span>
                  <h3 className="font-black text-slate-900 text-sm">{badge.name}</h3>
                  <p className="text-[10px] text-slate-600 mt-1">{badge.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Projects Portfolio */}
        <div className="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm">
          <h2 className="text-2xl font-black text-slate-900 mb-8 flex items-center gap-2">
            <GraduationCap className="text-indigo-600" /> Projects Portfolio
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {impactData.portfolio.map(project => (
              <div 
                key={project.id} 
                onClick={() => setExpandedProject(expandedProject === project.id ? null : project.id)}
                className="group cursor-pointer"
              >
                <div className="relative h-48 rounded-2xl overflow-hidden mb-4 border-2 border-slate-200 group-hover:border-indigo-500 transition-all">
                  <img src={project.thumbnail} alt={project.title} className="w-full h-full object-cover group-hover:scale-110 transition-transform" />
                  <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <span className="text-white font-black text-lg">View Details</span>
                  </div>
                  <div className="absolute top-3 right-3">
                    <span className={`text-xs font-black uppercase px-3 py-1.5 rounded-full border ${impactLevelColors[project.impactLevel]}`}>
                      {project.impactLevel}
                    </span>
                  </div>
                </div>
                <h3 className="font-black text-slate-900 text-lg leading-tight">{project.title}</h3>
                <p className="text-slate-600 text-sm mt-2 line-clamp-2">{project.description}</p>
                <div className="flex items-center gap-2 mt-3 flex-wrap">
                  <span className="text-[10px] font-bold bg-slate-100 px-2 py-1 rounded">{project.category}</span>
                  <span className="text-[10px] font-bold text-green-700 bg-green-100 px-2 py-1 rounded">✓ {project.results}</span>
                </div>

                {expandedProject === project.id && (
                  <div className="mt-4 p-4 bg-slate-50 rounded-2xl border border-slate-200">
                    <p className="text-sm text-slate-700 mb-3"><strong>Results:</strong> {project.results}</p>
                    <p className="text-xs text-slate-500 mb-4">Completed: {project.completedAt.toLocaleDateString()}</p>
                    {project.videoUrl && (
                      <a href={project.videoUrl} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg font-bold text-xs hover:bg-indigo-500 transition-colors">
                        <ImageIcon size={14} /> Watch Demo
                      </a>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Share Modal */}
      {showShareModal && (
        <div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl p-8 max-w-md w-full shadow-2xl">
            <h2 className="text-2xl font-black text-slate-900 mb-6">Share Your Impact</h2>
            <div className="space-y-3">
              <button className="w-full flex items-center gap-3 px-6 py-4 bg-blue-50 text-blue-700 rounded-2xl font-bold hover:bg-blue-100 transition-colors border-2 border-blue-200">
                <span className="text-2xl">f</span> Share on Facebook
              </button>
              <button className="w-full flex items-center gap-3 px-6 py-4 bg-sky-50 text-sky-700 rounded-2xl font-bold hover:bg-sky-100 transition-colors border-2 border-sky-200">
                <span className="text-2xl">𝕏</span> Share on Twitter
              </button>
              <button className="w-full flex items-center gap-3 px-6 py-4 bg-indigo-50 text-indigo-700 rounded-2xl font-bold hover:bg-indigo-100 transition-colors border-2 border-indigo-200">
                <span className="text-2xl">in</span> Share on LinkedIn
              </button>
              <button className="w-full flex items-center gap-3 px-6 py-4 bg-slate-100 text-slate-700 rounded-2xl font-bold hover:bg-slate-200 transition-colors border-2 border-slate-300 mt-6">
                Copy Link
              </button>
            </div>
            <button 
              onClick={() => setShowShareModal(false)}
              className="w-full mt-6 py-3 text-slate-600 font-bold hover:text-slate-900 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ImpactDashboard;
