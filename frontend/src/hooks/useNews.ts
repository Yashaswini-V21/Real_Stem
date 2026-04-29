import { useEffect, useState, useCallback, useRef } from 'react';
import { newsApi } from '../services/api';
import { NewsItem } from '../types/news';

// --- Types ---

export interface NewsParams {
  limit?: number;
  offset?: number;
  stemOnly?: boolean;
  topic?: string;
  breakingOnly?: boolean;
}

interface CacheEntry {
  data: NewsItem[];
  timestamp: number;
}

const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes in milliseconds
const POLLING_INTERVAL = 30 * 1000; // 30 seconds for breaking news

// --- Cache ---

const newsCache = new Map<string, CacheEntry>();

const getCacheKey = (params: NewsParams): string => {
  return JSON.stringify({
    limit: params.limit || 12,
    offset: params.offset || 0,
    stemOnly: params.stemOnly !== false,
    topic: params.topic || 'all',
  });
};

const isCacheValid = (cacheKey: string): boolean => {
  const entry = newsCache.get(cacheKey);
  if (!entry) return false;
  
  const now = Date.now();
  return now - entry.timestamp < CACHE_DURATION;
};

const getFromCache = (cacheKey: string): NewsItem[] | null => {
  if (isCacheValid(cacheKey)) {
    return newsCache.get(cacheKey)?.data || null;
  }
  
  newsCache.delete(cacheKey);
  return null;
};

const setCache = (cacheKey: string, data: NewsItem[]): void => {
  newsCache.set(cacheKey, {
    data,
    timestamp: Date.now(),
  });
};

// --- Hook ---

export const useNews = (params: NewsParams = { limit: 12, offset: 0, stemOnly: true }) => {
  // State
  const [news, setNews] = useState<NewsItem[]>([]);
  const [breakingNews, setBreakingNews] = useState<NewsItem[]>([]);
  const [trendingNews, setTrendingNews] = useState<NewsItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [total, setTotal] = useState(0);

  // Refs for pagination and polling
  const currentOffsetRef = useRef(params.offset || 0);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Action: Fetch news with caching
  const fetchNews = useCallback(
    async (newParams?: NewsParams) => {
      const finalParams = newParams || params;
      const cacheKey = getCacheKey(finalParams);

      try {
        setIsLoading(true);
        setError(null);

        // Check cache first
        const cachedData = getFromCache(cacheKey);
        if (cachedData) {
          setNews(cachedData);
          setIsLoading(false);
          return;
        }

        // Fetch from API
        const response = await newsApi.getNews({
          limit: finalParams.limit || 12,
          offset: finalParams.offset || 0,
          stemOnly: finalParams.stemOnly !== false,
        });

        let filteredItems = response.items;

        // Client-side filtering by topic
        if (finalParams.topic) {
          filteredItems = filteredItems.filter(
            (item) =>
              item.category.toLowerCase() === finalParams.topic?.toLowerCase()
          );
        }

        // Cache the result
        setCache(cacheKey, filteredItems);

        setNews(filteredItems);
        setTotal(response.total);
        setHasMore(
          (finalParams.offset || 0) + (finalParams.limit || 12) < response.total
        );
      } catch (err: any) {
        const errorMessage = err.message || 'Failed to fetch news';
        setError(errorMessage);
        setNews([]);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  // Action: Fetch breaking news
  const fetchBreakingNews = useCallback(async () => {
    try {
      setError(null);
      const data = await newsApi.getBreakingNews();
      setBreakingNews(data);
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to fetch breaking news';
      console.error('Breaking news error:', errorMessage);
      setError(errorMessage);
    }
  }, []);

  // Action: Fetch trending news
  const fetchTrendingNews = useCallback(async () => {
    try {
      setError(null);
      const data = await newsApi.getTrendingNews();
      setTrendingNews(data);
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to fetch trending news';
      console.error('Trending news error:', errorMessage);
      setError(errorMessage);
    }
  }, []);

  // Action: Load more (infinite scroll)
  const loadMore = useCallback(async () => {
    if (!hasMore || isLoading) return;

    const nextOffset = currentOffsetRef.current + (params.limit || 12);
    currentOffsetRef.current = nextOffset;

    try {
      setIsLoading(true);
      const response = await newsApi.getNews({
        limit: params.limit || 12,
        offset: nextOffset,
        stemOnly: params.stemOnly !== false,
      });

      let filteredItems = response.items;

      if (params.topic) {
        filteredItems = filteredItems.filter(
          (item) =>
            item.category.toLowerCase() === params.topic?.toLowerCase()
        );
      }

      setNews((prevNews) => [...prevNews, ...filteredItems]);
      setHasMore(nextOffset + (params.limit || 12) < response.total);
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to load more news';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [params, hasMore, isLoading]);

  // Effect: Initial fetch on mount
  useEffect(() => {
    fetchNews(params);
  }, [params.limit, params.offset, params.stemOnly, params.topic, fetchNews]);

  // Effect: Fetch breaking news on mount
  useEffect(() => {
    fetchBreakingNews();
  }, [fetchBreakingNews]);

  // Effect: Fetch trending news on mount
  useEffect(() => {
    fetchTrendingNews();
  }, [fetchTrendingNews]);

  // Effect: Poll for breaking news every 30 seconds
  useEffect(() => {
    pollingIntervalRef.current = setInterval(() => {
      fetchBreakingNews();
    }, POLLING_INTERVAL);

    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, [fetchBreakingNews]);

  // Effect: Reset offset when params change
  useEffect(() => {
    currentOffsetRef.current = params.offset || 0;
  }, [params.offset]);

  return {
    // State
    news,
    breakingNews,
    trendingNews,
    isLoading,
    error,
    hasMore,
    total,

    // Actions
    fetchNews,
    fetchBreakingNews,
    fetchTrendingNews,
    loadMore,
  };
};
};
