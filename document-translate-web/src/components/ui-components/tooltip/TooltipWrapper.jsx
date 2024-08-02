import React from 'react';
export const TooltipWrapper = ({ children }) => (
  <div className="absolute bottom-[100%] left-[50%] translate-x-[-50%] rounded text-white opacity-0 transition-opcaity duration-300 group-hover:opacity-100 text-nowrap">
    <div className="rounded bg-gray-900 p-2 text-xs text-center shadow-lg">
      {children}
    </div>
  </div>
);
