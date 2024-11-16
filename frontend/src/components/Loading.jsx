import React from "react";

const Loading = ({ fullScreen = true }) => {
  const containerClasses = fullScreen
    ? "fixed inset-0 flex items-center justify-center bg-gray-900 bg-opacity-50 z-50"
    : "flex items-center justify-center p-4";

  return (
    <div className={containerClasses}>
      <div className="relative flex flex-col items-center">
        <div className="w-12 h-12 rounded-full border-4 border-gray-300 border-t-blue-500 animate-spin" />

        <div className="mt-4 text-white animate-pulse">Loading...</div>
      </div>
    </div>
  );
};

export default Loading;
