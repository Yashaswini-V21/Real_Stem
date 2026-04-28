# RealSTEM - AI-Powered STEM Education Platform

![Status](https://img.shields.io/badge/status-In%20Development-yellow?style=for-the-badge)
![Python](https://img.shields.io/badge/backend-FastAPI%2B-green?style=for-the-badge)
![TypeScript](https://img.shields.io/badge/frontend-React%20%2B%20TypeScript-blue?style=for-the-badge)
![AI](https://img.shields.io/badge/AI-Claude%20%2B%20Gemini-purple?style=for-the-badge)

> **Transform real-world news into adaptive, standards-aligned STEM lessons with AI-powered personalization and global collaboration.**

---

## 📋 Project Overview

RealSTEM is a comprehensive educational platform that bridges the gap between current events and STEM education. It aggregates relevant news, generates adaptive lessons for multiple educational levels, provides interactive simulations, enables real-time collaboration, and connects learning to career opportunities.

### Core Mission
- **News-to-Lessons:** Convert breaking news into standards-aligned STEM curriculum
- **Adaptive Learning:** Content customized for grades K-12 and college levels
- **AI-Powered:** Personalized recommendations using ML models
- **Global Collaboration:** Real-time tools for students worldwide
- **Career Connected:** Show practical applications and career paths

---

## 🎯 What We've Built

### ✅ Backend Infrastructure & APIs
- **FastAPI Core**: Fully implemented async REST API with modular routers.
- **Authentication System**:
  - JWT-based OAuth2 flow using `python-jose`.
  - Secure password hashing via `passlib` (BCrypt).
  - Role-Based Access Control (RBAC) supporting Students, Teachers, and Admins.
- **AI-Driven Services**:
  - `ai_generator`: Logic for 5-tier adaptive content generation.
  - `video_creator`: Hooks for automated educational video assembly.
  - `simulation_builder`: Framework for self-contained `Three.js`/`Cannon.js` interactive labs.
- **STEM Intelligence**:
  - `classifier.py`: DistilBERT-based ML model for filtering high-relevance educational news.
- **Enhanced Data Models**:
  - `Lesson`: Support for 5 distinct academic levels (Elementary to College) per lesson.
  - `Collaboration`: WebSocket-ready models for real-time team learning.

### ✅ Frontend Intelligence & UX
- **Type-Safe API Client**: Built with Axios, featuring request/response interceptors and automated token management.
- **Dynamic News Dashboard**:
  - Real-time filtering by STEM topics (Physics, Chemistry, Biology, etc.).
  - "Teacher-Only" generation tools to trigger AI lesson creation from news cards.
  - Responsive layout with Tailwind CSS.
- **Advanced Lesson Viewer**:
  - Multi-tab learning environment (Video, Simulation, Practice, Careers).
  - Real-time learning progress and session time tracking.
  - 5-Tier academic level selector for personalized difficulty.
- **Custom React Hooks**:
  - `useNews`: Advanced hook for managing filtered/paginated STEM updates.
  - `useLessons`: Logic for fetching and interacting with adaptive content.

### ✅ Frontend Structure
- **React 18 + TypeScript** - Modern, type-safe UI framework
- **Vite Build Tool** - Lightning-fast development and production builds
- **Components** (8 core components):
  - **NewsFeed** - STEM news aggregation with topic filtering
  - **LessonViewer** - Adaptive lesson display with 5-tier difficulty levels
  - **VideoPlayer** - Custom bespoke video player with:
    - Interactive transcript sync (click to jump to timestamp)
    - Real-time transcript line highlighting
    - Custom HUD with volume, progress, and playback controls
    - Study notes export functionality
  - **Simulation** - Interactive STEM labs with adjustable parameters
  - **DebateArena** - Real-time AI-moderated debate with:
    - Multi-phase workflow (Recruiting → Research → Debate → Results)
    - PRO/CON team formations
    - AI Fact-checking module with verification badges
    - Live audience and timer HUD
    - Moderator logic scoring (Logic/Evidence/Fallacies)
  - **CareerExplorer** - Career pathway discovery with:
    - Salary comparisons (regional data charts)
    - Educational journey timelines (HS → College → Career)
    - Success stories from similar profiles
    - "Day in the Life" video streams
    - Career simulation labs
    - AI Mentor chatbot trained on professional interviews
  - **ImpactDashboard** - Student achievement showcase with:
    - Summary metrics (Lessons, Countries, Challenges, Concepts)
    - Skills radar chart (Critical Thinking, Problem Solving, Collaboration, etc.)
    - Real-world impact timeline with proof links and photos
    - Global network (mentors & peer connections)
    - Badges & achievements gallery
    - Projects portfolio with expandable details
    - Social sharing and PDF export functionality
  - **GlobalCollaboration** - Real-time collaboration tools

### ✅ State Management & Services
- **Zustand Stores** - User, Lesson, Notification state
- **API Service** - Axios-based REST client
- **WebSocket Service** - Real-time communication
- **Auth Service** - JWT token management
- **Custom Hooks** - useNews, useLessons, useRealtime

### ✅ Type System
- **TypeScript Interfaces** - Lesson, News, User types
- **Type-Safe** - All API responses and state are typed

### ✅ Utilities & Helpers
- **Formatters** - Date, time, currency formatting
- **Validators** - Email, password, username, URL validation
- **Utils** - Pagination, rate limiting, logging

### ✅ Documentation & Configuration
- **API Documentation** - Comprehensive endpoint reference
- **Architecture Guide** - System design overview
- **Setup Instructions** - Step-by-step deployment guide
- **Contributing Guidelines** - Development workflow
- **Docker Support** - Complete containerization setup
- **.gitignore** - Python, Node, ML models, sensitive data

---

## 📁 Complete Project Structure

```
RealSTEM/
│
├── 🐍 backend/                              # FastAPI Python Backend
│   ├── main.py                              # FastAPI app entry point
│   ├── config.py                            # Pydantic settings + 70+ config vars
│   ├── requirements.txt                     # 50+ production dependencies
│   │
│   ├── models/                              # SQLAlchemy 2.0 ORM Models
│   │   ├── user.py                          # User (Student/Teacher/Admin)
│   │   ├── news.py                          # NewsArticle with STEM scoring
│   │   ├── lesson.py                        # Adaptive multi-level lessons
│   │   └── progress.py                      # StudentProgress tracking
│   │
│   ├── services/                            # Business Logic Layer
│   │   ├── news_aggregator.py               # News fetching & aggregation
│   │   ├── ai_generator.py                  # AI lesson generation
│   │   ├── video_creator.py                 # Video content generation
│   │   ├── simulation_builder.py            # Interactive simulations
│   │   ├── career_matcher.py                # Career recommendations
│   │   └── translation.py                   # Multi-language support
│   │
│   ├── api/                                 # API Route Endpoints
│   │   ├── news.py                          # News API routes
│   │   ├── lessons.py                       # Lesson API routes
│   │   ├── users.py                         # User management routes
│   │   ├── collaboration.py                 # Collaboration routes
│   │   └── analytics.py                     # Analytics routes
│   │
│   ├── ml/                                  # Machine Learning Models
│   │   ├── classifier.py                    # Content classification
│   │   ├── difficulty_adapter.py            # Adaptive difficulty
│   │   └── career_recommender.py            # Career recommendations
│   │
│   ├── utils/                               # Utility Functions
│   │   ├── logger.py                        # Logging configuration
│   │   ├── validators.py                    # Data validation
│   │   └── cache.py                         # Redis caching
│   │
│   ├── tasks/                               # Celery Background Tasks
│   │   ├── news_scraper.py                  # News scraping task
│   │   └── lesson_generator.py              # Async lesson generation
│   │
│   ├── prompts/                             # AI Prompt Templates
│   │   ├── lesson_generator.txt             # Lesson generation prompt
│   │   ├── video_script.txt                 # Video script prompt
│   │   ├── assessment_creator.txt           # Assessment prompt
│   │   └── career_connector.txt             # Career connection prompt
│   │
│   ├── scripts/                             # Utility Scripts
│   │   ├── init_db.py                       # Database initialization
│   │   ├── seed_data.py                     # Database seeding
│   │   └── train_classifier.py              # ML model training
│   │
│   └── tests/                               # Unit & Integration Tests
│
├── ⚛️  frontend/                             # React TypeScript Frontend
│   ├── src/
│   │   ├── App.tsx                          # Main app component
│   │   ├── index.tsx                        # React entry point
│   │   │
│   │   ├── components/                      # React Components
│   │   │   ├── NewsFeed.tsx                 # STEM news feed
│   │   │   ├── LessonViewer.tsx             # Lesson display
│   │   │   ├── VideoPlayer.tsx              # Video playback
│   │   │   ├── Simulation.tsx               # Interactive simulation
│   │   │   ├── DebateArena.tsx              # Debate collaboration
│   │   │   ├── CareerExplorer.tsx           # Career paths
│   │   │   ├── ImpactDashboard.tsx          # Progress dashboard
│   │   │   └── GlobalCollaboration.tsx      # Real-time collaboration
│   │   │
│   │   ├── services/                        # API & External Services
│   │   │   ├── api.ts                       # Axios REST client
│   │   │   ├── websocket.ts                 # WebSocket real-time
│   │   │   └── auth.ts                      # Authentication
│   │   │
│   │   ├── store/                           # Zustand State Management
│   │   │   ├── userStore.ts                 # User state
│   │   │   ├── lessonStore.ts               # Lesson state
│   │   │   └── notificationStore.ts         # Notifications
│   │   │
│   │   ├── hooks/                           # Custom React Hooks
│   │   │   ├── useNews.ts                   # News fetching
│   │   │   ├── useLessons.ts                # Lesson fetching
│   │   │   └── useRealtime.ts               # WebSocket subscriptions
│   │   │
│   │   ├── types/                           # TypeScript Interfaces
│   │   │   ├── lesson.ts                    # Lesson type
│   │   │   ├── news.ts                      # News type
│   │   │   ├── user.ts                      # User type
│   │   │   ├── career.ts                    # Career pathways & education
│   │   │   └── impact.ts                    # Student impact & achievements
│   │   │
│   │   └── utils/                           # Utility Functions
│   │       ├── formatters.ts                # Date/time/currency formatting
│   │       └── validators.ts                # Input validation
│   │
│   ├── package.json                         # Frontend dependencies
│   ├── tsconfig.json                        # TypeScript config
│   └── vite.config.ts                       # Vite build config
│
├── 📊 ml/                                   # Machine Learning
│   ├── data/                                # Training datasets
│   ├── notebooks/                           # Jupyter notebooks
│   └── models/                              # Trained model storage
│
├── 🐳 docker/                               # Docker & Deployment
│   ├── Dockerfile                           # General Docker image
│   ├── Dockerfile.backend                   # Backend image
│   ├── Dockerfile.frontend                  # Frontend image
│   └── docker-compose.yml                   # Multi-container setup
│
├── 📚 docs/                                 # Documentation
│   ├── API.md                               # API reference
│   ├── SETUP.md                             # Setup instructions
│   ├── ARCHITECTURE.md                      # System architecture
│   └── CONTRIBUTING.md                      # Contribution guide
│
├── .env.example                             # Environment template (80+ vars)
├── .gitignore                               # Git ignore rules
└── README.md                                # This file
```

---

## 🚀 Technology Stack

### Backend
| Layer | Technology |
|-------|-----------|
| Framework | FastAPI 0.104.1 |
| Server | Uvicorn 0.24.0 |
| ORM | SQLAlchemy 2.0.23 |
| Database | PostgreSQL 15 |
| Cache | Redis 7 |
| AI/ML | Claude API, Gemini, Transformers, PyTorch |
| Task Queue | Celery 5.3.4 |
| Auth | JWT, Passlib, bcrypt |
| Validation | Pydantic 2.5 |

### Frontend
| Layer | Technology |
|-------|-----------|
| Framework | React 18.2.0 |
| Language | TypeScript 5.3 |
| Build Tool | Vite 5.0.8 |
| Router | React Router 6.20 |
| HTTP | Axios 1.6.2 |
| State | Zustand 4.4.7 |
| Real-time | WebSockets |

### Data & Integration
| Service | Purpose |
|---------|---------|
| NewsAPI | News aggregation |
| Reddit API | Community content |
| Google Cloud TTS | Audio generation |
| DeepL | Translation |

---

## 📊 Database Models

### User Model
- Roles: Student, Teacher, Admin
- Preferences: JSON-based settings
- Profiles: Grade level (students), Subjects (teachers)
- Authentication: Password hash, JWT tokens
- Metrics: Last active, created date

### NewsArticle Model
- Multi-source aggregation (NewsAPI, Reddit, RSS)
- STEM relevance scoring (0-1 confidence)
- Topics: Physics, Chemistry, AI, Engineering, etc.
- Breaking news flag
- Engagement metrics: Views, engagement score

### Lesson Model
- **Adaptive Content**: Elementary → College levels
- **Standards Aligned**: NGSS, Common Core, etc.
- **Multi-Media**: Videos, simulations, career paths
- **Status**: Draft, Published, Archived
- **Engagement**: Views, completions, ratings

### StudentProgress Model
- **Granular Tracking**: Time spent, activities, assessments
- **Conceptual Progress**: Mastered vs. struggling concepts
- **Collaboration**: Team work, contributions
- **Adaptive**: Difficulty level adjustments
- **Engagement**: Help requests, attempts, metadata

---

## ⚙️ Configuration

**70+ Environment Variables** configured through:
- `config.py` - Pydantic BaseSettings
- `.env` file - Local development
- Environment variables - Production deployment

**Key Configuration Categories**:
- 🔐 Security (JWT, encryption keys)
- 🗄️ Database (PostgreSQL, Redis)
- 🤖 AI APIs (Claude, Gemini, OpenAI, Hugging Face)
- 📰 News APIs (NewsAPI, Reddit)
- 🎤 Media APIs (Google Cloud TTS, DeepL)
- 📧 Email (SMTP configuration)
- 🚀 Feature Flags (9 toggleable features)

---

## 📦 Dependencies

**Backend**: 50+ production packages
- Web: FastAPI, Uvicorn
- Data: SQLAlchemy, Psycopg2, Alembic
- AI/ML: Anthropic, Google Generative AI, Transformers, PyTorch
- Data Processing: Pandas, NumPy, BeautifulSoup, Feedparser
- Background: Celery, Redis
- Security: Passlib, PyJWT, Cryptography
- Media: Google Cloud TTS, MoviePy, DeepL

**Frontend**: React, TypeScript, Axios, Zustand, Vite

---

## 🛠️ Getting Started

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example ../.env
python scripts/init_db.py
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Docker Deployment
```bash
docker-compose up --build
```

---

## 📚 Documentation

- **[API Reference](docs/API.md)** - Complete endpoint documentation
- **[Architecture Guide](docs/ARCHITECTURE.md)** - System design & data flow
- **[Setup Instructions](docs/SETUP.md)** - Detailed deployment steps
- **[Contributing Guide](docs/CONTRIBUTING.md)** - Development workflow

---

## ✨ Key Features

| Feature | Status | Details |
|---------|--------|---------|
| User Authentication | ✅ | JWT tokens, role-based access |
| News Aggregation | ✅ | Multi-source news feeds |
| AI Lesson Generation | ✅ | Claude/Gemini powered |
| Adaptive Content | ✅ | 5 educational levels |
| Video Integration | ✅ | YouTube, custom videos |
| Interactive Simulations | ✅ | PhET & custom |
| Real-time Collaboration | 🚧 | WebSocket support |
| Career Matching | ✅ | ML-based recommendations |
| Multi-language | ✅ | DeepL integration |
| Analytics Dashboard | ✅ | Progress tracking |
| Global Challenges | 🚧 | Gamification features |
| Teacher Tools | 🚧 | Classroom management |

---

## 📝 Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/feature-name
   ```

2. **Develop & Test**
   ```bash
   # Backend
   cd backend && pytest
   
   # Frontend
   cd frontend && npm test
   ```

3. **Code Quality**
   ```bash
   # Backend
   black . && flake8 . && mypy .
   
   # Frontend
   npm run lint && npm run format
   ```

4. **Commit & Push**
   ```bash
   git commit -m "feat: description"
   git push origin feature/feature-name
   ```

5. **Create Pull Request**

---

## 🔒 Security

- ✅ Password hashing (bcrypt)
- ✅ JWT authentication
- ✅ CORS protection
- ✅ Input validation (Pydantic)
- ✅ SQL injection prevention
- ✅ Rate limiting
- ✅ Environment-based secrets

---

## 📊 Project Stats

- **Models**: 4 comprehensive SQLAlchemy models
- **API Endpoints**: 15+ fully documented endpoints
- **Components**: 8 React components
- **Services**: 6 backend services
- **ML Modules**: 3 machine learning models
- **API Keys**: Support for 10+ external APIs
- **Languages**: Python, TypeScript, JavaScript

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT License - see LICENSE file for details

---

## 📧 Contact & Support

- Documentation: See `docs/` folder
- Issues: Create GitHub issue
- Email: support@realstem.edu

---

## 🎓 Educational Philosophy

RealSTEM is built on the principle that students learn best when:
- **Real**: Connected to current events and real-world impact
- **Adaptive**: Personalized to their learning level and pace
- **Collaborative**: Learning with peers globally
- **Career-Focused**: Understanding practical applications
- **Engaging**: Using multimedia and interactive tools

---

**Last Updated**: April 20, 2026  
**Version**: 1.0.0  
**Status**: Active Development


---

## 🔄 How It Works

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐     ┌────────────────┐
│  📡 News Input   │ ──▶ │  🎯 STEM Scoring  │ ──▶ │  🧠 AI Drafting  │ ──▶ │  👩‍🏫 Review    │
│  (Any headline)  │     │  (Subject match)  │     │  (Full lesson)   │     │  (Edit & save) │
└─────────────────┘     └──────────────────┘     └─────────────────┘     └────────────────┘
```

---

## 📸 Screenshots

> *Coming soon — UI polish in progress*

---

<p align="center">
  <sub>Built with 🧠 for the future of STEM education</sub>
</p>
