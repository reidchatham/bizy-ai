import api from './api';
import type { Task } from '../types';

export interface TaskFilters {
  status?: 'pending' | 'in_progress' | 'completed' | 'blocked';
  category?: string;
  priority?: 1 | 2 | 3;
  parent_goal_id?: number;
  search?: string;
  due_date_start?: string;
  due_date_end?: string;
}

export interface CreateTaskData {
  title: string;
  description?: string;
  status?: 'pending' | 'in_progress' | 'completed' | 'blocked';
  priority?: 1 | 2 | 3;
  category?: string;
  due_date?: string;
  estimated_hours?: number;
  parent_goal_id?: number;
  tags?: string[];
  dependencies?: number[];
  notes?: string;
}

export interface UpdateTaskData {
  title?: string;
  description?: string;
  status?: 'pending' | 'in_progress' | 'completed' | 'blocked';
  priority?: 1 | 2 | 3;
  category?: string;
  due_date?: string;
  estimated_hours?: number;
  actual_hours?: number;
  parent_goal_id?: number;
  tags?: string[];
  dependencies?: number[];
  notes?: string;
}

export interface CompleteTaskData {
  actual_hours?: number;
}

export interface TaskStats {
  total: number;
  completed: number;
  in_progress: number;
  pending: number;
  overdue: number;
  completion_rate: number;
}

export const taskService = {
  /**
   * Get list of tasks with optional filters
   */
  list: async (filters?: TaskFilters): Promise<Task[]> => {
    const response = await api.get('/tasks/', { params: filters });
    return response.data;
  },

  /**
   * Get a single task by ID
   */
  get: async (id: number): Promise<Task> => {
    const response = await api.get(`/tasks/${id}`);
    return response.data;
  },

  /**
   * Create a new task
   */
  create: async (data: CreateTaskData): Promise<Task> => {
    const response = await api.post('/tasks/', data);
    return response.data;
  },

  /**
   * Update an existing task
   */
  update: async (id: number, data: UpdateTaskData): Promise<Task> => {
    const response = await api.patch(`/tasks/${id}`, data);
    return response.data;
  },

  /**
   * Delete a task
   */
  delete: async (id: number): Promise<void> => {
    await api.delete(`/tasks/${id}`);
  },

  /**
   * Mark a task as complete
   */
  complete: async (id: number, data?: CompleteTaskData): Promise<Task> => {
    const response = await api.post(`/tasks/${id}/complete`, data || {});
    return response.data;
  },

  /**
   * Mark a task as incomplete (undo completion)
   */
  uncomplete: async (id: number): Promise<Task> => {
    const response = await api.post(`/tasks/${id}/uncomplete`);
    return response.data;
  },

  /**
   * Get task statistics
   */
  stats: async (): Promise<TaskStats> => {
    const response = await api.get('/tasks/stats/summary');
    return response.data;
  },
};
