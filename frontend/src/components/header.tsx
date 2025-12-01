import React from 'react';

export function Header() {
  return (
    // H-16 (height), fixed top, full width, semi-transparent backdrop
    <header className="w-full h-20 bg-dark-bg border-b border-gray-800 flex items-center justify-center sticky top-0 z-50">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-white tracking-wider uppercase">
          Factor Flow
        </h1>
        {/* Optional subtitle if you want it later, remove if not */}
        {/* <p className="text-xs text-gray-400 mt-1">Thematic Factor Tracking</p> */}
      </div>
    </header>
  );
}
