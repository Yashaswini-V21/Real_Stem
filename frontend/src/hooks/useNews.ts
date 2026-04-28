import { useEffect, useState } from 'react';
import { newsApi } from '../services/api';
import { NewsItem } from '../types/news';

export interface NewsFilters {
  limit?: number;
  offset?: number;
  stemOnly?: boolean;
  topic?: string;
  breakingOnly?: boolean;
}

export const useNews = (filters: NewsFilters = { limit: 12, offset: 0, stemOnly: true }) => {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    const fetchNews = async () => {
      try {
        setLoading(true);
        // We'll use getNews for general feed, but filter on client for topics since backend schema was simplified
        const response = await newsApi.getNews({
            limit: filters.limit,
            offset: filters.offset,
            stemOnly: filters.stemOnly
        });
        
        let filteredItems = response.items;
        
        if (filters.topic) {
            filteredItems = filteredItems.filter(item => 
                item.category.toLowerCase() === filters.topic?.toLowerCase()
            );
        }

        setNews(filteredItems);
        setTotal(response.total);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch news');
      } finally {
        setLoading(false);
      }
    };

    fetchNews();
  }, [filters.limit, filters.offset, filters.stemOnly, filters.topic, filters.breakingOnly]);

  return { news, total, loading, error };
};
