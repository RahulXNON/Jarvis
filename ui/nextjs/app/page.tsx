// Main page with 3-panel layout
'use client';

import ChatPanel from '@/components/ChatPanel';
import InputArea from '@/components/InputArea';
import MemoryPanel from '@/components/MemoryPanel';
import StatusPanel from '@/components/StatusPanel';
import { useState } from 'react';

export default function Home() {
  const [showSidebars, setShowSidebars] = useState(true);

  return (
    <div className="h-screen flex flex-col md:flex-row bg-dark">
      {/* Left Sidebar - Memory */}
      {showSidebars && (
        <div className="hidden lg:block w-80 border-r border-border">
          <MemoryPanel />
        </div>
      )}

      {/* Center - Chat */}
      <div className="flex-1 flex flex-col">
        <ChatPanel />
        <InputArea />
      </div>

      {/* Right Sidebar - Status */}
      {showSidebars && (
        <div className="hidden lg:block w-80 border-l border-border">
          <StatusPanel />
        </div>
      )}

      {/* Mobile Toggle Button */}
      <button
        onClick={() => setShowSidebars(!showSidebars)}
        className="lg:hidden fixed bottom-4 right-4 px-3 py-2 bg-primary text-dark rounded font-bold text-sm"
      >
        {showSidebars ? 'Hide' : 'Show'} Panels
      </button>
    </div>
  );
}
