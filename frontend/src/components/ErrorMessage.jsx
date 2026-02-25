import { AlertCircle, X } from "lucide-react";

export default function ErrorMessage({ message, onDismiss }) {
  if (!message) return null;

  return (
    <div className="flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 px-4 py-3">
      <AlertCircle className="mt-0.5 h-5 w-5 flex-shrink-0 text-red-500" />
      <p className="flex-1 text-sm text-red-700">{message}</p>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="flex-shrink-0 text-red-400 transition hover:text-red-600"
        >
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  );
}
