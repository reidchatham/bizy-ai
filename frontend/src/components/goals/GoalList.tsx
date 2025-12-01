import type { Goal } from '../../types';
import { GoalCard } from './GoalCard';
import { Spinner } from '../ui/Spinner';
import { AlertCircle } from 'lucide-react';

interface GoalListProps {
  goals: Goal[];
  isLoading?: boolean;
  error?: Error | null;
  onEdit?: (goal: Goal) => void;
  onDelete?: (id: number) => void;
  onBreakdown?: (goal: Goal) => void;
  onCalculateProgress?: (id: number) => void;
}

export function GoalList({
  goals,
  isLoading,
  error,
  onEdit,
  onDelete,
  onBreakdown,
  onCalculateProgress,
}: GoalListProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error loading goals</h3>
          <p className="text-gray-600">{error.message}</p>
        </div>
      </div>
    );
  }

  if (goals.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">No goals found. Create your first goal to get started!</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {goals.map((goal) => (
        <GoalCard
          key={goal.id}
          goal={goal}
          onEdit={onEdit}
          onDelete={onDelete}
          onBreakdown={onBreakdown}
          onCalculateProgress={onCalculateProgress}
        />
      ))}
    </div>
  );
}
