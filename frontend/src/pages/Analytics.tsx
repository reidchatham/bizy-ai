import { useState } from 'react';
import { TrendingUp, Target, CheckCircle, Activity, BarChart3, Calendar } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/Select';
import { MetricCard } from '../components/analytics/MetricCard';
import { CompletionChart } from '../components/analytics/CompletionChart';
import { VelocityChart } from '../components/analytics/VelocityChart';
import { InsightsPanel } from '../components/analytics/InsightsPanel';
import { Spinner } from '../components/ui/Spinner';
import { useAllAnalytics } from '../hooks/useAnalytics';

export default function Analytics() {
  const [timeRange, setTimeRange] = useState('30');

  // Fetch all analytics data
  const { taskAnalytics, goalAnalytics, velocity, trends, isLoading } = useAllAnalytics({
    days: parseInt(timeRange),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Spinner size="lg" />
      </div>
    );
  }

  // Transform data for charts
  const categoryData = taskAnalytics.data?.by_category
    ? Object.entries(taskAnalytics.data.by_category).map(([name, data]) => ({
        name: name.charAt(0).toUpperCase() + name.slice(1),
        total: data.total,
        completed: data.completed,
        completion_rate: data.completion_rate,
      }))
    : [];

  const priorityData = taskAnalytics.data?.by_priority
    ? Object.entries(taskAnalytics.data.by_priority).map(([name, data]) => ({
        name: `Priority ${name}`,
        total: data.total,
        completed: data.completed,
        completion_rate: data.completion_rate,
      }))
    : [];

  const horizonData = goalAnalytics.data?.by_horizon
    ? Object.entries(goalAnalytics.data.by_horizon).map(([name, data]) => ({
        name: name.charAt(0).toUpperCase() + name.slice(1),
        total: data.total,
        completed: data.completed,
        average_progress: data.average_progress,
      }))
    : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Analytics</h1>
          <p className="text-gray-600 mt-1">
            Insights and metrics for your productivity
          </p>
        </div>

        {/* Time Range Selector */}
        <Select value={timeRange} onValueChange={setTimeRange}>
          <SelectTrigger className="w-48">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="7">Last 7 days</SelectItem>
            <SelectItem value="30">Last 30 days</SelectItem>
            <SelectItem value="90">Last 90 days</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Completion Rate"
          value={`${taskAnalytics.data?.completion_rate?.toFixed(0) || 0}%`}
          subtitle={`${taskAnalytics.data?.completed_tasks || 0} of ${taskAnalytics.data?.total_tasks || 0} tasks`}
          icon={CheckCircle}
          variant="green"
        />

        <MetricCard
          title="Velocity"
          value={`${velocity.data?.tasks_per_day?.toFixed(1) || 0}`}
          subtitle="tasks per day"
          icon={TrendingUp}
          variant="blue"
        />

        <MetricCard
          title="Productivity Score"
          value={velocity.data?.productivity_score?.toFixed(0) || 0}
          subtitle={`Trend: ${velocity.data?.trend || 'stable'}`}
          icon={Activity}
          variant="purple"
        />

        <MetricCard
          title="Goal Progress"
          value={`${goalAnalytics.data?.average_progress?.toFixed(0) || 0}%`}
          subtitle={`${goalAnalytics.data?.total_goals || 0} total goals`}
          icon={Target}
          variant="orange"
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <CompletionChart
          title="Tasks by Category"
          data={categoryData}
          type="bar"
        />

        <CompletionChart
          title="Tasks by Priority"
          data={priorityData}
          type="pie"
        />
      </div>

      {/* Velocity Chart */}
      <VelocityChart
        title="Daily Task Completion"
        data={velocity.data?.daily_completion || {}}
        subtitle={`Best day: ${velocity.data?.best_day?.tasks_completed || 0} tasks | Worst day: ${velocity.data?.worst_day?.tasks_completed || 0} tasks`}
      />

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <CompletionChart
          title="Goals by Horizon"
          data={horizonData}
          type="bar"
        />

        {/* Time Tracking */}
        {taskAnalytics.data?.time_tracking && (
          <div className="space-y-4">
            <MetricCard
              title="Estimated Hours"
              value={taskAnalytics.data.time_tracking.total_estimated_hours?.toFixed(1) || 0}
              subtitle="total estimated time"
              icon={Calendar}
              variant="blue"
            />
            <MetricCard
              title="Actual Hours"
              value={taskAnalytics.data.time_tracking.total_actual_hours?.toFixed(1) || 0}
              subtitle="total time spent"
              icon={BarChart3}
              variant="green"
            />
            <MetricCard
              title="Estimation Accuracy"
              value={`${taskAnalytics.data.time_tracking.accuracy_rate?.toFixed(0) || 0}%`}
              subtitle="how accurate your estimates are"
              icon={Activity}
              variant="purple"
            />
          </div>
        )}
      </div>

      {/* AI Insights */}
      <InsightsPanel
        insights={trends.data?.insights || []}
        trend={velocity.data?.trend}
        categoryTrends={trends.data?.category_trends}
      />

      {/* Goals at Risk */}
      {goalAnalytics.data?.at_risk_goals && goalAnalytics.data.at_risk_goals.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-red-900 mb-4">⚠️ Goals at Risk</h3>
          <div className="space-y-3">
            {goalAnalytics.data.at_risk_goals.map((goal) => (
              <div
                key={goal.goal_id}
                className="flex items-center justify-between bg-white rounded-lg p-4"
              >
                <div>
                  <h4 className="font-medium text-gray-900">{goal.title}</h4>
                  <p className="text-sm text-gray-600">
                    Progress: {goal.progress}%
                    {goal.days_until_target && ` • ${goal.days_until_target} days until target`}
                  </p>
                </div>
                <div className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium">
                  {goal.risk_level}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Goals Near Completion */}
      {goalAnalytics.data?.goals_near_completion && goalAnalytics.data.goals_near_completion.length > 0 && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-green-900 mb-4">🎯 Almost There!</h3>
          <div className="space-y-3">
            {goalAnalytics.data.goals_near_completion.map((goal) => (
              <div
                key={goal.goal_id}
                className="flex items-center justify-between bg-white rounded-lg p-4"
              >
                <div>
                  <h4 className="font-medium text-gray-900">{goal.title}</h4>
                  <p className="text-sm text-gray-600">
                    Progress: {goal.progress}% • {goal.remaining_tasks} tasks remaining
                  </p>
                </div>
                <div className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                  {goal.progress}%
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
