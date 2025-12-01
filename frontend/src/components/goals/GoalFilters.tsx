import { Input } from '../ui/Input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/Select';
import { Search } from 'lucide-react';
import type { GoalFilters as GoalFiltersType } from '../../services/goals';

interface GoalFiltersProps {
  filters: GoalFiltersType;
  onChange: (filters: GoalFiltersType) => void;
}

export function GoalFilters({ filters, onChange }: GoalFiltersProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <Input
          placeholder="Search goals..."
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
          <SelectItem value="not_started">Not Started</SelectItem>
          <SelectItem value="in_progress">In Progress</SelectItem>
          <SelectItem value="completed">Completed</SelectItem>
          <SelectItem value="on_hold">On Hold</SelectItem>
          <SelectItem value="cancelled">Cancelled</SelectItem>
        </SelectContent>
      </Select>

      {/* Horizon filter */}
      <Select
        value={filters.horizon || 'all'}
        onValueChange={(value) =>
          onChange({ ...filters, horizon: value === 'all' ? undefined : value as any })
        }
      >
        <SelectTrigger>
          <SelectValue placeholder="All horizons" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All horizons</SelectItem>
          <SelectItem value="yearly">Yearly</SelectItem>
          <SelectItem value="quarterly">Quarterly</SelectItem>
          <SelectItem value="monthly">Monthly</SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}
