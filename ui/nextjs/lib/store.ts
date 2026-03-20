// Global state management with Zustand
import { create } from 'zustand';

export interface Message {
  id: string;
  text: string;
  type: 'user' | 'bot' | 'error';
}

interface ChatStore {
  messages: Message[];
  sessionId: string;
  messageCount: number;
  isLoading: boolean;
  lastResponseTime: number;
  ollamaOnline: boolean;
  memoryOnline: boolean;
  uptime: number;
  addMessage: (text: string, type: Message['type']) => void;
  clearMessages: () => void;
  setLoading: (loading: boolean) => void;
  setResponseTime: (ms: number) => void;
  setStatus: (ollama: boolean, memory: boolean, uptime: number) => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  messages: [],
  sessionId: generateUUID(),
  messageCount: 0,
  isLoading: false,
  lastResponseTime: 0,
  ollamaOnline: false,
  memoryOnline: false,
  uptime: 0,

  addMessage: (text: string, type: Message['type']) =>
    set((state) => ({
      messages: [
        ...state.messages,
        { id: Math.random().toString(36), text, type },
      ],
      messageCount: type === 'user' ? state.messageCount + 1 : state.messageCount,
    })),

  clearMessages: () => set({ messages: [], messageCount: 0 }),

  setLoading: (loading: boolean) => set({ isLoading: loading }),

  setResponseTime: (ms: number) => set({ lastResponseTime: ms }),

  setStatus: (ollama: boolean, memory: boolean, uptime: number) =>
    set({ ollamaOnline: ollama, memoryOnline: memory, uptime }),
}));

// UUID generator
function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}
