// Type definitions for GlobalCollaboration component

export type ChallengeStatus = 'recruiting' | 'in-progress' | 'judging' | 'completed';
export type UserRole = 'member' | 'team-lead' | 'judge' | 'organizer';
export type LanguageCode = 'en' | 'es' | 'fr' | 'de' | 'zh' | 'ja' | 'ar' | 'pt';
export type MemberStatus = 'online' | 'offline';
export type SubmissionStatus = 'pending' | 'submitted' | 'evaluated';

export interface Challenge {
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

export interface TeamMember {
  id: string;
  name: string;
  country: string;
  role: UserRole;
  avatar: string;
  status: MemberStatus;
  lastSeen: Date;
}

export interface Team {
  id: string;
  name: string;
  country: string;
  members: TeamMember[];
  challengeId: string;
  openings: number;
  score?: number;
  submissionStatus: SubmissionStatus;
}

export interface ChatMessage {
  id: string;
  sender: TeamMember;
  text: string;
  timestamp: Date;
  language: LanguageCode;
  translatedText?: string;
}

export interface Milestone {
  id: string;
  title: string;
  description: string;
  dueDate: Date;
  completed: boolean;
  assignee?: TeamMember;
}

export interface Submission {
  id: string;
  teamId: string;
  projectFile: string;
  videoPresentation: string;
  writtenReport: string;
  submittedAt: Date;
  score?: number;
  feedback?: string;
}

export interface LeaderboardEntry {
  rank: number;
  teamId: string;
  teamName: string;
  country: string;
  score: number;
  members: number;
  status: SubmissionStatus;
}
