# Setup Instructions

## Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

## Backend Setup

### 1. Create Virtual Environment
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp ../.env.example ../.env
# Edit .env with your configuration
```

### 4. Initialize Database
```bash
python scripts/init_db.py
python scripts/seed_data.py
```

### 5. Start Backend
```bash
python main.py
```

Backend will be available at http://localhost:8000

## Frontend Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Start Development Server
```bash
npm run dev
```

Frontend will be available at http://localhost:3000

## Docker Deployment

### 1. Build and Run
```bash
cd ..
docker-compose up --build
```

### 2. Services
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## Database Setup

### Create Database
```bash
psql -U postgres -c "CREATE DATABASE realstem;"
```

### Run Migrations
```bash
cd backend
alembic upgrade head
```

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## Development Workflow

1. Create a feature branch: `git checkout -b feature/feature-name`
2. Make changes and test
3. Commit: `git commit -m "Description"`
4. Push: `git push origin feature/feature-name`
5. Create a Pull Request

## Troubleshooting

### Database Connection Error
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env
- Verify database exists: `psql -U postgres -l`

### Redis Connection Error
- Ensure Redis is running
- Check REDIS_URL in .env
- Test: `redis-cli ping`

### Port Already in Use
- Backend: Change BACKEND_PORT in .env
- Frontend: Change port in vite.config.ts
- Use `lsof -i :8000` to find processes
