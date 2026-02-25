import { Mic, Square } from "lucide-react";

function formatDuration(seconds) {
  const m = Math.floor(seconds / 60)
    .toString()
    .padStart(2, "0");
  const s = (seconds % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

export default function AudioRecorder({
  isRecording,
  duration,
  onStart,
  onStop,
  disabled,
}) {
  return (
    <div className="flex flex-col items-center gap-4">
      {/* Big record button */}
      <button
        onClick={isRecording ? onStop : onStart}
        disabled={disabled}
        className={`group relative flex h-24 w-24 items-center justify-center rounded-full transition-all focus:outline-none focus:ring-4 disabled:opacity-50 ${
          isRecording
            ? "bg-red-500 text-white shadow-lg shadow-red-200 hover:bg-red-600 focus:ring-red-300"
            : "bg-brand-600 text-white shadow-lg shadow-brand-200 hover:bg-brand-700 focus:ring-brand-300"
        }`}
        aria-label={isRecording ? "Stop recording" : "Start recording"}
      >
        {isRecording ? (
          <>
            <div className="recording-indicator absolute inset-0 rounded-full bg-red-400 opacity-40" />
            <Square className="relative h-8 w-8" />
          </>
        ) : (
          <Mic className="h-8 w-8 transition group-hover:scale-110" />
        )}
      </button>

      {/* Status text */}
      <div className="text-center">
        {isRecording ? (
          <div className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-red-500 recording-indicator" />
            <span className="text-lg font-semibold tabular-nums text-red-600">
              {formatDuration(duration)}
            </span>
          </div>
        ) : (
          <p className="text-sm text-gray-500">Click to start recording</p>
        )}
      </div>
    </div>
  );
}
