// src/components/notifications/BaseNotification.jsx

// Remove the unused import
// import { XMarkIcon } from "@heroicons/react/24/solid";

const baseHeight = 80;
const gap = 10;
const getTopPosition = (index) => index * baseHeight + ((index + 1) * gap);

export const BaseNotification = ({ Icon, title, message, index, textColor="text-gray-500" }) => {
  return (
    <div className="fixed right-2 z-100" style={{ top: getTopPosition(index) }}>
      <div className="bg-white border border-slate-300 w-max min-h-20 shadow-lg rounded-md gap-4 p-4 flex flex-row items-center justify-center">
        <div className={`w-6 h-full flex flex-col items-center justify-start ${textColor}`}>
          {Icon}
        </div>
        <div className="h-full flex flex-col items-start justify-end gap-1">
          <h1 className={`text-base font-semibold ${textColor} antialiased`}>
            {title}
          </h1>
          <p className="text-sm font-medium text-zinc-400 antialiased">
            {message}
          </p>
        </div>
      </div>
    </div>
  );
};
