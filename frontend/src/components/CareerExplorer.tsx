import React, { useState, useMemo } from "react";
import { 
  Briefcase, 
  GraduationCap, 
  TrendingUp, 
  PlayCircle, 
  Target, 
  MessageCircle, 
  ChevronRight, 
  Filter, 
  Search,
  DollarSign,
  MapPin,
  Clock,
  BookOpen,
  ArrowRight,
  UserCheck
} from "lucide-react";
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Cell
} from "recharts";
import { Career, EducationLevel } from "../types/career";

interface CareerExplorerProps {
  careers: Career[];
  relatedSubjects: string[];
}

const CareerExplorer: React.FC<CareerExplorerProps> = ({ careers, relatedSubjects }) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedEducation, setSelectedEducation] = useState<EducationLevel | "All">("All");
  const [selectedSubject, setSelectedSubject] = useState<string>("All");
  const [minSalary, setMinSalary] = useState<number>(0);
  const [activeCareer, setActiveCareer] = useState<Career | null>(null);
  const [showModal, setShowModal] = useState<"video" | "mentor" | "simulation" | null>(null);

  const filteredCareers = useMemo(() => {
    return careers.filter(career => {
      const matchesSearch = career.title.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesEducation = selectedEducation === "All" || career.education === selectedEducation;
      const matchesSubject = selectedSubject === "All" || career.subjects.includes(selectedSubject);
      const matchesSalary = career.salary.average >= minSalary;
      return matchesSearch && matchesEducation && matchesSubject && matchesSalary;
    });
  }, [careers, searchQuery, selectedEducation, selectedSubject, minSalary]);

  const formatCurrency = (val: number) => 
    new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(val);

  return (
    <div className="flex flex-col gap-8 bg-slate-50 min-h-screen p-6 rounded-3xl">
      <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-200">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8">
          <div>
            <h2 className="text-3xl font-black text-slate-900 tracking-tight flex items-center gap-3">
              <Briefcase className="text-indigo-600" size={32} />
              Career Pathways
            </h2>
            <p className="text-slate-500 font-medium">Discover your future in STEM</p>
          </div>
          
          <div className="flex flex-wrap gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
              <input 
                type="text" 
                placeholder="Search careers..."
                className="pl-10 pr-4 py-2 bg-slate-100 border-transparent focus:bg-white focus:ring-2 focus:ring-indigo-500 rounded-xl text-sm transition-all"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>
        </div>

        <div className="flex flex-wrap gap-4">
          <div className="space-y-2">
            <label className="text-[10px] font-black uppercase tracking-widest text-slate-400 block ml-1">Education</label>
            <div className="flex gap-2">
              {["All", "BS", "MS", "PhD"].map(lvl => (
                <button
                  key={lvl}
                  onClick={() => setSelectedEducation(lvl as any)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                    selectedEducation === lvl ? "bg-indigo-600 text-white shadow-lg" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                  }`}
                >
                  {lvl}
                </button>
              ))}
            </div>
          </div>
          
          <div className="space-y-2">
            <label className="text-[10px] font-black uppercase tracking-widest text-slate-400 block ml-1">Subject Area</label>
            <select 
              className="bg-slate-100 border-none rounded-lg text-xs font-bold px-3 py-1.5 focus:ring-2 focus:ring-indigo-500"
              value={selectedSubject}
              onChange={(e) => setSelectedSubject(e.target.value)}
            >
              <option value="All">All Subjects</option>
              {relatedSubjects.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredCareers.map(career => (
          <div 
            key={career.id} 
            className="group bg-white rounded-[32px] p-6 border border-slate-200 hover:border-indigo-500/50 transition-all hover:shadow-2xl hover:shadow-indigo-500/10 cursor-pointer flex flex-col"
            onClick={() => setActiveCareer(career)}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="w-14 h-14 bg-indigo-50 rounded-2xl flex items-center justify-center text-indigo-600 group-hover:scale-110 transition-transform">
                <Briefcase size={28} />
              </div>
              <div className="text-right">
                <span className={`px-2 py-1 rounded-md text-[10px] font-black uppercase ${
                    career.growthRate > 0.1 ? "bg-green-100 text-green-700" : "bg-blue-100 text-blue-700"
                }`}>
                  +{Math.round(career.growthRate * 100)}% Growth
                </span>
              </div>
            </div>

            <h3 className="text-xl font-black text-slate-900 mb-2 leading-tight">{career.title}</h3>
            <p className="text-slate-500 text-sm leading-relaxed line-clamp-3 mb-6">{career.description}</p>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="bg-slate-50 p-3 rounded-2xl border border-slate-100">
                <span className="text-[10px] font-black uppercase text-slate-400 block mb-1">Avg Salary</span>
                <span className="text-slate-900 font-bold">{formatCurrency(career.salary.average)}</span>
              </div>
              <div className="bg-slate-50 p-3 rounded-2xl border border-slate-100">
                <span className="text-[10px] font-black uppercase text-slate-400 block mb-1">Education</span>
                <span className="text-slate-900 font-bold">{career.education}</span>
              </div>
            </div>

            <div className="flex flex-wrap gap-2 mb-8">
              {career.subjects.slice(0, 3).map(s => (
                <span key={s} className="px-2 py-1 bg-indigo-50 text-indigo-600 text-[10px] font-bold rounded-lg border border-indigo-100">
                  {s}
                </span>
              ))}
            </div>

            <div className="mt-auto flex items-center justify-between text-indigo-600 font-bold text-sm">
              <span>View Pathway</span>
              <ChevronRight size={18} className="group-hover:translate-x-1 transition-transform" />
            </div>
          </div>
        ))}
      </div>

      {activeCareer && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-end md:items-center justify-center p-4">
          <div className="bg-white w-full max-w-5xl max-h-[90vh] overflow-y-auto rounded-[40px] shadow-2xl relative">
            <button 
              onClick={() => setActiveCareer(null)}
              className="absolute top-6 right-6 p-2 bg-slate-100 hover:bg-slate-200 rounded-full transition-colors"
            >
              <ArrowRight className="rotate-180" size={24} />
            </button>

            <div className="grid grid-cols-1 lg:grid-cols-12">
              <div className="lg:col-span-7 p-8 lg:p-12 border-r border-slate-100">
                <div className="flex items-center gap-4 mb-8">
                  <div className="w-16 h-16 bg-indigo-600 rounded-3xl flex items-center justify-center text-white">
                    <Briefcase size={32} />
                  </div>
                  <div>
                    <h2 className="text-3xl font-black text-slate-900">{activeCareer.title}</h2>
                  </div>
                </div>

                <p className="text-slate-600 leading-relaxed mb-10 text-lg">{activeCareer.description}</p>

                <div className="flex flex-wrap gap-4 mb-12">
                  <button onClick={() => setShowModal("video")} className="flex-1 min-w-[200px] flex items-center justify-center gap-3 bg-red-50 text-red-600 py-4 px-6 rounded-2xl font-black uppercase tracking-tight hover:bg-red-100 transition-colors">
                    <PlayCircle size={24} /> Day in the Life
                  </button>
                  <button onClick={() => setShowModal("simulation")} className="flex-1 min-w-[200px] flex items-center justify-center gap-3 bg-indigo-600 text-white py-4 px-6 rounded-2xl font-black uppercase tracking-tight hover:bg-indigo-500 transition-all shadow-lg">
                    <Target size={24} /> Try This Career
                  </button>
                  <button onClick={() => setShowModal("mentor")} className="w-full flex items-center justify-center gap-3 bg-slate-100 text-slate-700 py-4 px-6 rounded-2xl font-black uppercase tracking-tight hover:bg-slate-200 transition-colors">
                    <MessageCircle size={24} /> Talk to Mentor
                  </button>
                </div>

                <div className="mb-12">
                  <h3 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
                    <GraduationCap className="text-indigo-600" /> Educational Journey
                  </h3>
                  <div className="space-y-4">
                    {activeCareer.pathway.map((step, idx) => (
                      <div key={idx} className="flex gap-4 group">
                        <div className="flex flex-col items-center">
                          <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold border-2 ${idx === 0 ? "bg-indigo-600 border-indigo-600 text-white" : "bg-white border-slate-200 text-slate-400"}`}>
                            {idx + 1}
                          </div>
                          {idx !== activeCareer.pathway.length - 1 && <div className="w-0.5 h-full bg-slate-100 my-2" />}
                        </div>
                        <div className="pb-8">
                          <h4 className="font-bold text-slate-900 text-lg mb-1">{step.label}</h4>
                          <span className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2 mb-2"><Clock size={12} /> {step.duration}</span>
                          <p className="text-slate-500 text-sm mb-3 leading-relaxed">{step.description}</p>
                          <div className="flex flex-wrap gap-2">
                            {step.courses.map(c => <span key={c} className="px-2 py-1 bg-slate-100 text-slate-600 text-[10px] font-bold rounded-md flex items-center gap-1"><BookOpen size={10} /> {c}</span>)}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="lg:col-span-5 p-8 lg:p-12 bg-slate-50">
                <div className="mb-12">
                  <h3 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2"><DollarSign className="text-green-600" /> Regional Comp.</h3>
                  <div className="h-64 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={activeCareer.salary.regional || []}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                        <XAxis dataKey="region" axisLine={false} tickLine={false} tick={{ fontSize: 10, fontWeight: 700 }} />
                        <YAxis hide />
                        <Tooltip cursor={{ fill: "#f1f5f9" }} contentStyle={{ borderRadius: "16px", border: "none", boxShadow: "0 10px 15px -3px rgb(0 0 0 / 0.1)" }} />
                        <Bar dataKey="average" fill="#4f46e5" radius={[8, 8, 0, 0]}>
                            {activeCareer.salary.regional?.map((entry, index) => <Cell key={index} fill={entry.average > activeCareer.salary.average ? "#4f46e5" : "#94a3b8"} />)}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                <div>
                  <h3 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2"><UserCheck className="text-indigo-600" /> People Like You</h3>
                  <div className="space-y-4">
                    {activeCareer.successStories.map(story => (
                      <div key={story.id} className="bg-white p-5 rounded-3xl border border-slate-200">
                        <div className="flex items-center gap-4 mb-4">
                          <img src={story.avatar} alt={story.name} className="w-12 h-12 rounded-2xl object-cover" />
                          <div>
                            <h4 className="font-bold text-slate-900 text-sm">{story.name}</h4>
                            <p className="text-[10px] font-black text-indigo-600 uppercase">{story.role}</p>
                          </div>
                        </div>
                        <p className="text-slate-600 text-xs italic leading-relaxed mb-3">"{story.story}"</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CareerExplorer;
