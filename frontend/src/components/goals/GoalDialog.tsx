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
import { Input } from '../ui/Input';
import { Textarea } from '../ui/Textarea';
import { Label } from '../ui/Label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/Select';
import type { CreateGoalData, UpdateGoalData } from '../../services/goals';

interface GoalDialogProps {
  goal?: Goal | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: CreateGoalData | UpdateGoalData) => void;
  isLoading?: boolean;
}

export function GoalDialog({ goal, open, onOpenChange, onSubmit, isLoading }: GoalDialogProps) {
  const [formData, setFormData] = useState<CreateGoalData>({
    title: '',
    description: '',
    horizon: 'monthly',
    status: 'active',
    target_date: '',
    success_criteria: '',
    metrics: undefined,
  });

  // Reset form when dialog opens/closes or goal changes
  useEffect(() => {
    if (goal) {
      setFormData({
        title: goal.title,
        description: goal.description || '',
        horizon: goal.horizon,
        status: goal.status,
        target_date: goal.target_date || '',
        success_criteria: goal.success_criteria || '',
        metrics: goal.metrics || undefined,
        parent_goal_id: goal.parent_goal_id,
      });
    } else {
      setFormData({
        title: '',
        description: '',
        horizon: 'monthly',
        status: 'active',
        target_date: '',
        success_criteria: '',
        metrics: undefined,
      });
    }
  }, [goal, open]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Clean up the data
    const submitData: CreateGoalData | UpdateGoalData = {
      ...formData,
      description: formData.description || undefined,
      target_date: formData.target_date || undefined,
      success_criteria: formData.success_criteria || undefined,
      metrics: formData.metrics || undefined,
    };

    onSubmit(submitData);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{goal ? 'Edit Goal' : 'Create New Goal'}</DialogTitle>
          <DialogDescription>
            {goal ? 'Update the goal details below.' : 'Define a new goal to work towards.'}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Title */}
          <div>
            <Label htmlFor="title">
              Title <span className="text-red-500">*</span>
            </Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="Enter goal title"
              required
            />
          </div>

          {/* Description */}
          <div>
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Describe the goal in detail..."
              rows={3}
            />
          </div>

          {/* Row 1: Horizon, Status */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="horizon">
                Horizon <span className="text-red-500">*</span>
              </Label>
              <Select
                value={formData.horizon}
                onValueChange={(value: any) => setFormData({ ...formData, horizon: value })}
              >
                <SelectTrigger id="horizon">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="yearly">Yearly</SelectItem>
                  <SelectItem value="quarterly">Quarterly</SelectItem>
                  <SelectItem value="monthly">Monthly</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="status">Status</Label>
              <Select
                value={formData.status}
                onValueChange={(value: any) => setFormData({ ...formData, status: value })}
              >
                <SelectTrigger id="status">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="not_started">Not Started</SelectItem>
                  <SelectItem value="in_progress">In Progress</SelectItem>
                  <SelectItem value="completed">Completed</SelectItem>
                  <SelectItem value="on_hold">On Hold</SelectItem>
                  <SelectItem value="cancelled">Cancelled</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Target Date */}
          <div>
            <Label htmlFor="target_date">Target Date</Label>
            <Input
              id="target_date"
              type="date"
              value={formData.target_date}
              onChange={(e) => setFormData({ ...formData, target_date: e.target.value })}
            />
          </div>

          {/* Success Criteria */}
          <div>
            <Label htmlFor="success_criteria">Success Criteria</Label>
            <Textarea
              id="success_criteria"
              value={formData.success_criteria}
              onChange={(e) => setFormData({ ...formData, success_criteria: e.target.value })}
              placeholder="What does success look like for this goal?"
              rows={2}
            />
            <p className="text-xs text-gray-500 mt-1">
              Define clear, measurable criteria for success
            </p>
          </div>

          {/* Metrics - TODO: Add JSON editor for metrics */}

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={!formData.title || isLoading}>
              {isLoading ? 'Saving...' : goal ? 'Update Goal' : 'Create Goal'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
