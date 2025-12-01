import { useState } from 'react';
import { Plus, Target } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { GoalList } from '../components/goals/GoalList';
import { GoalFilters } from '../components/goals/GoalFilters';
import { GoalDialog } from '../components/goals/GoalDialog';
import { GoalBreakdownDialog } from '../components/goals/GoalBreakdownDialog';
import {
  useGoals,
  useCreateGoal,
  useUpdateGoal,
  useDeleteGoal,
  useCalculateGoalProgress,
} from '../hooks/useGoals';
import type { GoalFilters as GoalFiltersType, CreateGoalData, UpdateGoalData } from '../services/goals';
import type { Goal } from '../types';

export default function Goals() {
  const [filters, setFilters] = useState<GoalFiltersType>({});
  const [dialogOpen, setDialogOpen] = useState(false);
  const [breakdownDialogOpen, setBreakdownDialogOpen] = useState(false);
  const [selectedGoal, setSelectedGoal] = useState<Goal | null>(null);
  const [breakdownGoal, setBreakdownGoal] = useState<Goal | null>(null);

  // Queries and mutations
  const { data: goals = [], isLoading, error } = useGoals(filters);
  const createGoal = useCreateGoal();
  const updateGoal = useUpdateGoal();
  const deleteGoal = useDeleteGoal();
  const calculateProgress = useCalculateGoalProgress();

  const handleCreateClick = () => {
    setSelectedGoal(null);
    setDialogOpen(true);
  };

  const handleEditClick = (goal: Goal) => {
    setSelectedGoal(goal);
    setDialogOpen(true);
  };

  const handleBreakdownClick = (goal: Goal) => {
    setBreakdownGoal(goal);
    setBreakdownDialogOpen(true);
  };

  const handleSubmit = async (data: CreateGoalData | UpdateGoalData) => {
    if (selectedGoal) {
      await updateGoal.mutateAsync({ id: selectedGoal.id, data });
    } else {
      await createGoal.mutateAsync(data as CreateGoalData);
    }
    setDialogOpen(false);
    setSelectedGoal(null);
  };

  const handleDelete = async (id: number) => {
    if (confirm('Are you sure you want to delete this goal? All related tasks will remain.')) {
      await deleteGoal.mutateAsync(id);
    }
  };

  const handleCalculateProgress = async (id: number) => {
    await calculateProgress.mutateAsync(id);
  };

  const handleBreakdownSuccess = () => {
    // Refresh goals after tasks are created
    setBreakdownDialogOpen(false);
    setBreakdownGoal(null);
  };

  const isSubmitting = createGoal.isPending || updateGoal.isPending;

  // Group goals by horizon and status
  const yearlyGoals = goals.filter((g) => g.horizon === 'yearly');
  const quarterlyGoals = goals.filter((g) => g.horizon === 'quarterly');
  const monthlyGoals = goals.filter((g) => g.horizon === 'monthly');
  const completedGoals = goals.filter((g) => g.status === 'completed');
  const activeGoals = goals.filter((g) => g.status === 'active');

  // Calculate average progress
  const avgProgress = goals.length > 0
    ? Math.round(goals.reduce((sum, g) => sum + (g.progress_percentage || 0), 0) / goals.length)
    : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Goals</h1>
          <p className="text-gray-600 mt-1">
            Define and track your goals with AI-powered task breakdown
          </p>
        </div>
        <Button onClick={handleCreateClick}>
          <Plus className="w-4 h-4 mr-2" />
          New Goal
        </Button>
      </div>

      {/* Filters */}
      <GoalFilters filters={filters} onChange={setFilters} />

      {/* Goal Statistics */}
      {!isLoading && goals.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-1">
              <Target className="w-4 h-4 text-gray-600" />
              <div className="text-2xl font-bold text-gray-900">{goals.length}</div>
            </div>
            <div className="text-sm text-gray-600">Total Goals</div>
          </div>

          <div className="bg-blue-50 rounded-lg p-4">
            <div className="text-2xl font-bold text-blue-700">{yearlyGoals.length}</div>
            <div className="text-sm text-blue-600">Yearly</div>
          </div>

          <div className="bg-purple-50 rounded-lg p-4">
            <div className="text-2xl font-bold text-purple-700">{quarterlyGoals.length}</div>
            <div className="text-sm text-purple-600">Quarterly</div>
          </div>

          <div className="bg-green-50 rounded-lg p-4">
            <div className="text-2xl font-bold text-green-700">{monthlyGoals.length}</div>
            <div className="text-sm text-green-600">Monthly</div>
          </div>

          <div className="bg-orange-50 rounded-lg p-4">
            <div className="text-2xl font-bold text-orange-700">{activeGoals.length}</div>
            <div className="text-sm text-orange-600">Active</div>
          </div>

          <div className="bg-emerald-50 rounded-lg p-4">
            <div className="text-2xl font-bold text-emerald-700">{completedGoals.length}</div>
            <div className="text-sm text-emerald-600">Completed</div>
          </div>
        </div>
      )}

      {/* Average Progress */}
      {!isLoading && goals.length > 0 && (
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 border border-blue-100">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-gray-900 mb-1">Average Progress</h3>
              <p className="text-sm text-gray-600">Across all your goals</p>
            </div>
            <div className="text-4xl font-bold text-blue-700">{avgProgress}%</div>
          </div>
        </div>
      )}

      {/* Goal List */}
      <div>
        <GoalList
          goals={goals}
          isLoading={isLoading}
          error={error}
          onEdit={handleEditClick}
          onDelete={handleDelete}
          onBreakdown={handleBreakdownClick}
          onCalculateProgress={handleCalculateProgress}
        />
      </div>

      {/* Create/Edit Dialog */}
      <GoalDialog
        goal={selectedGoal}
        open={dialogOpen}
        onOpenChange={(open) => {
          setDialogOpen(open);
          if (!open) setSelectedGoal(null);
        }}
        onSubmit={handleSubmit}
        isLoading={isSubmitting}
      />

      {/* AI Breakdown Dialog */}
      <GoalBreakdownDialog
        goal={breakdownGoal}
        open={breakdownDialogOpen}
        onOpenChange={(open) => {
          setBreakdownDialogOpen(open);
          if (!open) setBreakdownGoal(null);
        }}
        onSuccess={handleBreakdownSuccess}
      />
    </div>
  );
}
