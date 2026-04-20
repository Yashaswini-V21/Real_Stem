import { create } from 'zustand';
import { Lesson } from '../types/lesson';

interface LessonState {
  lessons: Lesson[];
  currentLesson: Lesson | null;
  setLessons: (lessons: Lesson[]) => void;
  setCurrentLesson: (lesson: Lesson) => void;
  addLesson: (lesson: Lesson) => void;
}

export const useLessonStore = create<LessonState>((set) => ({
  lessons: [],
  currentLesson: null,
  setLessons: (lessons) => set({ lessons }),
  setCurrentLesson: (lesson) => set({ currentLesson: lesson }),
  addLesson: (lesson) => set((state) => ({ lessons: [...state.lessons, lesson] })),
}));
