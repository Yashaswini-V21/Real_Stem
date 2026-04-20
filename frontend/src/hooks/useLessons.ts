import { useEffect, useState } from 'react';
import { getLessons } from '../services/api';
import { Lesson } from '../types/lesson';

export const useLessons = (topic?: string, level?: number) => {
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchLessons = async () => {
      try {
        setLoading(true);
        const response = await getLessons(topic, level);
        setLessons(response.data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchLessons();
  }, [topic, level]);

  return { lessons, loading, error };
};
