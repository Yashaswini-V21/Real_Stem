import React, { useEffect, useState } from 'react';
import { NewsItem } from '../types/news';

interface NewsFeedProps {
  category?: string;
}

const NewsFeed: React.FC<NewsFeedProps> = ({ category }) => {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch news
    setLoading(false);
  }, [category]);

  return (
    <div className="news-feed">
      <h1>STEM News Feed</h1>
      {loading ? (
        <div>Loading...</div>
      ) : (
        <div className="news-list">
          {news.map((item) => (
            <div key={item.id} className="news-item">
              <h3>{item.title}</h3>
              <p>{item.description}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default NewsFeed;
