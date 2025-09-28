
import React, { useState, useRef } from 'react';
import { ICONS } from '../../constants';

interface FileInputProps {
  onFileRead: (text: string, fileName: string) => void;
  id: string;
  label: string;
}

const FileInput: React.FC<FileInputProps> = ({ onFileRead, id, label }) => {
  const [fileName, setFileName] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setFileName(file.name);
      // NOTE: This implementation reads .txt files. For PDF support, a library like
      // 'pdf-parse' (server-side) or 'pdfjs-dist' (client-side) would be required
      // to extract text content.
      const reader = new FileReader();
      reader.onload = (e) => {
        const text = e.target?.result as string;
        onFileRead(text, file.name);
      };
      reader.onerror = () => {
        console.error("Error reading file");
        setFileName("Error reading file.");
      };
      reader.readAsText(file);
    }
  };

  const handleClearFile = () => {
    setFileName(null);
    onFileRead('', '');
    if (fileInputRef.current) {
        fileInputRef.current.value = '';
    }
  };

  return (
    <div className="w-full">
      <input
        type="file"
        id={id}
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden"
        accept=".txt, .md" // Accepting text-based files.
      />
      <label
        htmlFor={id}
        className="w-full flex items-center justify-center px-4 py-6 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer bg-white hover:bg-gray-50 transition-colors"
      >
        {fileName ? (
          <div className="text-center">
             <div className="flex items-center justify-center text-green-600">
                {ICONS.CHECK}
                <span className="ml-2 font-semibold text-gray-700">{fileName}</span>
             </div>
             <button onClick={(e) => { e.preventDefault(); handleClearFile(); }} className="mt-2 text-sm text-indigo-600 hover:underline">
                Choose a different file
            </button>
          </div>
        ) : (
          <div className="text-center">
            <div className="flex justify-center">{ICONS.UPLOAD}</div>
            <p className="mt-2 text-sm text-gray-600">
              <span className="font-semibold text-indigo-600">Click to upload</span> or drag and drop
            </p>
            <p className="text-xs text-gray-500">{label} (TXT, MD)</p>
          </div>
        )}
      </label>
    </div>
  );
};

export default FileInput;
