// Chat message display component
'use client';

import { useChatStore } from '@/lib/store';
import { useEffect, useRef } from 'react';

export default function ChatPanel() {
  const { messages } = useChatStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-5 space-y-3 bg-dark border-l border-r border-border">
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-[70%] px-4 py-3 rounded-lg ${
              msg.type === 'user'
                ? 'bg-primary text-dark rounded-br-none'
                : msg.type === 'error'
                  ? 'bg-red-600 text-white rounded-bl-none'
                  : 'bg-card border border-primary rounded-bl-none'
            }`}
          >
            <p className="break-words text-sm">{msg.text}</p>
          </div>
        </div>
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
}
