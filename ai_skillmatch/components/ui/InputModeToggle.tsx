
import React from 'react';

export type InputMode = 'text' | 'file';

interface InputModeToggleProps {
  mode: InputMode;
  onModeChange: (mode: InputMode) => void;
}

const InputModeToggle: React.FC<InputModeToggleProps> = ({ mode, onModeChange }) => {
  const baseClasses = "px-4 py-2 text-sm font-medium transition-colors duration-200 focus:outline-none";
  const activeClasses = "bg-indigo-600 text-white shadow-sm";
  const inactiveClasses = "bg-white text-gray-700 hover:bg-gray-100";

  return (
    <div className="flex rounded-md border border-gray-300">
      <button
        onClick={() => onModeChange('text')}
        className={`${baseClasses} rounded-l-md ${mode === 'text' ? activeClasses : inactiveClasses}`}
      >
        Paste Text
      </button>
      <button
        onClick={() => onModeChange('file')}
        className={`${baseClasses} rounded-r-md border-l border-gray-300 ${mode === 'file' ? activeClasses : inactiveClasses}`}
      >
        Upload File
      </button>
    </div>
  );
};

export default InputModeToggle;
