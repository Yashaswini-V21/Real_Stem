export interface Lesson {
  id: string;
  title: string;
  description: string;
  topic: string;
  difficultyLevel: number;
  content: string;
  learningObjectives: string[];
  videoUrl?: string;
  simulationUrl?: string;
  createdAt: Date;
  updatedAt: Date;
}
