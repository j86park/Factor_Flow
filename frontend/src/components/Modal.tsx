import React, { useEffect, useRef } from 'react';
import { X } from 'lucide-react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}

export function Modal({ isOpen, onClose, title, subtitle, children }: ModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  // Handle click outside modal content
  const handleBackdropClick = (e: React.MouseEvent) => {
    if (modalRef.current && !modalRef.current.contains(e.target as Node)) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div 
      className="z-50 bg-black/70 backdrop-blur-sm overflow-y-auto"
      style={{ 
        position: 'fixed',
        top: '56px',
        left: '0',
        right: '0',
        bottom: '0',
        display: 'grid',
        placeItems: 'start center',
        padding: '16px 0 32px 0'
      }}
      onClick={handleBackdropClick}
    >
      <div 
        ref={modalRef}
        className="bg-[#0d1321] border border-gray-800/50 rounded-2xl shadow-2xl flex flex-col overflow-hidden"
        style={{ width: '1280px', maxWidth: '85vw', height: 'calc(100vh - 120px)', maxHeight: '85vh' }}
        role="dialog"
        aria-modal="true"
      >
        {/* Header - Fixed */}
        <div className="flex items-start justify-between px-8 pt-6 pb-4 border-b border-gray-800/30 shrink-0">
          <div className="flex items-center gap-3">
            <div>
              <h2 className="text-2xl font-bold text-white">{title}</h2>
              {subtitle && <p className="text-gray-400 text-sm mt-1">{subtitle}</p>}
            </div>
          </div>
          <button 
            onClick={onClose}
            style={{ backgroundColor: '#ef4444', color: '#ffffff' }}
            className="hover:opacity-80 transition-all p-2 rounded-full"
            aria-label="Close"
          >
            <X className="w-6 h-6" strokeWidth={2.5} />
          </button>
        </div>
        {/* Content - Scrollable */}
        <div className="px-8 py-6 overflow-y-scroll flex-1 custom-scrollbar" style={{ scrollbarWidth: 'thin', scrollbarColor: '#4b5563 #1a2332' }}>
          {children}
        </div>
      </div>
    </div>
  );
}

