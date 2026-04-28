import React, { useState, useMemo } from 'react';
import { 
  Search, 
  Filter, 
  Zap, 
  Clock, 
  BookOpen, 
  AlertCircle, 
  ChevronDown,
  RefreshCw,
  FlaskConical,
  Dna,
  Atom,
  Calculator
} from 'lucide-react';
import { NewsItem } from '../types/news';
import { useNews } from '../hooks/useNews';
import { lessonsApi } from '../services/api';

// --- Helper Functions ---

const formatRelativeTime = (date: Date | string) => {
  const now = new Date();
  const published = new Date(date);
  const diffInSeconds = Math.floor((now.getTime() - published.getTime()) / 1000);

  if (diffInSeconds < 60) return 'just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  return published.toLocaleDateString();
};

const getSourceColor = (source: string) => {
  const colors: Record<string, string> = {
    'Nature': 'bg-green-100 text-green-800',
    'ScienceDaily': 'bg-blue-100 text-blue-800',
    'MIT Tech Review': 'bg-red-100 text-red-800',
    'NASA': 'bg-cyan-100 text-cyan-800',
    'Scientific American': 'bg-purple-100 text-purple-800',
  };
  return colors[source] || 'bg-gray-100 text-gray-800';
};

// --- Components ---

const NewsCard: React.FC<{ item: NewsItem; isTeacher?: boolean }> = ({ item, isTeacher }) => {
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerateLesson = async () => {
    try {
      setIsGenerating(true);
      await lessonsApi.generateLesson(item.id, false);
      alert('Lesson generation started! Check your dashboard soon.');
    } catch (error) {
      console.error('Failed to generate lesson:', error);
      alert('Failed to trigger lesson generation.');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden hover:shadow-md transition-shadow flex flex-col h-full">
      {item.imageUrl && (
        <div className="h-48 overflow-hidden relative">
          <img 
            src={item.imageUrl} 
            alt={item.title} 
            className="w-full h-full object-cover"
          />
          {item.category === 'Breaking' && (
            <div className="absolute top-3 left-3 bg-red-600 text-white px-2 py-1 rounded-md text-xs font-bold flex items-center gap-1">
              <Zap size={12} fill="white" /> BREAKING
            </div>
          )}
        </div>
      )}
      <div className="p-5 flex flex-col flex-grow">
        <div className="flex items-center justify-between mb-3">
          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${getSourceColor(item.source)}`}>
            {item.source}
          </span>
          <div className="flex items-center text-slate-400 text-xs gap-1">
            <Clock size={12} />
            {formatRelativeTime(item.publishedAt)}
          </div>
        </div>
        
        <h3 className="text-lg font-bold text-slate-900 mb-2 line-clamp-2 leading-snug">
          {item.title}
        </h3>
        
        <p className="text-slate-600 text-sm mb-4 line-clamp-3">
          {item.description}
        </p>
        
        <div className="flex flex-wrap gap-1.5 mb-6">
          <span className="bg-slate-50 text-slate-600 text-[10px] font-medium px-2 py-0.5 rounded border border-slate-100">
            #{item.category}
          </span>
          {/* Mock tags since we don't have them in schema */}
          <span className="bg-blue-50 text-blue-600 text-[10px] font-medium px-2 py-0.5 rounded border border-blue-100">
            #STEM
          </span>
        </div>

        <div className="mt-auto flex gap-2">
          {isTeacher && (
            <button 
              onClick={handleGenerateLesson}
              disabled={isGenerating}
              className="flex-1 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-300 text-white text-sm font-semibold py-2 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              {isGenerating ? <RefreshCw className="animate-spin" size={16} /> : <BookOpen size={16} />}
              Generate Lesson
            </button>
          )}
          <button className="flex-1 border border-slate-200 hover:bg-slate-50 text-slate-700 text-sm font-semibold py-2 px-4 rounded-lg transition-colors">
            Read More
          </button>
        </div>
      </div>
    </div>
  );
};

const SkeletonCard = () => (
  <div className="bg-slate-50 rounded-xl border border-slate-100 overflow-hidden animate-pulse h-[400px]">
    <div className="h-48 bg-slate-200" />
    <div className="p-5">
      <div className="flex justify-between mb-4">
        <div className="h-4 w-20 bg-slate-200 rounded" />
        <div className="h-4 w-16 bg-slate-200 rounded" />
      </div>
      <div className="h-6 w-full bg-slate-200 rounded mb-2" />
      <div className="h-6 w-2/3 bg-slate-200 rounded mb-4" />
      <div className="h-4 w-full bg-slate-100 rounded mb-1" />
      <div className="h-4 w-full bg-slate-100 rounded mb-1" />
      <div className="h-4 w-4/5 bg-slate-100 rounded" />
    </div>
  </div>
);

const NewsFeed: React.FC = () => {
  const [topic, setTopic] = useState<string>('All');
  const [breakingOnly, setBreakingOnly] = useState(false);
  const [limit, setLimit] = useState(12);

  const filters = useMemo(() => ({
    limit,
    offset: 0,
    stemOnly: true,
    topic: topic === 'All' ? undefined : topic,
    breakingOnly
  }), [topic, breakingOnly, limit]);

  const { news, loading, error } = useNews(filters);

  // Mock teacher role check
  const isTeacher = true; 

  const topics = [
    { name: 'All', icon: <Search size={14} /> },
    { name: 'Physics', icon: <Atom size={14} className="text-blue-500" /> },
    { name: 'Chemistry', icon: <FlaskConical size={14} className="text-purple-500" /> },
    { name: 'Biology', icon: <Dna size={14} className="text-green-500" /> },
    { name: 'Space', icon: <Zap size={14} className="text-orange-400" /> }
  ];

  const breakingNews = useMemo(() => news.filter(n => n.category === 'Breaking'), [news]);
  const regularNews = useMemo(() => news.filter(n => n.category !== 'Breaking'), [news]);

  if (error) {
    return (
      <div className="p-8 text-center bg-red-50 border border-red-100 rounded-xl">
        <AlertCircle className="mx-auto text-red-400 mb-3" size={48} />
        <h3 className="text-lg font-bold text-red-900 mb-1">Failed to load news</h3>
        <p className="text-red-600">{error}</p>
        <button 
          onClick={() => window.location.reload()}
          className="mt-4 bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-bold"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* --- Filter Bar --- */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8 bg-white p-4 rounded-2xl shadow-sm border border-slate-100">
        <div className="flex flex-wrap gap-2">
          {topics.map((t) => (
            <button
              key={t.name}
              onClick={() => setTopic(t.name)}
              className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold transition-all ${
                topic === t.name 
                  ? 'bg-slate-900 text-white shadow-md shadow-slate-200 scale-105' 
                  : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
              }`}
            >
              {t.icon} {t.name}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-4">
          <label className="flex items-center gap-3 cursor-pointer group">
            <span className="text-sm font-bold text-slate-700">Breaking Only</span>
            <div 
              onClick={() => setBreakingOnly(!breakingOnly)}
              className={`w-12 h-6 rounded-full p-1 transition-colors ${breakingOnly ? 'bg-red-500' : 'bg-slate-200'}`}
            >
              <div className={`w-4 h-4 bg-white rounded-full transition-transform ${breakingOnly ? 'translate-x-6' : 'translate-x-0'}`} />
            </div>
          </label>
        </div>
      </div>

      {/* --- Content Grid --- */}
      {loading && news.length === 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {[...Array(6)].map((_, i) => <SkeletonCard key={i} />)}
        </div>
      ) : news.length === 0 ? (
        <div className="text-center py-24 bg-slate-50 rounded-2xl border-2 border-dashed border-slate-200">
          <BookOpen className="mx-auto text-slate-300 mb-4" size={64} />
          <h2 className="text-2xl font-bold text-slate-900">No news found</h2>
          <p className="text-slate-500">Try adjusting your filters or checking back later.</p>
        </div>
      ) : (
        <div className="space-y-12">
          {/* Breaking News Section Highlighting */}
          {breakingNews.length > 0 && (
            <section>
              <div className="flex items-center gap-3 mb-6">
                <div className="bg-red-100 p-2 rounded-lg">
                  <Zap className="text-red-600" size={20} fill="currentColor" />
                </div>
                <h2 className="text-xl font-black text-slate-900 uppercase tracking-tight">Top Breaking Stories</h2>
                <div className="flex-grow h-px bg-slate-100 ml-4" />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {breakingNews.map(item => <NewsCard key={item.id} item={item} isTeacher={isTeacher} />)}
              </div>
            </section>
          )}

          {/* Regular News Section */}
          <section>
            <div className="flex items-center gap-3 mb-6">
              <div className="bg-blue-100 p-2 rounded-lg">
                <Clock className="text-blue-600" size={20} />
              </div>
              <h2 className="text-xl font-black text-slate-900 uppercase tracking-tight">Recent STEM Updates</h2>
              <div className="flex-grow h-px bg-slate-100 ml-4" />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {regularNews.map(item => <NewsCard key={item.id} item={item} isTeacher={isTeacher} />)}
            </div>
          </section>

          {/* Load More */}
          <div className="flex justify-center pt-8">
            <button 
              onClick={() => setLimit(prev => prev + 12)}
              disabled={loading}
              className="group bg-white border-2 border-slate-200 hover:border-slate-900 px-8 py-3 rounded-xl font-bold text-slate-900 transition-all flex items-center gap-3 shadow-sm hover:shadow-md"
            >
              {loading ? <RefreshCw className="animate-spin" size={20} /> : 'Load More Stories'}
              {!loading && <ChevronDown className="group-hover:translate-y-1 transition-transform" size={20} />}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default NewsFeed;
