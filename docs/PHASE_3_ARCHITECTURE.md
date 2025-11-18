# Phase 3 System Architecture & Tech Stack

**Version:** 1.0
**Date:** October 23, 2025
**Status:** Planning
**Owner:** Engineering Team

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Principles](#architecture-principles)
3. [High-Level Architecture](#high-level-architecture)
4. [Technology Stack](#technology-stack)
5. [Backend Architecture](#backend-architecture)
6. [Frontend Architecture](#frontend-architecture)
7. [Database Design](#database-design)
8. [API Design](#api-design)
9. [Real-Time Communication](#real-time-communication)
10. [Security Architecture](#security-architecture)
11. [Deployment Architecture](#deployment-architecture)
12. [Development Workflow](#development-workflow)
13. [Migration Strategy](#migration-strategy)

---

## Overview

Phase 3 transforms Bizy AI from a CLI-only tool into a full-stack web application. The architecture is designed to:

- **Preserve existing functionality:** All Phase 1 & 2 features work in web app
- **Enable multi-device access:** Users can access from any browser
- **Support real-time updates:** Changes sync instantly across devices
- **Prepare for scale:** Architecture supports thousands of concurrent users
- **Maintain code reusability:** Core business logic shared between CLI and web

---

## Architecture Principles

### 1. **Separation of Concerns**
- **Backend:** Business logic, data access, AI integration
- **Frontend:** UI rendering, user interaction, state management
- **Database:** Data persistence, consistency, integrity

### 2. **Stateless API Design**
- No server-side session state (enables horizontal scaling)
- JWT tokens for authentication (stored in HttpOnly cookies)
- Redis for caching and temporary data

### 3. **API-First Development**
- RESTful API design with OpenAPI specification
- Backend and frontend developed independently
- API versioning for backward compatibility

### 4. **Real-Time by Default**
- WebSocket connections for instant updates
- Optimistic UI updates for perceived performance
- Fallback to polling for unreliable connections

### 5. **Security First**
- Authentication on all endpoints
- Input validation and sanitization
- Rate limiting and DDoS protection
- HTTPS only in production

### 6. **Test-Driven Development**
- Unit tests for business logic (80%+ coverage)
- Integration tests for API endpoints
- E2E tests for critical user flows
- Load testing before production

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Browser    │  │   Mobile     │  │     CLI      │          │
│  │  (React UI)  │  │  (PWA/Native)│  │   (Python)   │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                  │
│         └──────────────────┴──────────────────┘                  │
│                            │                                     │
└────────────────────────────┼─────────────────────────────────────┘
                             │
                    ┌────────┴─────────┐
                    │   HTTPS / WSS    │
                    └────────┬─────────┘
                             │
┌────────────────────────────┼─────────────────────────────────────┐
│                     API GATEWAY LAYER                            │
│                    ┌────────┴─────────┐                          │
│                    │   Nginx Reverse  │                          │
│                    │      Proxy       │                          │
│                    │  (SSL, CORS,     │                          │
│                    │   Rate Limiting) │                          │
│                    └────────┬─────────┘                          │
└────────────────────────────┼─────────────────────────────────────┘
                             │
                    ┌────────┴─────────┐
                    │                  │
        ┌───────────┴──────┐  ┌────────┴──────────┐
        │   HTTP/REST      │  │    WebSocket      │
        │   Requests       │  │   Connections     │
        └───────┬──────────┘  └────────┬──────────┘
                │                      │
┌───────────────┼──────────────────────┼───────────────────────────┐
│            APPLICATION LAYER                                     │
│               │                      │                           │
│        ┌──────┴──────┐        ┌──────┴──────┐                   │
│        │   FastAPI   │        │  Socket.io  │                   │
│        │   REST API  │        │   Server    │                   │
│        │             │        │             │                   │
│        │ ┌─────────┐ │        │ ┌─────────┐ │                   │
│        │ │ Routes  │ │        │ │Handlers │ │                   │
│        │ ├─────────┤ │        │ └─────────┘ │                   │
│        │ │Schemas  │ │        └─────────────┘                   │
│        │ ├─────────┤ │                │                          │
│        │ │Services │◄├────────────────┘                          │
│        │ └────┬────┘ │                                           │
│        └──────┼──────┘                                           │
│               │                                                  │
│        ┌──────┴─────────────────────┐                           │
│        │   Business Logic Layer     │                           │
│        │  ┌──────────────────────┐  │                           │
│        │  │  agent/core.py       │  │ (Existing Phase 1 code)  │
│        │  │  agent/tasks.py      │  │                           │
│        │  │  agent/planner.py    │  │                           │
│        │  │  agent/research.py   │  │                           │
│        │  └──────────┬───────────┘  │                           │
│        └─────────────┼──────────────┘                           │
│                      │                                           │
└──────────────────────┼───────────────────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          │                         │
┌─────────┴──────┐        ┌─────────┴──────────┐
│  DATA LAYER    │        │   EXTERNAL APIs    │
│                │        │                    │
│ ┌────────────┐ │        │ ┌────────────────┐ │
│ │ PostgreSQL │ │        │ │ Anthropic API  │ │
│ │  Database  │ │        │ │  (Claude AI)   │ │
│ └────────────┘ │        │ └────────────────┘ │
│                │        │                    │
│ ┌────────────┐ │        │ ┌────────────────┐ │
│ │   Redis    │ │        │ │ Email Service  │ │
│ │   Cache    │ │        │ │  (SendGrid)    │ │
│ └────────────┘ │        │ └────────────────┘ │
│                │        │                    │
└────────────────┘        └────────────────────┘

         ┌────────────────────────────────┐
         │    BACKGROUND JOBS LAYER       │
         │                                │
         │  ┌──────────┐   ┌───────────┐ │
         │  │  Celery  │   │   Redis   │ │
         │  │  Worker  │──▶│   Broker  │ │
         │  └──────────┘   └───────────┘ │
         │                                │
         │  Jobs: AI calls, emails,      │
         │        analytics, backups      │
         └────────────────────────────────┘
```

---

## Technology Stack

### Backend

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| **Web Framework** | FastAPI | 0.104+ | - Fast, modern Python framework<br>- Built-in async support<br>- Auto-generated OpenAPI docs<br>- Type hints with Pydantic<br>- Best performance for Python web |
| **Database ORM** | SQLAlchemy | 2.0+ | - Already used in Phase 1<br>- Supports async queries<br>- Mature, well-documented<br>- Easy migration from SQLite |
| **Database** | PostgreSQL | 15+ | - Production-grade reliability<br>- JSONB support for flexible schemas<br>- Full-text search<br>- Horizontal scaling with read replicas |
| **Caching** | Redis | 7+ | - In-memory performance<br>- Session storage<br>- Celery message broker<br>- Rate limiting counters |
| **Task Queue** | Celery | 5.3+ | - Async background jobs<br>- AI API calls (avoid timeout)<br>- Email sending<br>- Scheduled tasks (briefings) |
| **WebSocket** | Socket.io | 4.6+ | - Real-time bidirectional communication<br>- Automatic reconnection<br>- Room/namespace support<br>- Battle-tested |
| **Migrations** | Alembic | 1.12+ | - Database version control<br>- Auto-generate migrations<br>- Rollback support |
| **Validation** | Pydantic | 2.4+ | - Type safety<br>- Data validation<br>- Serialization/deserialization<br>- Built into FastAPI |
| **Authentication** | python-jose | 3.3+ | - JWT token generation/validation<br>- Industry standard<br>- Secure, stateless |
| **Password Hashing** | bcrypt | 4.0+ | - Secure password hashing<br>- Configurable cost factor<br>- Resistant to brute force |

### Frontend

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| **Framework** | React | 18.2+ | - Most popular UI library<br>- Large ecosystem<br>- Virtual DOM performance<br>- Concurrent rendering |
| **Language** | TypeScript | 5.2+ | - Type safety<br>- Better IDE support<br>- Fewer runtime errors<br>- Self-documenting |
| **Build Tool** | Vite | 4.5+ | - Fast HMR (Hot Module Replacement)<br>- ESBuild for production<br>- Modern, optimized builds<br>- Great DX |
| **Styling** | TailwindCSS | 3.3+ | - Utility-first CSS<br>- Rapid prototyping<br>- Small bundle size<br>- Consistent design system |
| **State Management** | Zustand | 4.4+ | - Simple, minimal boilerplate<br>- TypeScript-first<br>- Dev tools support<br>- No providers needed |
| **Data Fetching** | TanStack Query | 5.0+ | - Caching and synchronization<br>- Optimistic updates<br>- Automatic refetching<br>- DevTools |
| **HTTP Client** | Axios | 1.5+ | - Interceptors (auth tokens)<br>- Request/response transformation<br>- Better error handling than fetch<br>- Timeout support |
| **Forms** | React Hook Form | 7.47+ | - Performance (uncontrolled)<br>- Validation with Zod<br>- Less re-renders<br>- TypeScript support |
| **Validation** | Zod | 3.22+ | - TypeScript-first schema validation<br>- Composable<br>- Error messages<br>- Type inference |
| **Charts** | Recharts | 2.9+ | - Built for React<br>- Responsive<br>- Composable components<br>- SVG-based |
| **Icons** | Lucide React | 0.289+ | - Modern icon set<br>- Tree-shakeable<br>- Consistent design<br>- React components |
| **Date/Time** | date-fns | 2.30+ | - Modern, functional<br>- Immutable<br>- Tree-shakeable<br>- Locale support |
| **WebSocket** | Socket.io Client | 4.6+ | - Pairs with backend Socket.io<br>- Automatic reconnection<br>- TypeScript support |

### DevOps & Infrastructure

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Containerization** | Docker | - Consistent environments<br>- Easy deployment<br>- Isolation |
| **Orchestration** | Docker Compose | - Local development<br>- Service coordination<br>- Simple, no K8s needed |
| **Reverse Proxy** | Nginx | - SSL termination<br>- Static file serving<br>- Load balancing<br>- CORS handling |
| **Hosting** | Railway | - Simple deployment<br>- Managed PostgreSQL<br>- Managed Redis<br>- Auto-scaling<br>- Cost-effective |
| **CI/CD** | GitHub Actions | - Native to GitHub<br>- Free for open source<br>- Easy configuration<br>- Matrix testing |
| **Monitoring** | Sentry | - Error tracking<br>- Performance monitoring<br>- Release tracking<br>- Source maps |
| **Analytics** | PostHog | - Open source<br>- Self-hosted option<br>- Feature flags<br>- Session recording |

---

## Backend Architecture

### Directory Structure

```
business-agent/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app initialization
│   │   ├── dependencies.py         # Dependency injection (DB, auth)
│   │   │
│   │   ├── routes/                 # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── auth.py            # POST /auth/login, /auth/register
│   │   │   ├── tasks.py           # CRUD /tasks/*
│   │   │   ├── goals.py           # CRUD /goals/*
│   │   │   ├── briefings.py       # POST /briefings/morning
│   │   │   ├── analytics.py       # GET /analytics/*
│   │   │   └── dashboard.py       # GET /dashboard/summary
│   │   │
│   │   ├── schemas/                # Pydantic models (request/response)
│   │   │   ├── __init__.py
│   │   │   ├── auth.py            # LoginRequest, RegisterRequest, Token
│   │   │   ├── task.py            # TaskCreate, TaskUpdate, TaskResponse
│   │   │   ├── goal.py            # GoalCreate, GoalUpdate, GoalResponse
│   │   │   ├── briefing.py        # BriefingResponse
│   │   │   └── analytics.py       # StatsResponse, VelocityResponse
│   │   │
│   │   ├── services/               # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py    # User registration, login, JWT
│   │   │   ├── task_service.py    # Task CRUD, completion logic
│   │   │   ├── goal_service.py    # Goal CRUD, progress calculation
│   │   │   ├── ai_service.py      # Claude API integration
│   │   │   └── analytics_service.py # Stats, velocity, predictions
│   │   │
│   │   ├── middleware/             # Custom middleware
│   │   │   ├── __init__.py
│   │   │   ├── auth.py            # JWT verification
│   │   │   ├── rate_limit.py      # Rate limiting
│   │   │   └── error_handler.py   # Global error handling
│   │   │
│   │   └── websocket/              # WebSocket handlers
│   │       ├── __init__.py
│   │       ├── manager.py         # Connection manager
│   │       └── events.py          # Event handlers
│   │
│   ├── agent/                      # Existing Phase 1 code (minimal changes)
│   │   ├── __init__.py
│   │   ├── models.py              # SQLAlchemy models (add user_id)
│   │   ├── core.py                # Briefing/review generation
│   │   ├── tasks.py               # Task management logic
│   │   ├── planner.py             # Goal breakdown logic
│   │   └── research.py            # Research agent
│   │
│   ├── migrations/                 # Alembic migrations
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │       └── 001_initial_schema.py
│   │
│   ├── tests/                      # Backend tests
│   │   ├── __init__.py
│   │   ├── conftest.py            # Pytest fixtures
│   │   ├── test_auth.py
│   │   ├── test_tasks.py
│   │   ├── test_goals.py
│   │   └── test_analytics.py
│   │
│   ├── scripts/                    # Utility scripts
│   │   ├── init_db.py             # Database initialization
│   │   ├── migrate_data.py        # SQLite → PostgreSQL
│   │   └── create_admin.py        # Create admin user
│   │
│   ├── alembic.ini                # Alembic configuration
│   ├── config.py                  # App configuration
│   ├── database.py                # Database connection
│   └── requirements.txt           # Python dependencies
│
└── docker-compose.yml             # Local development services
```

### API Layer Design

**FastAPI Application (`api/main.py`)**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import auth, tasks, goals, briefings, analytics, dashboard
from api.middleware import rate_limit, error_handler
from api.websocket import manager

app = FastAPI(
    title="Bizy AI API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Middleware
app.add_middleware(CORSMiddleware, allow_origins=["https://app.bizy.ai"])
app.add_middleware(rate_limit.RateLimitMiddleware)
app.middleware("http")(error_handler.global_error_handler)

# Routes
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(goals.router, prefix="/api/goals", tags=["goals"])
app.include_router(briefings.router, prefix="/api/briefings", tags=["briefings"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])

# WebSocket
@app.websocket("/ws/updates")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    # ... handle events
```

### Service Layer Pattern

**Example: Task Service (`api/services/task_service.py`)**

```python
from sqlalchemy.orm import Session
from agent.models import Task, Goal
from api.schemas.task import TaskCreate, TaskUpdate
from datetime import datetime

class TaskService:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def get_tasks(self, status: str = None, priority: int = None):
        """Get filtered list of tasks for user"""
        query = self.db.query(Task).filter(Task.user_id == self.user_id)
        if status:
            query = query.filter(Task.status == status)
        if priority:
            query = query.filter(Task.priority == priority)
        return query.all()

    def create_task(self, task_data: TaskCreate):
        """Create a new task"""
        task = Task(**task_data.dict(), user_id=self.user_id)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def complete_task(self, task_id: int):
        """Mark task as complete and update goal progress"""
        task = self.get_task(task_id)
        task.status = "completed"
        task.completed_at = datetime.utcnow()

        # Update goal progress if linked
        if task.goal_id:
            self._update_goal_progress(task.goal_id)

        self.db.commit()
        return task

    def _update_goal_progress(self, goal_id: int):
        """Recalculate goal progress based on completed tasks"""
        goal = self.db.query(Goal).filter(Goal.id == goal_id).first()
        total_tasks = len(goal.tasks)
        completed_tasks = len([t for t in goal.tasks if t.status == "completed"])
        goal.progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
```

### Dependency Injection

**Database and Auth Dependencies (`api/dependencies.py`)**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from api.services.auth_service import verify_token

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Verify JWT token and return current user"""
    token = credentials.credentials
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
```

**Usage in Routes:**

```python
@router.get("/tasks")
async def get_tasks(
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get tasks for authenticated user"""
    service = TaskService(db, current_user.id)
    tasks = service.get_tasks(status=status)
    return tasks
```

---

## Frontend Architecture

### Directory Structure

```
frontend/
├── src/
│   ├── api/
│   │   ├── client.ts              # Axios instance with interceptors
│   │   ├── auth.ts                # Auth API calls
│   │   ├── tasks.ts               # Task API calls
│   │   ├── goals.ts               # Goal API calls
│   │   ├── briefings.ts           # Briefing API calls
│   │   └── analytics.ts           # Analytics API calls
│   │
│   ├── components/
│   │   ├── common/                # Reusable components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Table.tsx
│   │   │   └── Loader.tsx
│   │   │
│   │   ├── layout/                # Layout components
│   │   │   ├── Navbar.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── MainLayout.tsx
│   │   │   └── AuthLayout.tsx
│   │   │
│   │   ├── tasks/                 # Task-related components
│   │   │   ├── TaskList.tsx
│   │   │   ├── TaskItem.tsx
│   │   │   ├── TaskFilters.tsx
│   │   │   ├── TaskFormModal.tsx
│   │   │   └── TaskDetail.tsx
│   │   │
│   │   ├── goals/                 # Goal-related components
│   │   │   ├── GoalList.tsx
│   │   │   ├── GoalCard.tsx
│   │   │   ├── GoalDetail.tsx
│   │   │   ├── GoalFormModal.tsx
│   │   │   └── GoalProgress.tsx
│   │   │
│   │   ├── analytics/             # Analytics components
│   │   │   ├── StatsCards.tsx
│   │   │   ├── VelocityChart.tsx
│   │   │   └── GoalProgressChart.tsx
│   │   │
│   │   └── dashboard/             # Dashboard components
│   │       ├── DashboardStats.tsx
│   │       ├── TodayTasks.tsx
│   │       ├── ActiveGoals.tsx
│   │       └── MorningBrief.tsx
│   │
│   ├── pages/
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── Dashboard.tsx
│   │   ├── Tasks.tsx
│   │   ├── Goals.tsx
│   │   ├── Analytics.tsx
│   │   └── Settings.tsx
│   │
│   ├── hooks/
│   │   ├── useAuth.ts             # Auth state and operations
│   │   ├── useTasks.ts            # Task queries and mutations
│   │   ├── useGoals.ts            # Goal queries and mutations
│   │   ├── useAnalytics.ts        # Analytics queries
│   │   ├── useWebSocket.ts        # WebSocket connection
│   │   └── useToast.ts            # Toast notifications
│   │
│   ├── store/
│   │   ├── authStore.ts           # Zustand auth store
│   │   └── uiStore.ts             # UI state (sidebar, modals)
│   │
│   ├── types/
│   │   ├── auth.ts                # Auth types
│   │   ├── task.ts                # Task types
│   │   ├── goal.ts                # Goal types
│   │   └── analytics.ts           # Analytics types
│   │
│   ├── utils/
│   │   ├── date.ts                # Date formatting utilities
│   │   ├── validation.ts          # Zod schemas
│   │   └── constants.ts           # App constants
│   │
│   ├── App.tsx                    # Root component
│   ├── main.tsx                   # Entry point
│   └── index.css                  # Global styles (Tailwind)
│
├── public/
│   ├── favicon.ico
│   └── manifest.json              # PWA manifest
│
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── .env.example
```

### State Management Strategy

**TanStack Query for Server State:**

```typescript
// hooks/useTasks.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as taskApi from '../api/tasks';

export function useTasks(filters?: TaskFilters) {
  return useQuery({
    queryKey: ['tasks', filters],
    queryFn: () => taskApi.getTasks(filters),
  });
}

export function useCompleteTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskId: number) => taskApi.completeTask(taskId),
    onSuccess: () => {
      // Invalidate tasks and goals queries
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['goals'] });
    },
    // Optimistic update
    onMutate: async (taskId) => {
      await queryClient.cancelQueries({ queryKey: ['tasks'] });
      const previousTasks = queryClient.getQueryData(['tasks']);

      queryClient.setQueryData(['tasks'], (old: Task[]) =>
        old.map(task =>
          task.id === taskId ? { ...task, status: 'completed' } : task
        )
      );

      return { previousTasks };
    },
    onError: (err, taskId, context) => {
      // Rollback on error
      queryClient.setQueryData(['tasks'], context.previousTasks);
    },
  });
}
```

**Zustand for Client State:**

```typescript
// store/authStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,

      login: async (email, password) => {
        const { user, token } = await authApi.login(email, password);
        set({ user, isAuthenticated: true });
        localStorage.setItem('token', token);
      },

      logout: () => {
        set({ user: null, isAuthenticated: false });
        localStorage.removeItem('token');
      },

      refreshToken: async () => {
        const { token } = await authApi.refreshToken();
        localStorage.setItem('token', token);
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user }),
    }
  )
);
```

### Component Patterns

**Smart/Container Components:**

```typescript
// pages/Tasks.tsx (Smart Component)
import { useTasks, useCompleteTask } from '../hooks/useTasks';
import TaskList from '../components/tasks/TaskList';

export default function TasksPage() {
  const { data: tasks, isLoading } = useTasks();
  const completeTask = useCompleteTask();

  const handleComplete = (taskId: number) => {
    completeTask.mutate(taskId);
  };

  if (isLoading) return <Loader />;

  return <TaskList tasks={tasks} onComplete={handleComplete} />;
}
```

**Presentational/Dumb Components:**

```typescript
// components/tasks/TaskList.tsx (Presentational Component)
interface TaskListProps {
  tasks: Task[];
  onComplete: (id: number) => void;
}

export default function TaskList({ tasks, onComplete }: TaskListProps) {
  return (
    <div className="space-y-2">
      {tasks.map(task => (
        <TaskItem
          key={task.id}
          task={task}
          onComplete={() => onComplete(task.id)}
        />
      ))}
    </div>
  );
}
```

---

## Database Design

### Schema Changes from Phase 1/2

```sql
-- New users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    email_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Add user_id to existing tables
ALTER TABLE tasks ADD COLUMN user_id INTEGER REFERENCES users(id);
ALTER TABLE goals ADD COLUMN user_id INTEGER REFERENCES users(id);

-- Add timestamps (if not exist)
ALTER TABLE tasks ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE tasks ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE goals ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE goals ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Add indexes for performance
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_goals_user_id ON goals(user_id);
CREATE INDEX idx_goals_horizon ON goals(horizon);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_goals_updated_at BEFORE UPDATE ON goals
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### Database Models

**Updated SQLAlchemy Models (`agent/models.py`)**

```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    email_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # Relationships
    tasks = relationship("Task", back_populates="user")
    goals = relationship("Goal", back_populates="user")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    priority = Column(Integer, default=2)
    category = Column(String)
    estimated_hours = Column(Integer)
    due_date = Column(DateTime)
    status = Column(String, default="pending")
    goal_id = Column(Integer, ForeignKey("goals.id"))
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="tasks")
    goal = relationship("Goal", back_populates="tasks")

class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    horizon = Column(String)  # yearly, quarterly, monthly, weekly
    target_date = Column(DateTime)
    progress = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="goals")
    tasks = relationship("Task", back_populates="goal")
```

---

## API Design

### RESTful Conventions

- **Resource-based URLs:** `/api/tasks`, `/api/goals` (plural nouns)
- **HTTP Methods:** GET (read), POST (create), PATCH (update), DELETE (delete)
- **Status Codes:** 200 (OK), 201 (Created), 204 (No Content), 400 (Bad Request), 401 (Unauthorized), 404 (Not Found), 500 (Server Error)
- **Versioning:** `/api/v1/*` (future-proof)
- **Pagination:** `?page=1&limit=50`
- **Filtering:** `?status=pending&priority=1`
- **Sorting:** `?sort=due_date&order=asc`

### Authentication Flow

```
1. User registers → POST /api/auth/register
   Request: { email, password, name }
   Response: { user: {...}, access_token: "...", refresh_token: "..." }

2. User logs in → POST /api/auth/login
   Request: { email, password }
   Response: { user: {...}, access_token: "...", refresh_token: "..." }

3. Frontend stores tokens
   - access_token in memory (or HttpOnly cookie)
   - refresh_token in HttpOnly cookie

4. All API requests include access_token
   Header: Authorization: Bearer <access_token>

5. If access_token expires (15 min) → POST /api/auth/refresh
   Request: { refresh_token }
   Response: { access_token: "..." }

6. User logs out → POST /api/auth/logout
   - Invalidate tokens (add to Redis blacklist)
```

### Request/Response Examples

**Create Task:**

```http
POST /api/tasks
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json

{
  "title": "Design landing page",
  "priority": 1,
  "category": "design",
  "estimated_hours": 4,
  "due_date": "2026-01-15T10:00:00Z",
  "goal_id": 5
}

Response (201 Created):
{
  "id": 42,
  "user_id": 7,
  "title": "Design landing page",
  "priority": 1,
  "category": "design",
  "estimated_hours": 4,
  "due_date": "2026-01-15T10:00:00Z",
  "status": "pending",
  "goal_id": 5,
  "completed_at": null,
  "created_at": "2025-10-23T14:30:00Z",
  "updated_at": "2025-10-23T14:30:00Z"
}
```

**Get Tasks with Filters:**

```http
GET /api/tasks?status=pending&priority=1&sort=due_date&order=asc
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

Response (200 OK):
{
  "data": [
    { "id": 42, "title": "Design landing page", ... },
    { "id": 43, "title": "Fix auth bug", ... }
  ],
  "total": 2,
  "page": 1,
  "limit": 50
}
```

**AI Goal Breakdown:**

```http
POST /api/goals/5/breakdown
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

Response (200 OK):
{
  "goal_id": 5,
  "goal_title": "Launch MVP Product",
  "tasks_created": 8,
  "tasks": [
    {
      "id": 44,
      "title": "Design database schema",
      "priority": 1,
      "estimated_hours": 3,
      "category": "backend"
    },
    ...
  ]
}
```

---

## Real-Time Communication

### WebSocket Architecture

**Connection Flow:**

```
1. User logs in → Establish WebSocket connection
   WS /ws/updates?token=<access_token>

2. Server validates token → Add to connection pool
   connections[user_id] = websocket

3. When task completed → Broadcast to user's connections
   await manager.send_personal_message(user_id, {
     event: "task_completed",
     data: { task_id: 42, goal_id: 5, new_goal_progress: 65 }
   })

4. Frontend receives event → Update UI (via TanStack Query)
   socket.on('task_completed', (data) => {
     queryClient.invalidateQueries(['tasks']);
     queryClient.invalidateQueries(['goals']);
   })

5. On logout/disconnect → Remove from pool
   del connections[user_id]
```

**Event Types:**

```typescript
// events.ts
export enum WebSocketEvent {
  // Task events
  TASK_CREATED = 'task_created',
  TASK_UPDATED = 'task_updated',
  TASK_COMPLETED = 'task_completed',
  TASK_DELETED = 'task_deleted',

  // Goal events
  GOAL_CREATED = 'goal_created',
  GOAL_UPDATED = 'goal_updated',
  GOAL_PROGRESS_UPDATED = 'goal_progress_updated',
  GOAL_DELETED = 'goal_deleted',

  // System events
  BRIEFING_READY = 'briefing_ready',
  SYNC_REQUIRED = 'sync_required',
}
```

**Frontend WebSocket Hook:**

```typescript
// hooks/useWebSocket.ts
import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import io from 'socket.io-client';

export function useWebSocket() {
  const queryClient = useQueryClient();

  useEffect(() => {
    const token = localStorage.getItem('token');
    const socket = io('ws://localhost:8000', {
      auth: { token }
    });

    socket.on('task_completed', () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['goals'] });
    });

    socket.on('goal_progress_updated', () => {
      queryClient.invalidateQueries({ queryKey: ['goals'] });
    });

    return () => socket.disconnect();
  }, [queryClient]);
}
```

---

## Security Architecture

### Authentication & Authorization

1. **Password Security:**
   - bcrypt hashing (cost factor 12)
   - Minimum 8 characters, 1 uppercase, 1 number
   - Password reset via email with expiring token

2. **JWT Tokens:**
   - Access token: 15 min expiry (short-lived)
   - Refresh token: 7 day expiry (HttpOnly cookie)
   - Stored in Redis blacklist on logout

3. **HTTPS Only:**
   - Redirect HTTP to HTTPS
   - HSTS headers (max-age=31536000)

4. **CORS:**
   - Whitelist frontend domain only
   - Credentials allowed (for cookies)

5. **Rate Limiting:**
   - 100 requests/minute per user (authenticated)
   - 10 requests/minute per IP (unauthenticated)
   - Redis-based counter

### Input Validation

- **Pydantic schemas** validate all request bodies
- **SQL injection** prevented by SQLAlchemy ORM (parameterized queries)
- **XSS protection** via React auto-escaping + CSP headers
- **CSRF protection** via same-site cookies

### Security Headers

```python
# api/main.py
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["app.bizy.ai"])

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

---

## Deployment Architecture

### Development Environment

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: bizy_dev
      POSTGRES_USER: bizy
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    command: uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://bizy:dev_password@postgres:5432/bizy_dev
      REDIS_URL: redis://redis:6379
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
    depends_on:
      - postgres
      - redis

  frontend:
    build: ./frontend
    command: npm run dev
    volumes:
      - ./frontend:/app
    ports:
      - "3000:3000"
    environment:
      VITE_API_URL: http://localhost:8000

  celery_worker:
    build: ./backend
    command: celery -A api.celery_app worker --loglevel=info
    volumes:
      - ./backend:/app
    environment:
      DATABASE_URL: postgresql://bizy:dev_password@postgres:5432/bizy_dev
      REDIS_URL: redis://redis:6379
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
```

### Production (Railway)

**Backend Service:**
- **Runtime:** Python 3.10
- **Start Command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables:**
  - `DATABASE_URL` (auto from Railway PostgreSQL)
  - `REDIS_URL` (auto from Railway Redis)
  - `ANTHROPIC_API_KEY`
  - `JWT_SECRET`
  - `FRONTEND_URL`

**Frontend Service:**
- **Runtime:** Node.js 18
- **Build Command:** `npm run build`
- **Start Command:** `npm run preview`
- **Environment Variables:**
  - `VITE_API_URL` (backend URL)

**PostgreSQL:** Managed by Railway (auto-backups, monitoring)

**Redis:** Managed by Railway (persistence enabled)

**Nginx (optional):** Reverse proxy for SSL termination, caching

---

## Development Workflow

### Local Development

```bash
# 1. Clone repository
git clone https://github.com/yourusername/business-agent.git
cd business-agent

# 2. Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# 3. Start services
docker-compose up -d

# 4. Run database migrations
docker-compose exec backend alembic upgrade head

# 5. Create admin user
docker-compose exec backend python scripts/create_admin.py

# 6. Access application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
```

### Testing

```bash
# Backend tests
docker-compose exec backend pytest tests/ -v --cov=api

# Frontend tests
docker-compose exec frontend npm test

# E2E tests
npm run test:e2e

# Load testing
locust -f tests/load_test.py --host=http://localhost:8000
```

### CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: CI/CD

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/tests/ -v

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: cd frontend && npm install
      - run: cd frontend && npm test
      - run: cd frontend && npm run build

  deploy:
    needs: [backend-tests, frontend-tests]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        run: railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

---

## Migration Strategy

### Phase 2 → Phase 3 Migration

**Week 1: Data Migration**

1. **Export SQLite data:**
   ```bash
   python scripts/export_sqlite.py > data_export.json
   ```

2. **Set up PostgreSQL:**
   ```bash
   docker-compose up postgres -d
   alembic upgrade head
   ```

3. **Import data:**
   ```bash
   python scripts/import_to_postgres.py data_export.json
   ```

4. **Create default admin user:**
   ```bash
   python scripts/create_admin.py
   # Assign all existing tasks/goals to admin user
   ```

5. **Verify data integrity:**
   ```bash
   python scripts/verify_migration.py
   ```

**Week 2-4: Backend Development**
- Develop API endpoints
- Test with Postman/Insomnia
- Write automated tests
- Deploy to staging

**Week 5-7: Frontend Development**
- Build React components
- Integrate with API
- Test across devices
- Deploy to staging

**Week 8: Beta Testing**
- Onboard 10-20 beta users
- Collect feedback
- Fix critical bugs
- Optimize performance

**Week 9-10: Production Launch**
- Security audit
- Load testing
- Documentation
- Launch 🚀

### Rollback Plan

If migration fails:

1. **Keep Phase 2 CLI working** (don't remove)
2. **Database backup before migration**
3. **Ability to restore from backup**
4. **Feature flag to disable web app**

---

## Appendix: Technology Comparison

### Why FastAPI over Flask/Django?

| Criteria | FastAPI | Flask | Django |
|----------|---------|-------|--------|
| **Performance** | 🟢 Best (async) | 🟡 Good | 🟡 Good |
| **Type Safety** | 🟢 Built-in (Pydantic) | 🔴 Manual | 🔴 Manual |
| **Auto Docs** | 🟢 Yes (Swagger) | 🔴 No | 🟡 DRF only |
| **Learning Curve** | 🟡 Medium | 🟢 Low | 🔴 High |
| **Async Support** | 🟢 Native | 🟡 Add-on | 🟡 Add-on |
| **Boilerplate** | 🟢 Minimal | 🟢 Minimal | 🔴 Heavy |

**Verdict:** FastAPI wins for modern Python web development.

### Why React over Vue/Svelte?

| Criteria | React | Vue | Svelte |
|----------|-------|-----|--------|
| **Ecosystem** | 🟢 Largest | 🟡 Good | 🔴 Small |
| **Jobs/Hiring** | 🟢 Most | 🟡 Medium | 🔴 Few |
| **TypeScript** | 🟢 Excellent | 🟡 Good | 🟡 Good |
| **Learning Curve** | 🟡 Medium | 🟢 Low | 🟢 Low |
| **Performance** | 🟡 Good | 🟡 Good | 🟢 Best |
| **Community** | 🟢 Huge | 🟡 Large | 🟡 Growing |

**Verdict:** React for ecosystem, hiring, and long-term support.

### Why PostgreSQL over MySQL/MongoDB?

| Criteria | PostgreSQL | MySQL | MongoDB |
|----------|-----------|-------|---------|
| **ACID Compliance** | 🟢 Full | 🟡 Good | 🔴 Limited |
| **JSON Support** | 🟢 JSONB | 🔴 Basic | 🟢 Native |
| **Full-Text Search** | 🟢 Built-in | 🔴 Limited | 🟢 Built-in |
| **Reliability** | 🟢 Excellent | 🟡 Good | 🟡 Good |
| **Scaling** | 🟡 Vertical | 🟡 Vertical | 🟢 Horizontal |
| **Community** | 🟢 Strong | 🟢 Strong | 🟡 Good |

**Verdict:** PostgreSQL for reliability, features, and future growth.

---

**Document Status:** Draft v1.0
**Next Review:** After technical review
**Owner:** Engineering Team
**Last Updated:** October 23, 2025
