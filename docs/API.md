# API Documentation

## RealSTEM API Reference

### Base URL
```
http://localhost:8000/api
```

### Authentication
All protected endpoints require a bearer token in the Authorization header:
```
Authorization: Bearer {access_token}
```

## News Endpoints

### Get All News
```
GET /news
Query Parameters:
  - category: string (optional)
  - limit: integer (default: 20)

Response: { "news": [...] }
```

### Get News Detail
```
GET /news/{news_id}
Response: { "id", "title", "content", ... }
```

## Lessons Endpoints

### Get All Lessons
```
GET /lessons
Query Parameters:
  - topic: string (optional)
  - level: integer (optional)
  - limit: integer (default: 20)

Response: { "lessons": [...] }
```

### Get Lesson Detail
```
GET /lessons/{lesson_id}
Response: Lesson object
```

### Complete Lesson
```
POST /lessons/{lesson_id}/complete
Body: { "user_id": "string" }
Response: { "success": true }
```

## Users Endpoints

### Register
```
POST /users/register
Body: { "email", "username", "password", "fullName" }
Response: { "success": true, "user_id": "string" }
```

### Login
```
POST /users/login
Body: { "email", "password" }
Response: { "access_token": "string", "token_type": "bearer" }
```

### Get Profile
```
GET /users/profile/{user_id}
Response: User object
```

## Analytics Endpoints

### Get Dashboard
```
GET /analytics/dashboard/{user_id}
Response: { "learning_progress": {...}, "impact_metrics": {...} }
```

### Get User Progress
```
GET /analytics/progress/{user_id}
Response: { "completed_lessons": [...], "in_progress": [...] }
```

## WebSocket

Connect to real-time updates:
```
ws://localhost:8000/ws
```

### Message Format
```json
{
  "type": "event_type",
  "payload": { ... }
}
```
