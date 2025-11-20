import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  Sunrise,
  CheckCircle2,
  Circle,
  Target,
  TrendingUp,
  AlertCircle,
  Lightbulb,
  ArrowRight,
} from 'lucide-react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Button,
  Badge,
  Progress,
  Spinner,
} from '../components/ui';
import api from '../services/api';
import { MorningBriefing, Task, Goal } from '../types';

export default function Dashboard() {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 60000);
    return () => clearInterval(timer);
  }, []);

  const { data: briefing, isLoading: briefingLoading } = useQuery<MorningBriefing>({
    queryKey: ['morning-briefing'],
    queryFn: async () => {
      const response = await api.get('/briefings/morning');
      return response.data;
    },
  });

  const { data: tasks, isLoading: tasksLoading } = useQuery<Task[]>({
    queryKey: ['tasks'],
    queryFn: async () => {
      const response = await api.get('/tasks/');
      return response.data;
    },
  });

  const { data: goals, isLoading: goalsLoading } = useQuery<Goal[]>({
    queryKey: ['goals'],
    queryFn: async () => {
      const response = await api.get('/goals/');
      return response.data;
    },
  });

  const greeting = () => {
    const hour = currentTime.getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const todayTasks = tasks?.filter(
    (task) =>
      task.due_date &&
      new Date(task.due_date).toDateString() === new Date().toDateString()
  ) || [];

  const completedToday = todayTasks.filter((task) => task.status === 'completed').length;
  const pendingTasks = tasks?.filter((task) => task.status === 'pending').length || 0;
  const inProgressTasks = tasks?.filter((task) => task.status === 'in_progress').length || 0;

  const activeGoals = goals?.filter((goal) => goal.status === 'active') || [];
  const completedGoals = goals?.filter((goal) => goal.status === 'completed').length || 0;

  const averageGoalProgress = activeGoals.length > 0
    ? activeGoals.reduce((sum, goal) => sum + (goal.progress || 0), 0) / activeGoals.length
    : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Sunrise className="h-8 w-8 text-orange-500" />
          {greeting()}
        </h1>
        <p className="text-[hsl(var(--muted-foreground))] mt-2">
          {currentTime.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
          })}
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Tasks</CardTitle>
            <Circle className="h-4 w-4 text-[hsl(var(--muted-foreground))]" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{pendingTasks}</div>
            <p className="text-xs text-[hsl(var(--muted-foreground))]">
              {inProgressTasks} in progress
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Due Today</CardTitle>
            <AlertCircle className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{todayTasks.length}</div>
            <p className="text-xs text-[hsl(var(--muted-foreground))]">
              {completedToday} completed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Goals</CardTitle>
            <Target className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{activeGoals.length}</div>
            <p className="text-xs text-[hsl(var(--muted-foreground))]">
              {completedGoals} completed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Progress</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{averageGoalProgress.toFixed(0)}%</div>
            <p className="text-xs text-[hsl(var(--muted-foreground))]">Across active goals</p>
          </CardContent>
        </Card>
      </div>

      {/* Morning Briefing */}
      {briefingLoading ? (
        <Card>
          <CardContent className="flex items-center justify-center py-12">
            <Spinner size="lg" />
          </CardContent>
        </Card>
      ) : briefing && (
        <Card className="border-orange-200 dark:border-orange-900">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sunrise className="h-5 w-5 text-orange-500" />
              Morning Briefing
            </CardTitle>
            <CardDescription>AI-powered insights for your day</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Yesterday Recap */}
            {briefing.yesterday_recap && (
              <div className="space-y-2">
                <h3 className="text-sm font-semibold flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-500" />
                  Yesterday's Wins
                </h3>
                <p className="text-sm text-[hsl(var(--muted-foreground))] pl-6">
                  {briefing.yesterday_recap}
                </p>
              </div>
            )}

            {/* Today's Mission */}
            <div className="space-y-2">
              <h3 className="text-sm font-semibold flex items-center gap-2">
                <Target className="h-4 w-4 text-blue-500" />
                Today's Mission
              </h3>
              <p className="text-sm pl-6">{briefing.todays_mission}</p>
            </div>

            {/* Watch Out For */}
            {briefing.watch_out_for && (
              <div className="space-y-2">
                <h3 className="text-sm font-semibold flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 text-orange-500" />
                  Watch Out For
                </h3>
                <p className="text-sm text-[hsl(var(--muted-foreground))] pl-6">
                  {briefing.watch_out_for}
                </p>
              </div>
            )}

            {/* Pro Tip */}
            {briefing.pro_tip && (
              <div className="space-y-2">
                <h3 className="text-sm font-semibold flex items-center gap-2">
                  <Lightbulb className="h-4 w-4 text-yellow-500" />
                  Pro Tip
                </h3>
                <p className="text-sm text-[hsl(var(--muted-foreground))] pl-6">
                  {briefing.pro_tip}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Today's Tasks */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Today's Tasks</CardTitle>
              <CardDescription>Tasks due today</CardDescription>
            </div>
            <Link to="/tasks">
              <Button variant="ghost" size="sm">
                View All <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </CardHeader>
        <CardContent>
          {tasksLoading ? (
            <div className="flex justify-center py-8">
              <Spinner />
            </div>
          ) : todayTasks.length === 0 ? (
            <p className="text-sm text-[hsl(var(--muted-foreground))] text-center py-8">
              No tasks due today. Great job staying ahead!
            </p>
          ) : (
            <div className="space-y-3">
              {todayTasks.slice(0, 5).map((task) => (
                <div
                  key={task.id}
                  className="flex items-center justify-between p-3 border rounded-lg hover:bg-[hsl(var(--accent))] transition-colors"
                >
                  <div className="flex items-center gap-3">
                    {task.status === 'completed' ? (
                      <CheckCircle2 className="h-5 w-5 text-green-500" />
                    ) : (
                      <Circle className="h-5 w-5 text-[hsl(var(--muted-foreground))]" />
                    )}
                    <div>
                      <p className={`text-sm font-medium ${task.status === 'completed' ? 'line-through text-[hsl(var(--muted-foreground))]' : ''}`}>
                        {task.title}
                      </p>
                      {task.category && (
                        <p className="text-xs text-[hsl(var(--muted-foreground))]">
                          {task.category}
                        </p>
                      )}
                    </div>
                  </div>
                  <Badge
                    variant={
                      task.priority === 1
                        ? 'destructive'
                        : task.priority === 2
                        ? 'warning'
                        : 'secondary'
                    }
                  >
                    {task.priority === 1 ? 'High' : task.priority === 2 ? 'Medium' : 'Low'}
                  </Badge>
                </div>
              ))}
              {todayTasks.length > 5 && (
                <Link to="/tasks">
                  <Button variant="outline" className="w-full">
                    View {todayTasks.length - 5} more tasks
                  </Button>
                </Link>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Active Goals */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Active Goals</CardTitle>
              <CardDescription>Track your progress</CardDescription>
            </div>
            <Link to="/goals">
              <Button variant="ghost" size="sm">
                View All <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </CardHeader>
        <CardContent>
          {goalsLoading ? (
            <div className="flex justify-center py-8">
              <Spinner />
            </div>
          ) : activeGoals.length === 0 ? (
            <p className="text-sm text-[hsl(var(--muted-foreground))] text-center py-8">
              No active goals. Set a new goal to get started!
            </p>
          ) : (
            <div className="space-y-4">
              {activeGoals.slice(0, 3).map((goal) => (
                <div key={goal.id} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Target className="h-4 w-4 text-blue-500" />
                      <p className="text-sm font-medium">{goal.title}</p>
                    </div>
                    <Badge variant="outline">
                      {goal.horizon === 'yearly' ? 'Yearly' : goal.horizon === 'quarterly' ? 'Quarterly' : 'Monthly'}
                    </Badge>
                  </div>
                  <Progress value={goal.progress || 0} showLabel />
                </div>
              ))}
              {activeGoals.length > 3 && (
                <Link to="/goals">
                  <Button variant="outline" className="w-full">
                    View {activeGoals.length - 3} more goals
                  </Button>
                </Link>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
