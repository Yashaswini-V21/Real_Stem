import { useEffect, useState, useCallback, useRef } from 'react';
import { lessonsApi } from '../services/api';
import { Lesson } from '../types/lesson';

// --- Types ---

export interface LessonParams {
  status?: string;
  level?: string;
  subject?: string;
  limit?: number;
  offset?: number;
}

interface LessonCacheEntry {
  data: Lesson;
  timestamp: number;
}

const LESSON_CACHE_DURATION = 10 * 60 * 1000; // 10 minutes

// --- Cache ---

const lessonCache = new Map<string, LessonCacheEntry>();

const getCachedLesson = (id: string | number): Lesson | null => {
  const cacheKey = id.toString();
  const entry = lessonCache.get(cacheKey);

  if (!entry) return null;

  const now = Date.now();
  if (now - entry.timestamp > LESSON_CACHE_DURATION) {
    lessonCache.delete(cacheKey);
    return null;
  }

  return entry.data;
};

const setCachedLesson = (id: string | number, lesson: Lesson): void => {
  const cacheKey = id.toString();
  lessonCache.set(cacheKey, {
    data: lesson,
    timestamp: Date.now(),
  });
};

// --- Hook ---

export const useLessons = (params: LessonParams = { level: 'high', limit: 20 }) => {
  // State
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [currentLesson, setCurrentLesson] = useState<Lesson | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Refs for tracking
  const optimisticRatingsRef = useRef<Map<string, number>>(new Map());

  // Action: Fetch lessons list
  const fetchLessons = useCallback(
    async (newParams?: LessonParams) => {
      const finalParams = newParams || params;

      try {
        setIsLoading(true);
        setError(null);

        const response = await lessonsApi.getLessons({
          status: finalParams.status,
          level: finalParams.level,
          subject: finalParams.subject,
          limit: finalParams.limit || 20,
          offset: finalParams.offset || 0,
        });

        setLessons(response.items);
      } catch (err: any) {
        const errorMessage = err.message || 'Failed to fetch lessons';
        setError(errorMessage);
        setLessons([]);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  // Action: Fetch single lesson by ID
  const fetchLessonById = useCallback(async (id: string | number) => {
    try {
      setIsLoading(true);
      setError(null);

      // Check cache first
      const cachedLesson = getCachedLesson(id);
      if (cachedLesson) {
        setCurrentLesson(cachedLesson);
        setIsLoading(false);
        return;
      }

      // Fetch from API
      const lesson = await lessonsApi.getLessonById(id);

      // Cache the result
      setCachedLesson(id, lesson);

      setCurrentLesson(lesson);
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to fetch lesson';
      setError(errorMessage);
      setCurrentLesson(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Action: Generate lesson from news
  const generateLesson = useCallback(
    async (newsId: string | number, breakingMode: boolean) => {
      try {
        setIsLoading(true);
        setError(null);

        const generatedLesson = await lessonsApi.generateLesson(newsId, breakingMode);

        // Cache the generated lesson
        setCachedLesson(generatedLesson.id, generatedLesson);

        // Add to lessons list
        setLessons((prev) => [generatedLesson, ...prev]);

        return generatedLesson;
      } catch (err: any) {
        const errorMessage = err.message || 'Failed to generate lesson';
        setError(errorMessage);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  // Action: Rate lesson (optimistic update)
  const rateLesson = useCallback(
    async (id: string | number, rating: number) => {
      const idStr = id.toString();

      try {
        // Optimistic update
        optimisticRatingsRef.current.set(idStr, rating);
        setError(null);

        // Sync with API
        await lessonsApi.rateLesson(id, rating);

        // Success - remove from optimistic updates
        optimisticRatingsRef.current.delete(idStr);
      } catch (err: any) {
        // Revert optimistic update on error
        optimisticRatingsRef.current.delete(idStr);

        const errorMessage = err.message || 'Failed to rate lesson';
        setError(errorMessage);
        throw err;
      }
    },
    []
  );

  // Action: Search lessons
  const searchLessons = useCallback(async (query: string) => {
    if (!query.trim()) {
      setLessons([]);
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      const response = await lessonsApi.searchLessons(query);
      setLessons(response.items);
    } catch (err: any) {
      const errorMessage = err.message || 'Search failed';
      setError(errorMessage);
      setLessons([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Effect: Initial fetch on mount
  useEffect(() => {
    fetchLessons(params);
  }, [params.level, params.subject, params.limit, fetchLessons]);

  return {
    // State
    lessons,
    currentLesson,
    isLoading,
    error,

    // Actions
    fetchLessons,
    fetchLessonById,
    generateLesson,
    rateLesson,
    searchLessons,
  };
};
