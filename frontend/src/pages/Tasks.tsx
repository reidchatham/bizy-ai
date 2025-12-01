import { useState } from 'react';
import { Plus } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { TaskList } from '../components/tasks/TaskList';
import { TaskFilters } from '../components/tasks/TaskFilters';
import { TaskDialog } from '../components/tasks/TaskDialog';
import {
  useTasks,
  useCreateTask,
  useUpdateTask,
  useDeleteTask,
  useCompleteTask,
  useUncompleteTask,
} from '../hooks/useTasks';
import type { TaskFilters as TaskFiltersType, CreateTaskData, UpdateTaskData } from '../services/tasks';
import type { Task } from '../types';

export default function Tasks() {
  const [filters, setFilters] = useState<TaskFiltersType>({});
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);

  // Queries and mutations
  const { data: tasks = [], isLoading, error } = useTasks(filters);
  const createTask = useCreateTask();
  const updateTask = useUpdateTask();
  const deleteTask = useDeleteTask();
  const completeTask = useCompleteTask();
  const uncompleteTask = useUncompleteTask();

  const handleCreateClick = () => {
    setSelectedTask(null);
    setDialogOpen(true);
  };

  const handleEditClick = (task: Task) => {
    setSelectedTask(task);
    setDialogOpen(true);
  };

  const handleSubmit = async (data: CreateTaskData | UpdateTaskData) => {
    if (selectedTask) {
      await updateTask.mutateAsync({ id: selectedTask.id, data });
    } else {
      await createTask.mutateAsync(data as CreateTaskData);
    }
    setDialogOpen(false);
    setSelectedTask(null);
  };

  const handleDelete = async (id: number) => {
    if (confirm('Are you sure you want to delete this task?')) {
      await deleteTask.mutateAsync(id);
    }
  };

  const handleComplete = async (id: number) => {
    await completeTask.mutateAsync({ id });
  };

  const handleUncomplete = async (id: number) => {
    await uncompleteTask.mutateAsync(id);
  };

  const isSubmitting = createTask.isPending || updateTask.isPending;

  // Group tasks by status for better organization
  const pendingTasks = tasks.filter((t) => t.status === 'pending');
  const inProgressTasks = tasks.filter((t) => t.status === 'in_progress');
  const completedTasks = tasks.filter((t) => t.status === 'completed');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Tasks</h1>
          <p className="text-gray-600 mt-1">
            Manage your tasks and track your progress
          </p>
        </div>
        <Button onClick={handleCreateClick}>
          <Plus className="w-4 h-4 mr-2" />
          New Task
        </Button>
      </div>

      {/* Filters */}
      <TaskFilters filters={filters} onChange={setFilters} />

      {/* Task Statistics */}
      {!isLoading && tasks.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="text-2xl font-bold text-blue-700">{tasks.length}</div>
            <div className="text-sm text-blue-600">Total Tasks</div>
          </div>
          <div className="bg-yellow-50 rounded-lg p-4">
            <div className="text-2xl font-bold text-yellow-700">{pendingTasks.length}</div>
            <div className="text-sm text-yellow-600">Pending</div>
          </div>
          <div className="bg-purple-50 rounded-lg p-4">
            <div className="text-2xl font-bold text-purple-700">{inProgressTasks.length}</div>
            <div className="text-sm text-purple-600">In Progress</div>
          </div>
          <div className="bg-green-50 rounded-lg p-4">
            <div className="text-2xl font-bold text-green-700">{completedTasks.length}</div>
            <div className="text-sm text-green-600">Completed</div>
          </div>
        </div>
      )}

      {/* Task List */}
      <div>
        <TaskList
          tasks={tasks}
          isLoading={isLoading}
          error={error}
          onComplete={handleComplete}
          onUncomplete={handleUncomplete}
          onEdit={handleEditClick}
          onDelete={handleDelete}
        />
      </div>

      {/* Create/Edit Dialog */}
      <TaskDialog
        task={selectedTask}
        open={dialogOpen}
        onOpenChange={(open) => {
          setDialogOpen(open);
          if (!open) setSelectedTask(null);
        }}
        onSubmit={handleSubmit}
        isLoading={isSubmitting}
      />
    </div>
  );
}
