// Memory search panel
'use client';

import { useState, useEffect } from 'react';
import { searchMemory, getTasks } from '@/lib/jarvis';

interface MemoryResult {
  text: string;
  relevance_score: number;
}

export default function MemoryPanel() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<MemoryResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTimeout, setSearchTimeout] = useState<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (searchTimeout) clearTimeout(searchTimeout);

    if (!query.trim()) {
      setResults([]);
      return;
    }

    const timeout = setTimeout(async () => {
      setLoading(true);
      const data = await searchMemory(query, 3);
      if (data) setResults(data.results);
      setLoading(false);
    }, 500);

    setSearchTimeout(timeout);
  }, [query]);

  return (
    <div className="flex flex-col h-full bg-dark border-r border-border p-4">
      <h2 className="text-primary font-bold text-sm uppercase mb-4">Memory</h2>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search conversations..."
        className="w-full px-3 py-2 bg-card border border-border text-white rounded mb-4 text-sm focus:outline-none focus:border-primary"
      />
      <div className="flex-1 overflow-y-auto space-y-2">
        {loading && <p className="text-xs text-gray-500">Searching...</p>}
        {results.map((result, i) => (
          <div key={i} className="bg-card p-2 rounded border-l-2 border-primary text-xs">
            <p className="line-clamp-2 text-gray-300 mb-1">{result.text.substring(0, 100)}...</p>
            <p className="text-primary text-xs">
              Relevance: {(result.relevance_score * 100).toFixed(0)}%
            </p>
          </div>
        ))}
        {!loading && results.length === 0 && query && (
          <p className="text-xs text-gray-600">No results found</p>
        )}
      </div>
    </div>
  );
}
