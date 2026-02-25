import { useRef, useState, useCallback } from "react";
import { Upload, FileAudio } from "lucide-react";

const ACCEPTED = ".mp3,.wav,.ogg,.webm,.m4a,.flac,.mp4,.wma";
const MAX_SIZE_MB = 100;

export default function FileUploader({ onFileSelected, disabled }) {
  const inputRef = useRef(null);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState(null);

  const validateAndSelect = useCallback(
    (file) => {
      setError(null);
      if (!file) return;

      const sizeMB = file.size / (1024 * 1024);
      if (sizeMB > MAX_SIZE_MB) {
        setError(`File too large (${sizeMB.toFixed(1)}MB). Max: ${MAX_SIZE_MB}MB.`);
        return;
      }

      const ext = "." + file.name.split(".").pop().toLowerCase();
      const allowed = ACCEPTED.split(",");
      if (!allowed.includes(ext)) {
        setError(`Unsupported format (${ext}). Supported: mp3, wav, ogg, webm, m4a, flac, mp4`);
        return;
      }

      onFileSelected(file);
    },
    [onFileSelected],
  );

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]) {
      validateAndSelect(e.dataTransfer.files[0]);
    }
  };

  const handleClick = () => {
    if (!disabled) inputRef.current?.click();
  };

  const handleChange = (e) => {
    if (e.target.files?.[0]) {
      validateAndSelect(e.target.files[0]);
    }
  };

  return (
    <div>
      <div
        onClick={handleClick}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`group cursor-pointer rounded-xl border-2 border-dashed p-8 text-center transition ${
          disabled
            ? "cursor-not-allowed border-gray-200 bg-gray-50"
            : dragActive
              ? "border-brand-400 bg-brand-50"
              : "border-gray-300 bg-white hover:border-brand-400 hover:bg-brand-50/50"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED}
          onChange={handleChange}
          className="hidden"
          disabled={disabled}
        />

        <div className="flex flex-col items-center gap-3">
          <div
            className={`flex h-12 w-12 items-center justify-center rounded-full transition ${
              dragActive ? "bg-brand-100" : "bg-gray-100 group-hover:bg-brand-100"
            }`}
          >
            {dragActive ? (
              <FileAudio className="h-6 w-6 text-brand-600" />
            ) : (
              <Upload className="h-6 w-6 text-gray-400 group-hover:text-brand-600" />
            )}
          </div>

          <div>
            <p className="text-sm font-medium text-gray-700">
              {dragActive ? "Drop your audio file here" : "Upload an audio file"}
            </p>
            <p className="mt-1 text-xs text-gray-500">
              MP3, WAV, OGG, WebM, M4A, FLAC — up to {MAX_SIZE_MB}MB
            </p>
          </div>
        </div>
      </div>

      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
    </div>
  );
}
