import { Link } from "react-router-dom";
import { Clock, FileText, ChevronRight } from "lucide-react";

function formatDate(dateStr) {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatDuration(seconds) {
  if (!seconds) return "—";
  if (seconds < 60) return `${Math.round(seconds)}s`;
  const m = Math.floor(seconds / 60);
  const s = Math.round(seconds % 60);
  return `${m}m ${s}s`;
}

const STATUS_BADGE = {
  completed: "badge-green",
  transcribing: "badge-yellow",
  summarizing: "badge-yellow",
  uploading: "badge-blue",
  error: "badge-red",
};

export default function SessionCard({ session }) {
  return (
    <Link
      to={`/history/${session.id}`}
      className="card group flex items-center gap-4 transition hover:border-brand-300 hover:shadow-md"
    >
      {/* Icon */}
      <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-brand-50 text-brand-600">
        <FileText className="h-5 w-5" />
      </div>

      {/* Content */}
      <div className="min-w-0 flex-1">
        <h3 className="truncate font-medium text-gray-900 group-hover:text-brand-700">
          {session.title}
        </h3>
        <div className="mt-1 flex flex-wrap items-center gap-3 text-xs text-gray-500">
          <span className="flex items-center gap-1">
            <Clock className="h-3 w-3" />
            {formatDate(session.created_at)}
          </span>
          <span>{formatDuration(session.audio_duration)}</span>
          {session.word_count != null && <span>{session.word_count} words</span>}
          {session.language && (
            <span className="uppercase">{session.language}</span>
          )}
        </div>
      </div>

      {/* Status + Arrow */}
      <div className="flex items-center gap-3">
        <span className={STATUS_BADGE[session.status] || "badge-blue"}>
          {session.status}
        </span>
        <ChevronRight className="h-4 w-4 text-gray-400 transition group-hover:text-brand-600" />
      </div>
    </Link>
  );
}
