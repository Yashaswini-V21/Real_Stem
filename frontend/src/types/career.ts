export type EducationLevel = 'BS' | 'MS' | 'PhD' | 'None';

export interface SalaryData {
  average: number;
  low: number;
  high: number;
  regional?: {
    region: string;
    average: number;
  }[];
}

export interface PathwayStep {
  label: string;
  duration: string;
  description: string;
  courses: string[];
}

export interface SuccessStory {
  id: string;
  name: string;
  role: string;
  story: string;
  avatar: string;
  startingPoint: string;
}

export interface Career {
  id: string;
  title: string;
  icon: string;
  salary: SalaryData;
  education: EducationLevel;
  description: string;
  subjects: string[];
  dayInLifeVideoUrl: string;
  growthRate: number; // e.g., 0.15 for 15%
  pathway: PathwayStep[];
  successStories: SuccessStory[];
}
