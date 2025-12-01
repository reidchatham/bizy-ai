import { Card, CardContent } from '../ui/Card';
import type { LucideIcon } from 'lucide-react';
import { Badge } from '../ui/Badge';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: LucideIcon;
  trend?: {
    value: number;
    label: string;
  };
  variant?: 'default' | 'blue' | 'green' | 'purple' | 'orange' | 'red';
}

const variantStyles = {
  default: {
    bg: 'bg-gray-50',
    text: 'text-gray-900',
    icon: 'text-gray-600',
    subtitle: 'text-gray-600',
  },
  blue: {
    bg: 'bg-blue-50',
    text: 'text-blue-900',
    icon: 'text-blue-600',
    subtitle: 'text-blue-600',
  },
  green: {
    bg: 'bg-green-50',
    text: 'text-green-900',
    icon: 'text-green-600',
    subtitle: 'text-green-600',
  },
  purple: {
    bg: 'bg-purple-50',
    text: 'text-purple-900',
    icon: 'text-purple-600',
    subtitle: 'text-purple-600',
  },
  orange: {
    bg: 'bg-orange-50',
    text: 'text-orange-900',
    icon: 'text-orange-600',
    subtitle: 'text-orange-600',
  },
  red: {
    bg: 'bg-red-50',
    text: 'text-red-900',
    icon: 'text-red-600',
    subtitle: 'text-red-600',
  },
};

export function MetricCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  variant = 'default',
}: MetricCardProps) {
  const styles = variantStyles[variant];

  return (
    <Card className={`${styles.bg} border-none`}>
      <CardContent className="p-6">
        <div className="flex items-start justify-between mb-2">
          <div className="text-sm font-medium text-gray-600">{title}</div>
          {Icon && <Icon className={`w-5 h-5 ${styles.icon}`} />}
        </div>

        <div className={`text-3xl font-bold ${styles.text} mb-1`}>{value}</div>

        {subtitle && <div className={`text-sm ${styles.subtitle}`}>{subtitle}</div>}

        {trend && (
          <div className="mt-3 pt-3 border-t border-gray-200">
            <div className="flex items-center gap-2">
              <Badge
                variant={trend.value > 0 ? 'success' : trend.value < 0 ? 'destructive' : 'default'}
                className="text-xs"
              >
                {trend.value > 0 ? '+' : ''}
                {trend.value}%
              </Badge>
              <span className="text-xs text-gray-600">{trend.label}</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
