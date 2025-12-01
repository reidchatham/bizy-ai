import type { Goal } from '../../types';
import { Card, CardContent } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { Progress } from '../ui/Progress';
import { Edit, Trash2, Target, Sparkles, Calendar } from 'lucide-react';
import { format } from 'date-fns';

interface GoalCardProps {
  goal: Goal;
  onEdit?: (goal: Goal) => void;
  onDelete?: (id: number) => void;
  onBreakdown?: (goal: Goal) => void;
  onCalculateProgress?: (id: number) => void;
}

const horizonColors = {
  yearly: 'bg-blue-500',
  quarterly: 'bg-purple-500',
  monthly: 'bg-green-500',
  weekly: 'bg-orange-500',
} as const;

const horizonBadgeVariants = {
  yearly: 'default' as const,
  quarterly: 'secondary' as const,
  monthly: 'success' as const,
  weekly: 'warning' as const,
};

const horizonLabels = {
  yearly: 'Yearly',
  quarterly: 'Quarterly',
  monthly: 'Monthly',
  weekly: 'Weekly',
};

const statusColors = {
  active: 'secondary',
  completed: 'success',
  on_hold: 'warning',
  cancelled: 'outline',
} as const;

const statusLabels = {
  active: 'Active',
  completed: 'Completed',
  on_hold: 'On Hold',
  cancelled: 'Cancelled',
};

export function GoalCard({
  goal,
  onEdit,
  onDelete,
  onBreakdown,
  onCalculateProgress,
}: GoalCardProps) {
  const isCompleted = goal.status === 'completed';
  const progress = goal.progress_percentage || 0;

  return (
    <Card className={`transition-all hover:shadow-md ${isCompleted ? 'opacity-90' : ''}`}>
      <CardContent className="p-5">
        {/* Header */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              <Target className={`w-4 h-4 ${horizonColors[goal.horizon].replace('bg-', 'text-')}`} />
              <h3
                className={`font-semibold text-lg ${
                  isCompleted ? 'line-through text-gray-500' : 'text-gray-900'
                }`}
              >
                {goal.title}
              </h3>
            </div>
            {goal.description && (
              <p className="text-sm text-gray-600 line-clamp-2">{goal.description}</p>
            )}
          </div>

          {/* Action buttons */}
          <div className="flex gap-1">
            {onBreakdown && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onBreakdown(goal)}
                className="h-8 w-8 p-0 text-purple-600 hover:text-purple-700 hover:bg-purple-50"
                title="AI Breakdown"
              >
                <Sparkles className="w-4 h-4" />
              </Button>
            )}
            {onEdit && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onEdit(goal)}
                className="h-8 w-8 p-0"
              >
                <Edit className="w-4 h-4" />
              </Button>
            )}
            {onDelete && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onDelete(goal.id)}
                className="h-8 w-8 p-0 text-red-600 hover:text-red-700 hover:bg-red-50"
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            )}
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-3">
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm font-medium text-gray-700">Progress</span>
            <span className="text-sm font-semibold text-gray-900">{progress}%</span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>

        {/* Metadata */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Horizon badge */}
          <Badge variant={horizonBadgeVariants[goal.horizon]}>
            {horizonLabels[goal.horizon]}
          </Badge>

          {/* Status badge */}
          <Badge variant={statusColors[goal.status]}>
            {statusLabels[goal.status]}
          </Badge>

          {/* Target date */}
          {goal.target_date && (
            <div className="flex items-center gap-1 text-xs text-gray-600">
              <Calendar className="w-3 h-3" />
              Target: {format(new Date(goal.target_date), 'MMM d, yyyy')}
            </div>
          )}

          {/* Parent goal indicator */}
          {goal.parent_goal_id && (
            <Badge variant="outline" className="text-xs">
              Sub-goal
            </Badge>
          )}
        </div>

        {/* Success Criteria */}
        {goal.success_criteria && (
          <div className="mt-3 pt-3 border-t border-gray-100">
            <p className="text-xs text-gray-600">
              <span className="font-medium">Success Criteria: </span>
              {goal.success_criteria}
            </p>
          </div>
        )}

        {/* Footer actions */}
        {onCalculateProgress && progress < 100 && (
          <div className="mt-3 pt-3 border-t border-gray-100">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onCalculateProgress(goal.id)}
              className="w-full text-xs"
            >
              Recalculate Progress
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
