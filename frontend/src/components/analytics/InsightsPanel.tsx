import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Lightbulb, TrendingUp, TrendingDown, Minus, Sparkles } from 'lucide-react';

interface InsightsPanelProps {
  insights: string[];
  trend?: 'improving' | 'stable' | 'declining';
  categoryTrends?: Record<string, {
    trend: 'increasing' | 'stable' | 'decreasing';
    change_percentage: number;
  }>;
}

const trendIcons = {
  improving: TrendingUp,
  stable: Minus,
  declining: TrendingDown,
};

const trendColors = {
  improving: 'text-green-600',
  stable: 'text-gray-600',
  declining: 'text-red-600',
};

const trendLabels = {
  improving: 'Improving',
  stable: 'Stable',
  declining: 'Declining',
};

const categoryTrendColors = {
  increasing: 'success',
  stable: 'default',
  decreasing: 'warning',
} as const;

export function InsightsPanel({ insights, trend, categoryTrends }: InsightsPanelProps) {
  const TrendIcon = trend ? trendIcons[trend] : null;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-600" />
            <CardTitle>AI Insights</CardTitle>
          </div>
          {trend && TrendIcon && (
            <div className="flex items-center gap-2">
              <TrendIcon className={`w-5 h-5 ${trendColors[trend]}`} />
              <span className={`text-sm font-medium ${trendColors[trend]}`}>
                {trendLabels[trend]}
              </span>
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Insights List */}
        {insights.length > 0 ? (
          <div className="space-y-3">
            {insights.map((insight, index) => (
              <div
                key={index}
                className="flex gap-3 p-3 bg-purple-50 rounded-lg border border-purple-100"
              >
                <Lightbulb className="w-5 h-5 text-purple-600 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-gray-700">{insight}</p>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <Sparkles className="w-12 h-12 mx-auto mb-3 text-gray-400" />
            <p>No insights available yet. Complete more tasks to get AI-powered insights!</p>
          </div>
        )}

        {/* Category Trends */}
        {categoryTrends && Object.keys(categoryTrends).length > 0 && (
          <div className="pt-4 border-t border-gray-200">
            <h4 className="text-sm font-medium text-gray-700 mb-3">Category Trends</h4>
            <div className="flex flex-wrap gap-2">
              {Object.entries(categoryTrends).map(([category, data]) => (
                <div
                  key={category}
                  className="flex items-center gap-2 px-3 py-2 bg-gray-50 rounded-lg"
                >
                  <span className="text-sm font-medium capitalize">{category}</span>
                  <Badge variant={categoryTrendColors[data.trend]} className="text-xs">
                    {data.trend === 'increasing' && '+'}
                    {data.trend === 'decreasing' && '-'}
                    {Math.abs(data.change_percentage)}%
                  </Badge>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
