import { create } from 'zustand';
import { Lesson } from '../types/lesson';
import { lessonsApi } from '../services/api';

// --- Types ---

export type DifficultyLevel = 'elementary' | 'middle' | 'high' | 'advanced' | 'college';
export type LessonTab = 'video' | 'simulation' | 'debate' | 'learn' | 'projects' | 'challenge' | 'careers';

export interface Progress {
  lessonId: string;
  completedSections: string[];
  videosWatched: number;
  totalVideos: number;
  simulationsCompleted: number;
  timeSpent: number; // in seconds
  quizScore?: number;
  lastAccessedAt: Date;
  completedAt?: Date;
}

export interface FetchParams {
  status?: string;
  level?: string;
  subject?: string;
  limit?: number;
  offset?: number;
}

interface LessonStoreState {
  // State
  lessons: Lesson[];
  currentLesson: Lesson | null;
  currentLevel: DifficultyLevel;
  currentTab: LessonTab;
  progress: Map<string, Progress>;
  isLoading: boolean;
  error: string | null;
  totalLessons: number;

  // Actions
  fetchLessons: (params: FetchParams) => Promise<void>;
  fetchLessonById: (id: string | number) => Promise<void>;
  setCurrentLevel: (level: DifficultyLevel) => void;
  setCurrentTab: (tab: LessonTab) => void;
  markSectionComplete: (lessonId: string, section: string) => Promise<void>;
  updateProgress: (lessonId: string, updates: Partial<Progress>) => Promise<void>;
  rateLesson: (lessonId: string | number, rating: number) => Promise<void>;
  searchLessons: (query: string) => Promise<void>;
  getProgress: (lessonId: string) => Progress | undefined;
  clearError: () => void;
  initializeProgress: () => void;
}

// --- Helpers ---

const STORAGE_KEY = 'lesson_progress';

const loadProgressFromStorage = (): Map<string, Progress> => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return new Map();
    
    const parsed = JSON.parse(stored);
    const map = new Map<string, Progress>();
    
    for (const [key, value] of Object.entries(parsed)) {
      map.set(key, {
        ...(value as Progress),
        lastAccessedAt: new Date(value.lastAccessedAt),
        completedAt: value.completedAt ? new Date(value.completedAt) : undefined,
      });
    }
    
    return map;
  } catch (error) {
    console.error('Failed to load progress from storage:', error);
    return new Map();
  }
};

const saveProgressToStorage = (progress: Map<string, Progress>) => {
  try {
    const obj: Record<string, Progress> = {};
    progress.forEach((value, key) => {
      obj[key] = value;
    });
    localStorage.setItem(STORAGE_KEY, JSON.stringify(obj));
  } catch (error) {
    console.error('Failed to save progress to storage:', error);
  }
};

// --- Store ---

