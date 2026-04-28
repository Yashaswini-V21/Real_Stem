export type ImpactLevel = 'local' | 'regional' | 'national' | 'global';
export type SkillCategory = 'critical_thinking' | 'problem_solving' | 'collaboration' | 'communication' | 'technical';

export interface Achievement {
  id: string;
  title: string;
  description: string;
  date: Date;
  impactLevel: ImpactLevel;
  proofLinks: string[];
  photos: string[];
  metricsImpact?: {
    label: string;
    value: number;
  };
}

export interface Connection {
  id: string;
  name: string;
  role: string;
  avatar: string;
  type: 'mentor' | 'peer';
  country?: string;
  sessions?: number;
}

export interface CareerExperienceData {
  id: string;
  careerTitle: string;
  simulationScore: number;
  dateCompleted: Date;
  interestLevel: number; // 0-100
}

export interface SkillEntry {
  skill: SkillCategory;
  label: string;
  value: number; // 0-100
}

export interface Badge {
  id: string;
  name: string;
  icon: string;
  description: string;
  unlockedAt: Date;
}

export interface ProjectPortfolio {
  id: string;
  title: string;
  description: string;
  thumbnail: string;
  videoUrl?: string;
  results: string;
  category: string;
  completedAt: Date;
  impactLevel: ImpactLevel;
}

export interface ImpactData {
  lessonsCompleted: number;
  countriesCollaborated: number;
  challengesWon: number;
  conceptsMastered: number;
  achievements: Achievement[];
  connections: Connection[];
  careerExperiences: CareerExperienceData[];
  skills: SkillEntry[];
  badges: Badge[];
  portfolio: ProjectPortfolio[];
  joinDate: Date;
}
