import api from './api';

export interface TaskAnalyticsData {
  total_tasks: number;
  completed_tasks: number;
  pending_tasks: number;
  in_progress_tasks: number;
  completion_rate: number;
  average_completion_time_hours: number;
  by_category: Record<string, {
    total: number;
    completed: number;
    completion_rate: number;
  }>;
  by_priority: Record<string, {
    total: number;
    completed: number;
    completion_rate: number;
  }>;
  time_tracking: {
    total_estimated_hours: number;
    total_actual_hours: number;
    accuracy_rate: number;
  };
}

export interface GoalAnalyticsData {
  total_goals: number;
  completed_goals: number;
  in_progress_goals: number;
  not_started_goals: number;
  on_hold_goals: number;
  average_progress: number;
  by_horizon: Record<string, {
    total: number;
    completed: number;
    average_progress: number;
  }>;
  at_risk_goals: Array<{
    goal_id: number;
    title: string;
    progress: number;
    target_date: string | null;
    days_until_target: number | null;
    risk_level: string;
  }>;
  goals_near_completion: Array<{
    goal_id: number;
    title: string;
    progress: number;
    remaining_tasks: number;
  }>;
}

export interface VelocityMetrics {
  period_days: number;
  tasks_completed: number;
  tasks_per_day: number;
  productivity_score: number;
  trend: 'improving' | 'stable' | 'declining';
  daily_completion: Record<string, number>;
  best_day: {
    date: string;
    tasks_completed: number;
  } | null;
  worst_day: {
    date: string;
    tasks_completed: number;
  } | null;
}

export interface TrendAnalysis {
  period_days: number;
  weekly_completion: Record<string, {
    week_start: string;
    tasks_completed: number;
    completion_rate: number;
  }>;
  category_trends: Record<string, {
    trend: 'increasing' | 'stable' | 'decreasing';
    change_percentage: number;
  }>;
  insights: string[];
}

export interface AnalyticsFilters {
  start_date?: string;
  end_date?: string;
  days?: number;
}

export const analyticsService = {
  /**
   * Get task analytics
   */
  tasks: async (filters?: AnalyticsFilters): Promise<TaskAnalyticsData> => {
    const response = await api.get('/analytics/tasks', { params: filters });
    return response.data;
  },

  /**
   * Get goal analytics
   */
  goals: async (filters?: AnalyticsFilters): Promise<GoalAnalyticsData> => {
    const response = await api.get('/analytics/goals', { params: filters });
    return response.data;
  },

  /**
   * Get velocity metrics
   */
  velocity: async (filters?: AnalyticsFilters): Promise<VelocityMetrics> => {
    const response = await api.get('/analytics/velocity', { params: filters });
    return response.data;
  },

  /**
   * Get trend analysis
   */
  trends: async (filters?: AnalyticsFilters): Promise<TrendAnalysis> => {
    const response = await api.get('/analytics/trends', { params: filters });
    return response.data;
  },
};
