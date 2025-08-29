# Backend API Integration Guide

This document describes how to integrate the frontend with the backend authentication and database persistence system.

## Base URL
```
http://127.0.0.1:8000
```

## Authentication Flow

### 1. Google OAuth2 Login
**Endpoint:** `POST /auth/google`

**Request Body:**
```json
{
  "id_token": "google_id_token_from_frontend"
}
```

**Response:**
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer"
}
```

### 2. Get Current User
**Endpoint:** `GET /auth/me`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": "user_id",
  "email": "user@example.com",
  "full_name": "User Name",
  "google_id": "google_user_id",
  "picture_url": "https://...",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### 3. Logout
**Endpoint:** `POST /auth/logout`

**Headers:**
```
Authorization: Bearer <access_token>
```

## Resume Management

All resume endpoints require authentication header: `Authorization: Bearer <access_token>`

### Create Resume
**Endpoint:** `POST /resumes/`

**Request Body:**
```json
{
  "title": "My Resume",
  "resume_data": {
    "personalInfo": {
      "fullName": "John Doe",
      "email": "john@example.com",
      "phone": "+1234567890",
      "location": "City, State",
      "linkedin": "linkedin.com/in/johndoe",
      "github": "github.com/johndoe"
    },
    "summary": "Professional summary...",
    "experience": [
      {
        "company": "Company Name",
        "position": "Job Title",
        "startDate": "2020-01",
        "endDate": "2023-12",
        "description": "Job description..."
      }
    ],
    "education": [
      {
        "institution": "University Name",
        "degree": "Bachelor's Degree",
        "field": "Computer Science",
        "startDate": "2016-09",
        "endDate": "2020-05",
        "gpa": "3.8"
      }
    ],
    "skills": [
      {
        "category": "Programming Languages",
        "items": ["JavaScript", "Python", "Java"]
      }
    ],
    "projects": [
      {
        "name": "Project Name",
        "description": "Project description...",
        "technologies": ["React", "Node.js"],
        "link": "https://github.com/user/project"
      }
    ]
  }
}
```

### List Resumes
**Endpoint:** `GET /resumes/`

### Get Resume
**Endpoint:** `GET /resumes/{resume_id}`

### Update Resume
**Endpoint:** `PUT /resumes/{resume_id}`

### Delete Resume
**Endpoint:** `DELETE /resumes/{resume_id}`

## Application Kit Generation

### Generate Application Kit
**Endpoint:** `POST /application-kits/`

**Request Body:**
```json
{
  "resume_id": "resume_id_here",
  "job_description": "Job description text..."
}
```

### List Application Kits
**Endpoint:** `GET /application-kits/`

### Get Application Kit
**Endpoint:** `GET /application-kits/{kit_id}`

## Resume Analysis

### Create Analysis
**Endpoint:** `POST /analysis/`

**Request Body:**
```json
{
  "resume_id": "resume_id_here",
  "job_description": "Job description text...",
  "experience_level": "entry|mid|senior"
}
```

### List Analyses
**Endpoint:** `GET /analysis/`

## Future Enhancements

### Phase 2: Asynchronous Task Processing (Optional Future)

If needed later, we can introduce a background task queue so long-running AI tasks don't block HTTP requests.

-   Possible technologies: Celery with Redis, RQ, Dramatiq, or simple background tasks
-   Benefit: API can respond instantly while tasks run in the background
-   Implementation: Convert `create_kit` and `create_analysis` to enqueue a job and poll for results

### Phase 3: Advanced AI with LangGraph

To create more sophisticated and reliable AI agents, we will migrate the AI logic to LangGraph.

-   **Technology:** LangGraph
-   **Benefit:** Allows for building complex, stateful AI workflows with cycles, tool usage, and better error handling. This will enable more powerful features like multi-step resume analysis, interactive feedback loops, and agent-based job searching.
-   **Implementation:** The core functions in `ai_service.py` will be replaced with LangGraph graphs.

## Frontend Integration Steps

### 1. Replace localStorage with API calls

Instead of storing resumes in localStorage, use the backend API:

```javascript
// OLD: localStorage.setItem('resumes', JSON.stringify(resumes))
// NEW: POST /resumes/ with authentication

// OLD: JSON.parse(localStorage.getItem('resumes') || '[]')
// NEW: GET /resumes/ with authentication
```

### 2. Implement Google Sign-In

Update your Google Sign-In to use the backend:

```javascript
// After successful Google Sign-In
const response = await fetch('http://127.0.0.1:8000/auth/google', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    id_token: googleResponse.credential
  })
});

const { access_token } = await response.json();
localStorage.setItem('access_token', access_token);
```

### 3. Add Authentication Headers

All API calls should include the auth header:

```javascript
const token = localStorage.getItem('access_token');
const response = await fetch('http://127.0.0.1:8000/resumes/', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

### 4. Handle Authentication Errors

```javascript
if (response.status === 401) {
  // Token expired or invalid
  localStorage.removeItem('access_token');
  // Redirect to login
}
```

### 5. Update State Management

Replace localStorage usage in your React components with API calls and proper state management.

## Environment Setup

1. Make sure MongoDB is running on `localhost:27017` (or use Atlas)
2. Set up Google OAuth2 credentials in `.env` file
3. Start the backend server: `uvicorn app.main:app --reload`

## CORS Configuration

The backend is configured to allow requests from your frontend. Make sure your frontend URL is included in the CORS origins if needed.

## Error Handling

The API uses standard HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Internal Server Error

All error responses include a `detail` field with a description of the error.
