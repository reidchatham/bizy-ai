import api from './api';
import type { Goal } from '../types';

export interface GoalFilters {
  status?: 'active' | 'completed' | 'on_hold' | 'cancelled';
  horizon?: 'yearly' | 'quarterly' | 'monthly' | 'weekly';
  parent_goal_id?: number;
  search?: string;
}

export interface CreateGoalData {
  title: string;
  description?: string;
  horizon: 'yearly' | 'quarterly' | 'monthly' | 'weekly';
  status?: 'active' | 'completed' | 'on_hold' | 'cancelled';
  target_date?: string;
  success_criteria?: string;
  metrics?: Record<string, any>;
  parent_goal_id?: number;
}

export interface UpdateGoalData {
  title?: string;
  description?: string;
  horizon?: 'yearly' | 'quarterly' | 'monthly' | 'weekly';
  status?: 'active' | 'completed' | 'on_hold' | 'cancelled';
  target_date?: string;
  success_criteria?: string;
  metrics?: Record<string, any>;
  parent_goal_id?: number;
  progress?: number;
}

export interface BreakdownSuggestion {
  title: string;
  description: string;
  priority: 1 | 2 | 3;
  category: string;
  estimated_hours?: number;
  reasoning: string;
}

export interface GoalBreakdownResponse {
  goal_id: number;
  suggestions: BreakdownSuggestion[];
  reasoning: string;
  estimated_timeline: string;
}

export interface CreateTasksFromBreakdownData {
  task_indices: number[];
}

export interface GoalStats {
  total: number;
  completed: number;
  in_progress: number;
  not_started: number;
  on_hold: number;
  average_progress: number;
  at_risk_goals: number;
}

export const goalService = {
  /**
   * Get list of goals with optional filters
   */
  list: async (filters?: GoalFilters): Promise<Goal[]> => {
    const response = await api.get('/goals/', { params: filters });
    return response.data;
  },

  /**
   * Get a single goal by ID
   */
  get: async (id: number): Promise<Goal> => {
    const response = await api.get(`/goals/${id}`);
    return response.data;
  },

  /**
   * Create a new goal
   */
  create: async (data: CreateGoalData): Promise<Goal> => {
    const response = await api.post('/goals/', data);
    return response.data;
  },

  /**
   * Update an existing goal
   */
  update: async (id: number, data: UpdateGoalData): Promise<Goal> => {
    const response = await api.patch(`/goals/${id}`, data);
    return response.data;
  },

  /**
   * Delete a goal
   */
  delete: async (id: number): Promise<void> => {
    await api.delete(`/goals/${id}`);
  },

  /**
   * Calculate goal progress based on tasks
   */
  calculateProgress: async (id: number): Promise<Goal> => {
    const response = await api.post(`/goals/${id}/calculate-progress`);
    return response.data;
  },

  /**
   * Get AI-powered breakdown of goal into tasks
   */
  breakdown: async (id: number): Promise<GoalBreakdownResponse> => {
    const response = await api.post(`/goals/${id}/breakdown`);
    return response.data;
  },

  /**
   * Create tasks from AI breakdown suggestions
   */
  createTasksFromBreakdown: async (
    id: number,
    data: CreateTasksFromBreakdownData
  ): Promise<{ tasks: any[]; message: string }> => {
    const response = await api.post(`/goals/${id}/breakdown/create-tasks`, data);
    return response.data;
  },

  /**
   * Get goal statistics
   */
  stats: async (): Promise<GoalStats> => {
    const response = await api.get('/goals/stats/summary');
    return response.data;
  },
};