export const useLessonStore = create<LessonStoreState>((set, get) => ({
  // Initial state
  lessons: [],
  currentLesson: null,
  currentLevel: 'high',
  currentTab: 'video',
  progress: new Map(),
  isLoading: false,
  error: null,
  totalLessons: 0,

  // Actions
  fetchLessons: async (params: FetchParams) => {
    set({ isLoading: true, error: null });
    try {
      const response = await lessonsApi.getLessons(params);
      
      set({
        lessons: response.items,
        totalLessons: response.total,
        isLoading: false,
        error: null,
      });
    } catch (error) {
      const errorMessage = error instanceof Error
        ? error.message
        : 'Failed to fetch lessons.';
      
      set({
        isLoading: false,
        error: errorMessage,
        lessons: [],
      });
      
      throw error;
    }
  },

  fetchLessonById: async (id: string | number) => {
    set({ isLoading: true, error: null });
    try {
      const lesson = await lessonsApi.getLessonById(id);
      
      // Initialize progress for this lesson if not already tracked
      const progress = get().progress;
      const lessonIdStr = id.toString();
      if (!progress.has(lessonIdStr)) {
        const newProgress: Progress = {
          lessonId: lessonIdStr,
          completedSections: [],
          videosWatched: 0,
          totalVideos: 1,
          simulationsCompleted: 0,
          timeSpent: 0,
          lastAccessedAt: new Date(),
        };
        
        const updatedProgress = new Map(progress);
        updatedProgress.set(lessonIdStr, newProgress);
        set({ progress: updatedProgress });
        saveProgressToStorage(updatedProgress);
      } else {
        // Update lastAccessedAt
        const lessonProgress = progress.get(lessonIdStr);
        if (lessonProgress) {
          const updatedProgress = new Map(progress);
          updatedProgress.set(lessonIdStr, {
            ...lessonProgress,
            lastAccessedAt: new Date(),
          });
          set({ progress: updatedProgress });
          saveProgressToStorage(updatedProgress);
        }
      }
      
      set({
        currentLesson: lesson,
        isLoading: false,
        error: null,
      });
    } catch (error) {
      const errorMessage = error instanceof Error
        ? error.message
        : 'Failed to fetch lesson.';
      
      set({
        isLoading: false,
        error: errorMessage,
        currentLesson: null,
      });
      
      throw error;
    }
  },

  setCurrentLevel: (level: DifficultyLevel) => {
    set({ currentLevel: level });
    localStorage.setItem('current_difficulty_level', level);
  },

  setCurrentTab: (tab: LessonTab) => {
    set({ currentTab: tab });
    localStorage.setItem('current_lesson_tab', tab);
  },

  markSectionComplete: async (lessonId: string, section: string) => {
    try {
      const progress = get().progress;
      const lessonProgress = progress.get(lessonId);
      
      if (!lessonProgress) {
        throw new Error('Lesson progress not found');
      }
      
      // Add section to completed sections
      const updatedSections = Array.from(new Set([
        ...lessonProgress.completedSections,
        section,
      ]));
      
      const updatedProgress = {
        ...lessonProgress,
        completedSections: updatedSections,
        lastAccessedAt: new Date(),
      };
      
      const newProgress = new Map(progress);
      newProgress.set(lessonId, updatedProgress);
      
      set({ progress: newProgress });
      saveProgressToStorage(newProgress);
      
      // Sync with API (fire-and-forget)
      // await api.post(`/api/lessons/${lessonId}/progress`, updatedProgress);
    } catch (error) {
      console.error('Failed to mark section complete:', error);
    }
  },

  updateProgress: async (lessonId: string, updates: Partial<Progress>) => {
    try {
      const progress = get().progress;
      const lessonProgress = progress.get(lessonId);
      
      if (!lessonProgress) {
        throw new Error('Lesson progress not found');
      }
      
      const updatedProgress: Progress = {
        ...lessonProgress,
        ...updates,
        lastAccessedAt: new Date(),
      };
      
      const newProgress = new Map(progress);
      newProgress.set(lessonId, updatedProgress);
      
      set({ progress: newProgress });
      saveProgressToStorage(newProgress);
      
      // Sync with API (fire-and-forget)
      // await api.put(`/api/lessons/${lessonId}/progress`, updatedProgress);
    } catch (error) {
      console.error('Failed to update progress:', error);
    }
  },

  rateLesson: async (lessonId: string | number, rating: number) => {
    set({ isLoading: true, error: null });
    try {
      await lessonsApi.rateLesson(lessonId, rating);
      
      set({
        isLoading: false,
        error: null,
      });
    } catch (error) {
      const errorMessage = error instanceof Error
        ? error.message
        : 'Failed to rate lesson.';
      
      set({
        isLoading: false,
        error: errorMessage,
      });
      
      throw error;
    }
  },

  searchLessons: async (query: string) => {
    if (!query.trim()) {
      set({ lessons: [], error: null });
      return;
    }
    
    set({ isLoading: true, error: null });
    try {
      const response = await lessonsApi.searchLessons(query);
      
      set({
        lessons: response.items,
        totalLessons: response.total,
        isLoading: false,
        error: null,
      });
    } catch (error) {
      const errorMessage = error instanceof Error
        ? error.message
        : 'Search failed.';
      
      set({
        isLoading: false,
        error: errorMessage,
        lessons: [],
      });
      
      throw error;
    }
  },

  getProgress: (lessonId: string) => {
    return get().progress.get(lessonId);
  },

  clearError: () => {
    set({ error: null });
  },

  initializeProgress: () => {
    const progress = loadProgressFromStorage();
    set({ progress });
    
    // Restore UI preferences
    const savedLevel = localStorage.getItem('current_difficulty_level') as DifficultyLevel;
    const savedTab = localStorage.getItem('current_lesson_tab') as LessonTab;
    
    if (savedLevel) set({ currentLevel: savedLevel });
    if (savedTab) set({ currentTab: savedTab });
  },
}));
