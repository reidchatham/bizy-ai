// Task types
export interface Task {
  id: number;
  user_id: number;
  title: string;
  description?: string;
  priority: number;
  status: 'pending' | 'in_progress' | 'completed' | 'blocked';
  category?: string;
  estimated_hours?: number;
  actual_hours?: number;
  due_date?: string;
  parent_goal_id?: number;
  dependencies?: number[];
  notes?: string;
  tags?: string[];
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

// Goal types
export interface Goal {
  id: number;
  user_id: number;
  parent_goal_id?: number;
  title: string;
  description?: string;
  horizon: 'yearly' | 'quarterly' | 'monthly' | 'weekly';
  target_date?: string;
  status: 'active' | 'completed' | 'on_hold' | 'cancelled';
  progress_percentage: number;
  success_criteria?: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  metrics?: Record<string, any>;
  task_count?: number;
  subgoal_count?: number;
}

// Auth types
export interface User {
  id: number;
  username: string;
  email: string;
  is_admin: boolean;
}

export interface AuthResponse {
  token: string;
  user_id: number;
}

// Analytics types
export interface TaskAnalytics {
  period_days: number;
  tasks_completed: number;
  tasks_created: number;
  tasks_pending: number;
  tasks_in_progress: number;
  tasks_blocked: number;
  completion_rate: number;
  total_estimated_hours: number;
  total_actual_hours: number;
  by_category: Record<string, number>;
  by_priority: Record<string, number>;
  by_status: Record<string, number>;
  overdue_count: number;
}

export interface GoalAnalytics {
  total_goals: number;
  active_goals: number;
  completed_goals: number;
  on_hold_goals: number;
  cancelled_goals: number;
  average_progress: number;
  by_horizon: Record<string, number>;
  goals_near_completion: number;
  goals_at_risk: number;
}

export interface VelocityMetrics {
  period_days: number;
  velocity: number;
  tasks_per_day: number;
  completion_trend: 'improving' | 'declining' | 'stable';
  productivity_score: number;
  best_day?: {
    date: string;
    tasks_completed: number;
  };
  worst_day?: {
    date: string;
    tasks_completed: number;
  };
  daily_breakdown: Array<{
    date: string;
    tasks_completed: number;
  }>;
}

// Briefing types
export interface MorningBriefing {
  date: string;
  greeting: string;
  yesterday_recap: {
    tasks_completed: number;
    tasks_due: number;
    completion_rate: number;
  };
  todays_mission: Array<{
    priority: number;
    task: string;
    why_it_matters: string;
    estimated_time: string;
  }>;
  watch_out_for: string[];
  pro_tip: string;
  tasks_today: Task[];
  active_goals: Goal[];
  overdue_tasks: Task[];
}
