import React from 'react';
import { Badge } from '../ui/badge';
import { ContainerStatus } from '../../lib/sse-context';

interface LiveStatusBadgeProps {
  status: ContainerStatus;
  showAnimation?: boolean;
}

const statusConfig = {
  running: {
    label: 'Running',
    className: 'bg-green-500 hover:bg-green-600 text-white',
    dotColor: 'bg-green-300',
  },
  exited: {
    label: 'Exited',
    className: 'bg-gray-500 hover:bg-gray-600 text-white',
    dotColor: 'bg-gray-300',
  },
  deploying: {
    label: 'Deploying',
    className: 'bg-yellow-500 hover:bg-yellow-600 text-white',
    dotColor: 'bg-yellow-300',
  },
  inactive: {
    label: 'Inactive',
    className: 'bg-gray-400 hover:bg-gray-500 text-white',
    dotColor: 'bg-gray-200',
  },
  error: {
    label: 'Error',
    className: 'bg-red-500 hover:bg-red-600 text-white',
    dotColor: 'bg-red-300',
  },
  removing: {
    label: 'Removing',
    className: 'bg-red-500 hover:bg-red-600 text-white',
    dotColor: 'bg-red-300',
  },
  unknown: {
    label: 'Unknown',
    className: 'bg-gray-400 hover:bg-gray-500 text-white',
    dotColor: 'bg-gray-200',
  },
};

export const LiveStatusBadge: React.FC<LiveStatusBadgeProps> = ({ 
  status, 
  showAnimation = true 
}) => {
  const config = statusConfig[status];
  const shouldAnimate = showAnimation && (status === 'running' || status === 'deploying');

  return (
    <Badge className={`${config.className} flex items-center gap-1.5`}>
      {shouldAnimate && (
        <span className="relative flex h-2 w-2">
          <span
            className={`animate-ping absolute inline-flex h-full w-full rounded-full ${config.dotColor} opacity-75`}
          />
          <span
            className={`relative inline-flex rounded-full h-2 w-2 ${config.dotColor}`}
          />
        </span>
      )}
      {config.label}
    </Badge>
  );
};
