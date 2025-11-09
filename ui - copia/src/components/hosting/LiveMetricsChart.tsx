import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid } from 'recharts';
import { Activity, Cpu, HardDrive, TrendingUp } from 'lucide-react';
import { ContainerMetrics } from '../../lib/sse-context';

interface LiveMetricsChartProps {
  metrics: ContainerMetrics;
  projectId: string;
}

interface MetricHistory {
  timestamp: string;
  cpu: number;
  memory: number;
}

export const LiveMetricsChart: React.FC<LiveMetricsChartProps> = ({ metrics, projectId }) => {
  const [history, setHistory] = useState<MetricHistory[]>([]);

  useEffect(() => {
    const newPoint: MetricHistory = {
      timestamp: new Date().toLocaleTimeString(),
      cpu: metrics.cpu,
      memory: metrics.memory,
    };

    setHistory((prev) => {
      const updated = [...prev, newPoint];
      // Mantener solo los últimos 10 puntos
      return updated.slice(-10);
    });
  }, [metrics]);

  return (
    <div className="space-y-4">
      {/* Métricas Actuales */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">CPU Usage</CardTitle>
            <Cpu className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">{metrics.cpu.toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground mt-1">
              <TrendingUp className="h-3 w-3 inline mr-1" />
              Live update
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Memory Usage</CardTitle>
            <HardDrive className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">{metrics.memory.toFixed(0)} MB</div>
            <p className="text-xs text-muted-foreground mt-1">
              <TrendingUp className="h-3 w-3 inline mr-1" />
              Live update
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Requests</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">{metrics.requests}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Uptime: {metrics.uptime}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Gráfico en Tiempo Real */}
      {history.length > 1 && (
        <Card>
          <CardHeader>
            <CardTitle>Real-time Performance</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={history}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis 
                  dataKey="timestamp" 
                  className="text-xs"
                  stroke="currentColor"
                />
                <YAxis 
                  className="text-xs"
                  stroke="currentColor"
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'hsl(var(--background))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '6px',
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="cpu"
                  stroke="#10b981"
                  strokeWidth={2}
                  dot={false}
                  name="CPU %"
                />
                <Line
                  type="monotone"
                  dataKey="memory"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={false}
                  name="Memory MB"
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
