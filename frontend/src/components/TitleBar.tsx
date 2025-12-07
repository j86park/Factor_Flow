import { Layers } from 'lucide-react';

export function Header() {
  return (
    <header className="w-full bg-[#1a2332] sticky top-0 z-50 py-2">
      <div className="max-w-[1800px] mx-auto px-4 flex items-center justify-center">
        {/* Logo - Top Left */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-b from-cyan-400 to-blue-600 rounded-lg flex items-center justify-center">
            <Layers className="w-5 h-5 text-white" />
          </div>
          <h1 className="text-2xl font-large text-white/90 tracking-tight">
            Factor Flow
          </h1>
        </div>
      </div>
    </header>
  );
}
