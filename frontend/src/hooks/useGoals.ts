import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { goalService, type GoalFilters, type CreateGoalData, type UpdateGoalData, type CreateTasksFromBreakdownData } from '../services/goals';
import { toast } from 'sonner';

/**
 * Hook to fetch list of goals
 */
export const useGoals = (filters?: GoalFilters) => {
  return useQuery({
    queryKey: ['goals', filters],
    queryFn: () => goalService.list(filters),
  });
};

/**
 * Hook to fetch a single goal
 */
export const useGoal = (id: number) => {
  return useQuery({
    queryKey: ['goals', id],
    queryFn: () => goalService.get(id),
    enabled: !!id,
  });
};

/**
 * Hook to fetch goal statistics
 */
export const useGoalStats = () => {
  return useQuery({
    queryKey: ['goals', 'stats'],
    queryFn: () => goalService.stats(),
  });
};

/**
 * Hook to create a new goal
 */
export const useCreateGoal = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateGoalData) => goalService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['goals'] });
      toast.success('Goal created successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create goal');
    },
  });
};

/**
 * Hook to update an existing goal
 */
export const useUpdateGoal = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateGoalData }) =>
      goalService.update(id, data),
    onSuccess: (updatedGoal) => {
      queryClient.invalidateQueries({ queryKey: ['goals'] });
      queryClient.invalidateQueries({ queryKey: ['goals', updatedGoal.id] });
      toast.success('Goal updated successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update goal');
    },
  });
};

/**
 * Hook to delete a goal
 */
export const useDeleteGoal = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => goalService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['goals'] });
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      toast.success('Goal deleted successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete goal');
    },
  });
};

/**
 * Hook to calculate goal progress
 */
export const useCalculateGoalProgress = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => goalService.calculateProgress(id),
    onSuccess: (updatedGoal) => {
      queryClient.invalidateQueries({ queryKey: ['goals'] });
      queryClient.invalidateQueries({ queryKey: ['goals', updatedGoal.id] });
      toast.success('Goal progress updated');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to calculate progress');
    },
  });
};

/**
 * Hook to get AI breakdown of a goal
 */
export const useGoalBreakdown = (id: number, enabled = false) => {
  return useQuery({
    queryKey: ['goals', id, 'breakdown'],
    queryFn: () => goalService.breakdown(id),
    enabled: enabled && !!id,
    staleTime: 0, // Always fetch fresh AI breakdown
  });
};

/**
 * Hook to trigger AI breakdown (for manual triggering)
 */
export const useTriggerGoalBreakdown = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => goalService.breakdown(id),
    onSuccess: (data, id) => {
      queryClient.setQueryData(['goals', id, 'breakdown'], data);
      toast.success('AI breakdown generated successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to generate breakdown');
    },
  });
};

/**
 * Hook to create tasks from AI breakdown
 */
export const useCreateTasksFromBreakdown = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: CreateTasksFromBreakdownData }) =>
      goalService.createTasksFromBreakdown(id, data),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['goals'] });
      toast.success(response.message || `${response.tasks.length} tasks created successfully`);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create tasks');
    },
  });
};
