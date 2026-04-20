export interface NewsItem {
  id: string;
  title: string;
  description: string;
  content: string;
  source: string;
  sourceUrl: string;
  category: string;
  imageUrl?: string;
  publishedAt: Date;
  createdAt: Date;
  updatedAt: Date;
}
