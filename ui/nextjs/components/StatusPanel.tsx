// Status/health indicator panel
'use client';

import { useEffect } from 'react';
import { getHealth } from '@/lib/jarvis';
import { useChatStore } from '@/lib/store';

export default function StatusPanel() {
  const {
    sessionId,
    messageCount,
    lastResponseTime,
    ollamaOnline,
    memoryOnline,
    uptime,
    setStatus,
  } = useChatStore();

  useEffect(() => {
    const checkHealth = async () => {
      const health = await getHealth();
      if (health) {
        setStatus(health.ollama, health.memory, health.uptime_seconds);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, [setStatus]);

  const formatUptime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    return `${mins}m`;
  };

  return (
    <div className="flex flex-col bg-dark border-l border-border p-4 space-y-4">
      <h2 className="text-primary font-bold text-sm uppercase">Status</h2>

      <div className="space-y-2 text-xs">
        <div className="flex items-center gap-2">
          <div
            className={`w-3 h-3 rounded-full ${ollamaOnline ? 'bg-primary' : 'bg-red-600 animate-pulse'}`}
          />
          <span className="text-gray-400">Ollama</span>
          <span className="ml-auto text-primary font-mono">
            {ollamaOnline ? 'Online' : 'Offline'}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <div
            className={`w-3 h-3 rounded-full ${memoryOnline ? 'bg-primary' : 'bg-red-600 animate-pulse'}`}
          />
          <span className="text-gray-400">Memory</span>
          <span className="ml-auto text-primary font-mono">
            {memoryOnline ? 'Online' : 'Offline'}
          </span>
        </div>

        <div className="flex justify-between pt-2 border-t border-border">
          <span className="text-gray-400">Model</span>
          <span className="text-primary font-mono">phi3-mini</span>
        </div>

        <div className="flex justify-between">
          <span className="text-gray-400">Response</span>
          <span className="text-primary font-mono">{lastResponseTime}ms</span>
        </div>

        <div className="flex justify-between">
          <span className="text-gray-400">Messages</span>
          <span className="text-primary font-mono">{messageCount}</span>
        </div>

        <div className="flex justify-between">
          <span className="text-gray-400">Uptime</span>
          <span className="text-primary font-mono">{formatUptime(uptime)}</span>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-border">
        <p className="text-gray-500 text-xs font-mono break-all">
          Session: {sessionId.substring(0, 12)}...
        </p>
      </div>
    </div>
  );
}
