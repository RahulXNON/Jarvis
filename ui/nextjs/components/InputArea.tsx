// Input area for messages
'use client';

import { useState } from 'react';
import { sendChat } from '@/lib/jarvis';
import { useChatStore } from '@/lib/store';

export default function InputArea() {
  const [input, setInput] = useState('');
  const {
    addMessage,
    setLoading,
    setResponseTime,
    isLoading,
    sessionId,
  } = useChatStore();

  const handleSend = async () => {
    const message = input.trim();
    if (!message || isLoading) return;

    addMessage(message, 'user');
    setInput('');
    setLoading(true);

    const startTime = Date.now();
    const reader = await sendChat({ message, session_id: sessionId });

    if (!reader) {
      addMessage('Error: Could not send message', 'error');
      setLoading(false);
      return;
    }

    const decoder = new TextDecoder();
    let botMessage = '';
    let firstChunk = true;

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        botMessage += chunk;

        if (firstChunk) {
          addMessage(chunk, 'bot');
          firstChunk = false;
        } else {
          useChatStore.setState((state) => ({
            messages: state.messages.map((m, i) =>
              i === state.messages.length - 1
                ? { ...m, text: botMessage }
                : m
            ),
          }));
        }
      }

      setResponseTime(Date.now() - startTime);
    } catch (error) {
      addMessage('Error: Failed to stream response', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 border-t border-border bg-dark flex gap-3">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
          }
        }}
        placeholder="Message JARVIS..."
        disabled={isLoading}
        className="flex-1 px-4 py-2 bg-card border border-border text-white rounded focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20"
      />
      <button
        onClick={handleSend}
        disabled={isLoading}
        className="px-6 py-2 bg-primary text-dark font-bold rounded hover:bg-primary/90 disabled:opacity-50 transition"
      >
        {isLoading ? 'Sending...' : 'Send'}
      </button>
    </div>
  );
}
