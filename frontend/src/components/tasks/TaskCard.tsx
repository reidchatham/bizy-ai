import type { Task } from '../../types';
import { Card, CardContent } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { CheckCircle2, Circle, Edit, Trash2, Clock } from 'lucide-react';
import { format } from 'date-fns';

interface TaskCardProps {
  task: Task;
  onComplete?: (id: number) => void;
  onUncomplete?: (id: number) => void;
  onEdit?: (task: Task) => void;
  onDelete?: (id: number) => void;
}

const priorityColors = {
  1: 'destructive',
  2: 'warning',
  3: 'default',
} as const;

const priorityLabels = {
  1: 'High',
  2: 'Medium',
  3: 'Low',
};

const statusColors = {
  pending: 'default',
  in_progress: 'secondary',
  completed: 'success',
  blocked: 'warning',
  cancelled: 'outline',
} as const;

export function TaskCard({ task, onComplete, onUncomplete, onEdit, onDelete }: TaskCardProps) {
  const isCompleted = task.status === 'completed';
  const isOverdue = task.due_date && new Date(task.due_date) < new Date() && !isCompleted;

  return (
    <Card className={`transition-all hover:shadow-md ${isCompleted ? 'opacity-75' : ''}`}>
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          {/* Completion checkbox */}
          <button
            onClick={() => (isCompleted ? onUncomplete?.(task.id) : onComplete?.(task.id))}
            className="mt-1 text-gray-500 hover:text-blue-600 transition-colors"
          >
            {isCompleted ? (
              <CheckCircle2 className="w-5 h-5 text-green-600" />
            ) : (
              <Circle className="w-5 h-5" />
            )}
          </button>

          {/* Task content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <div>
                <h3
                  className={`font-medium ${
                    isCompleted ? 'line-through text-gray-500' : 'text-gray-900'
                  }`}
                >
                  {task.title}
                </h3>
                {task.description && (
                  <p className="text-sm text-gray-600 mt-1 line-clamp-2">{task.description}</p>
                )}
              </div>

              {/* Action buttons */}
              <div className="flex gap-1">
                {onEdit && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onEdit(task)}
                    className="h-8 w-8 p-0"
                  >
                    <Edit className="w-4 h-4" />
                  </Button>
                )}
                {onDelete && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onDelete(task.id)}
                    className="h-8 w-8 p-0 text-red-600 hover:text-red-700 hover:bg-red-50"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                )}
              </div>
            </div>

            {/* Metadata */}
            <div className="flex flex-wrap items-center gap-2 mt-3">
              {/* Priority badge */}
              <Badge variant={priorityColors[task.priority as keyof typeof priorityColors]}>
                {priorityLabels[task.priority as keyof typeof priorityLabels]}
              </Badge>

              {/* Status badge */}
              <Badge variant={statusColors[task.status as keyof typeof statusColors]}>
                {task.status.replace('_', ' ')}
              </Badge>

              {/* Category */}
              {task.category && (
                <Badge variant="outline" className="capitalize">
                  {task.category}
                </Badge>
              )}

              {/* Due date */}
              {task.due_date && (
                <div
                  className={`flex items-center gap-1 text-xs ${
                    isOverdue ? 'text-red-600 font-medium' : 'text-gray-600'
                  }`}
                >
                  <Clock className="w-3 h-3" />
                  {format(new Date(task.due_date), 'MMM d, yyyy')}
                  {isOverdue && <span className="ml-1">(Overdue)</span>}
                </div>
              )}

              {/* Time tracking */}
              {task.estimated_hours && (
                <div className="text-xs text-gray-600">
                  Est: {task.estimated_hours}h
                  {task.actual_hours && ` • Actual: ${task.actual_hours}h`}
                </div>
              )}
            </div>

            {/* Tags */}
            {task.tags && task.tags.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                {task.tags.map((tag) => (
                  <span
                    key={tag}
                    className="text-xs px-2 py-0.5 bg-gray-100 text-gray-700 rounded-full"
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
