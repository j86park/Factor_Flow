import { Layers } from 'lucide-react';

export function Header() {
  return (
    <header className="w-full bg-black/40 backdrop-blur-md sticky top-0 z-50 py-2">
      <div className="max-w-[1800px] mx-auto px-4 flex items-center justify-center">
        {/* Logo - Top Left */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-b from-cyan-400 to-blue-600 rounded-lg flex items-center justify-center">
            <Layers className="w-4 h-4 text-white" />
          </div>
          <h1 className="text-lg font-medium text-white/90 tracking-tight">
            Factor Flow
          </h1>
        </div>
      </div>
    </header>
  );
}
