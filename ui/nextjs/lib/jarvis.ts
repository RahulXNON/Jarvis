// API service with typed responses and error handling
const API_BASE = 'http://127.0.0.1:8888';

export interface HealthResponse {
  ollama: boolean;
  memory: boolean;
  uptime_seconds: number;
}

export interface ChatRequest {
  message: string;
  session_id: string;
}

export interface TaskItem {
  session_id: string;
  message: string;
  response_preview: string;
  response_time_ms: number;
  timestamp: string;
}

export interface TasksResponse {
  tasks: TaskItem[];
}

export interface MemoryResult {
  text: string;
  relevance_score: number;
}

export interface MemorySearchResponse {
  results: MemoryResult[];
}

// Health check
export async function getHealth(): Promise<HealthResponse | null> {
  try {
    const response = await fetch(`${API_BASE}/health`, { cache: 'no-store' });
    if (!response.ok) return null;
    return await response.json();
  } catch (e) {
    console.error('Health check error:', e);
    return null;
  }
}

// Send chat message with streaming
export async function sendChat(request: ChatRequest): Promise<ReadableStreamDefaultReader<Uint8Array> | null> {
  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    if (!response.ok) return null;
    return response.body?.getReader() ?? null;
  } catch (e) {
    console.error('Chat error:', e);
    return null;
  }
}

// Get recent tasks
export async function getTasks(limit: number = 20): Promise<TasksResponse | null> {
  try {
    const response = await fetch(`${API_BASE}/tasks?limit=${limit}`, { cache: 'no-store' });
    if (!response.ok) return null;
    return await response.json();
  } catch (e) {
    console.error('Get tasks error:', e);
    return null;
  }
}

// Search memory
export async function searchMemory(query: string, limit: number = 3): Promise<MemorySearchResponse | null> {
  try {
    const response = await fetch(
      `${API_BASE}/memory/search?q=${encodeURIComponent(query)}&limit=${limit}`,
      { cache: 'no-store' }
    );
    if (!response.ok) return null;
    return await response.json();
  } catch (e) {
    console.error('Search memory error:', e);
    return null;
  }
}
