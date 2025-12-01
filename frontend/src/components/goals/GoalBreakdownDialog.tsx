import { useState, useEffect } from 'react';
import type { Goal } from '../../types';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../ui/Dialog';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { Spinner } from '../ui/Spinner';
import { Sparkles, CheckCircle2, Circle, Clock, AlertCircle } from 'lucide-react';
import { useTriggerGoalBreakdown, useCreateTasksFromBreakdown } from '../../hooks/useGoals';
import type { BreakdownSuggestion } from '../../services/goals';

interface GoalBreakdownDialogProps {
  goal: Goal | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
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

export function GoalBreakdownDialog({ goal, open, onOpenChange, onSuccess }: GoalBreakdownDialogProps) {
  const [selectedTasks, setSelectedTasks] = useState<Set<number>>(new Set());
  const [suggestions, setSuggestions] = useState<BreakdownSuggestion[]>([]);
  const [reasoning, setReasoning] = useState<string>('');
  const [timeline, setTimeline] = useState<string>('');

  const breakdownMutation = useTriggerGoalBreakdown();
  const createTasksMutation = useCreateTasksFromBreakdown();

  // Trigger breakdown when dialog opens with a goal
  useEffect(() => {
    if (open && goal && !breakdownMutation.data && !breakdownMutation.isPending) {
      breakdownMutation.mutate(goal.id);
    }
  }, [open, goal]);

  // Update local state when breakdown completes
  useEffect(() => {
    if (breakdownMutation.data) {
      setSuggestions(breakdownMutation.data.suggestions);
      setReasoning(breakdownMutation.data.reasoning);
      setTimeline(breakdownMutation.data.estimated_timeline);
      // Select all tasks by default
      setSelectedTasks(new Set(breakdownMutation.data.suggestions.map((_, i) => i)));
    }
  }, [breakdownMutation.data]);

  // Reset state when dialog closes
  useEffect(() => {
    if (!open) {
      setSelectedTasks(new Set());
      setSuggestions([]);
      setReasoning('');
      setTimeline('');
      breakdownMutation.reset();
      createTasksMutation.reset();
    }
  }, [open]);

  const handleToggleTask = (index: number) => {
    const newSelected = new Set(selectedTasks);
    if (newSelected.has(index)) {
      newSelected.delete(index);
    } else {
      newSelected.add(index);
    }
    setSelectedTasks(newSelected);
  };

  const handleSelectAll = () => {
    setSelectedTasks(new Set(suggestions.map((_, i) => i)));
  };

  const handleDeselectAll = () => {
    setSelectedTasks(new Set());
  };

  const handleCreateTasks = async () => {
    if (!goal || selectedTasks.size === 0) return;

    await createTasksMutation.mutateAsync({
      id: goal.id,
      data: { task_indices: Array.from(selectedTasks) },
    });

    onSuccess?.();
    onOpenChange(false);
  };

  const isLoading = breakdownMutation.isPending;
  const hasError = breakdownMutation.isError;
  const hasData = breakdownMutation.data && suggestions.length > 0;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-600" />
            AI Goal Breakdown
          </DialogTitle>
          <DialogDescription>
            {goal ? `Breaking down: "${goal.title}"` : 'AI-powered task suggestions for your goal'}
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto py-4">
          {/* Loading State */}
          {isLoading && (
            <div className="flex flex-col items-center justify-center py-12">
              <Spinner size="lg" />
              <p className="mt-4 text-gray-600">AI is analyzing your goal...</p>
              <p className="text-sm text-gray-500 mt-2">This may take a few seconds</p>
            </div>
          )}

          {/* Error State */}
          {hasError && (
            <div className="flex flex-col items-center justify-center py-12">
              <AlertCircle className="w-12 h-12 text-red-500 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Failed to generate breakdown</h3>
              <p className="text-gray-600 text-center max-w-md">
                {(breakdownMutation.error as any)?.response?.data?.detail || 'An error occurred while generating the breakdown. Please try again.'}
              </p>
              <Button
                variant="outline"
                onClick={() => goal && breakdownMutation.mutate(goal.id)}
                className="mt-4"
              >
                Try Again
              </Button>
            </div>
          )}

          {/* Success State */}
          {hasData && (
            <div className="space-y-6">
              {/* AI Reasoning */}
              <div className="bg-purple-50 rounded-lg p-4 border border-purple-100">
                <h3 className="font-medium text-purple-900 mb-2 flex items-center gap-2">
                  <Sparkles className="w-4 h-4" />
                  AI Analysis
                </h3>
                <p className="text-sm text-purple-800 whitespace-pre-wrap">{reasoning}</p>
                {timeline && (
                  <div className="mt-3 pt-3 border-t border-purple-200">
                    <div className="flex items-center gap-2 text-sm">
                      <Clock className="w-4 h-4 text-purple-600" />
                      <span className="font-medium text-purple-900">Estimated Timeline:</span>
                      <span className="text-purple-800">{timeline}</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Selection Controls */}
              <div className="flex items-center justify-between">
                <h3 className="font-medium text-gray-900">
                  Suggested Tasks ({selectedTasks.size} of {suggestions.length} selected)
                </h3>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleSelectAll}
                    disabled={selectedTasks.size === suggestions.length}
                  >
                    Select All
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleDeselectAll}
                    disabled={selectedTasks.size === 0}
                  >
                    Deselect All
                  </Button>
                </div>
              </div>

              {/* Task Suggestions */}
              <div className="space-y-3">
                {suggestions.map((suggestion, index) => (
                  <div
                    key={index}
                    className={`border rounded-lg p-4 transition-all cursor-pointer hover:shadow-sm ${
                      selectedTasks.has(index)
                        ? 'border-blue-300 bg-blue-50'
                        : 'border-gray-200 bg-white'
                    }`}
                    onClick={() => handleToggleTask(index)}
                  >
                    <div className="flex items-start gap-3">
                      {/* Checkbox */}
                      <div className="mt-0.5">
                        {selectedTasks.has(index) ? (
                          <CheckCircle2 className="w-5 h-5 text-blue-600" />
                        ) : (
                          <Circle className="w-5 h-5 text-gray-400" />
                        )}
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <h4 className="font-medium text-gray-900 mb-1">{suggestion.title}</h4>
                        <p className="text-sm text-gray-600 mb-3">{suggestion.description}</p>

                        {/* Metadata */}
                        <div className="flex flex-wrap items-center gap-2">
                          <Badge variant={priorityColors[suggestion.priority]}>
                            {priorityLabels[suggestion.priority]}
                          </Badge>
                          <Badge variant="outline" className="capitalize">
                            {suggestion.category}
                          </Badge>
                          {suggestion.estimated_hours && (
                            <span className="text-xs text-gray-600">
                              Est: {suggestion.estimated_hours}h
                            </span>
                          )}
                        </div>

                        {/* AI Reasoning for this task */}
                        {suggestion.reasoning && (
                          <div className="mt-2 pt-2 border-t border-gray-100">
                            <p className="text-xs text-gray-500 italic">{suggestion.reasoning}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        {hasData && (
          <DialogFooter className="border-t pt-4">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleCreateTasks}
              disabled={selectedTasks.size === 0 || createTasksMutation.isPending}
            >
              {createTasksMutation.isPending
                ? 'Creating...'
                : `Create ${selectedTasks.size} Task${selectedTasks.size !== 1 ? 's' : ''}`}
            </Button>
          </DialogFooter>
        )}
      </DialogContent>
    </Dialog>
  );
}
