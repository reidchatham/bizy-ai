import { useQuery } from '@tanstack/react-query';
import { analyticsService, type AnalyticsFilters } from '../services/analytics';

/**
 * Hook to fetch task analytics
 */
export const useTaskAnalytics = (filters?: AnalyticsFilters) => {
  return useQuery({
    queryKey: ['analytics', 'tasks', filters],
    queryFn: () => analyticsService.tasks(filters),
  });
};

/**
 * Hook to fetch goal analytics
 */
export const useGoalAnalytics = (filters?: AnalyticsFilters) => {
  return useQuery({
    queryKey: ['analytics', 'goals', filters],
    queryFn: () => analyticsService.goals(filters),
  });
};

/**
 * Hook to fetch velocity metrics
 */
export const useVelocityMetrics = (filters?: AnalyticsFilters) => {
  return useQuery({
    queryKey: ['analytics', 'velocity', filters],
    queryFn: () => analyticsService.velocity(filters),
  });
};

/**
 * Hook to fetch trend analysis
 */
export const useTrendAnalysis = (filters?: AnalyticsFilters) => {
  return useQuery({
    queryKey: ['analytics', 'trends', filters],
    queryFn: () => analyticsService.trends(filters),
  });
};

/**
 * Hook to fetch all analytics data at once
 */
export const useAllAnalytics = (filters?: AnalyticsFilters) => {
  const taskAnalytics = useTaskAnalytics(filters);
  const goalAnalytics = useGoalAnalytics(filters);
  const velocity = useVelocityMetrics(filters);
  const trends = useTrendAnalysis(filters);

  return {
    taskAnalytics,
    goalAnalytics,
    velocity,
    trends,
    isLoading: taskAnalytics.isLoading || goalAnalytics.isLoading || velocity.isLoading || trends.isLoading,
    isError: taskAnalytics.isError || goalAnalytics.isError || velocity.isError || trends.isError,
  };
};
