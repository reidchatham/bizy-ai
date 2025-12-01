import { Input } from '../ui/Input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/Select';
import { Search } from 'lucide-react';
import type { TaskFilters as TaskFiltersType } from '../../services/tasks';

interface TaskFiltersProps {
  filters: TaskFiltersType;
  onChange: (filters: TaskFiltersType) => void;
}

export function TaskFilters({ filters, onChange }: TaskFiltersProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      {/* Search */}
      <div className="relative md:col-span-2">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <Input
          placeholder="Search tasks..."
          value={filters.search || ''}
          onChange={(e) => onChange({ ...filters, search: e.target.value || undefined })}
          className="pl-9"
        />
      </div>

      {/* Status filter */}
      <Select
        value={filters.status || 'all'}
        onValueChange={(value) =>
          onChange({ ...filters, status: value === 'all' ? undefined : value as any })
        }
      >
        <SelectTrigger>
          <SelectValue placeholder="All statuses" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All statuses</SelectItem>
          <SelectItem value="pending">Pending</SelectItem>
          <SelectItem value="in_progress">In Progress</SelectItem>
          <SelectItem value="completed">Completed</SelectItem>
          <SelectItem value="cancelled">Cancelled</SelectItem>
        </SelectContent>
      </Select>

      {/* Priority filter */}
      <Select
        value={filters.priority?.toString() || 'all'}
        onValueChange={(value) =>
          onChange({ ...filters, priority: value === 'all' ? undefined : parseInt(value) as any })
        }
      >
        <SelectTrigger>
          <SelectValue placeholder="All priorities" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All priorities</SelectItem>
          <SelectItem value="1">High priority</SelectItem>
          <SelectItem value="2">Medium priority</SelectItem>
          <SelectItem value="3">Low priority</SelectItem>
        </SelectContent>
      </Select>

      {/* Category filter */}
      <Select
        value={filters.category || 'all'}
        onValueChange={(value) =>
          onChange({ ...filters, category: value === 'all' ? undefined : value })
        }
      >
        <SelectTrigger>
          <SelectValue placeholder="All categories" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All categories</SelectItem>
          <SelectItem value="development">Development</SelectItem>
          <SelectItem value="design">Design</SelectItem>
          <SelectItem value="testing">Testing</SelectItem>
          <SelectItem value="deployment">Deployment</SelectItem>
          <SelectItem value="documentation">Documentation</SelectItem>
          <SelectItem value="meeting">Meeting</SelectItem>
          <SelectItem value="research">Research</SelectItem>
          <SelectItem value="other">Other</SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}
