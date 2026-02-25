import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { ArrowLeft, Trash2, Clock, Globe, Hash, Loader2 } from "lucide-react";
import TranscriptView from "../components/TranscriptView.jsx";
import SummaryView from "../components/SummaryView.jsx";
import ErrorMessage from "../components/ErrorMessage.jsx";
import api from "../api/client.js";

function formatDate(dateStr) {
  if (!dateStr) return "";
  return new Date(dateStr).toLocaleString("en-US", {
    weekday: "short",
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

export default function SessionDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    async function fetch() {
      setLoading(true);
      try {
        const data = await api.getSession(id);
        setSession(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetch();
  }, [id]);

  const handleDelete = async () => {
    if (!window.confirm("Delete this session? This cannot be undone.")) return;
    setDeleting(true);
    try {
      await api.deleteSession(id);
      navigate("/history");
    } catch (err) {
      setError(err.message);
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-brand-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <Link to="/history" className="flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900">
          <ArrowLeft className="h-4 w-4" /> Back to History
        </Link>
        <ErrorMessage message={error} />
      </div>
    );
  }

  if (!session) return null;

  return (
    <div className="space-y-6">
      {/* Back + Actions */}
      <div className="flex items-center justify-between">
        <Link
          to="/history"
          className="flex items-center gap-1 text-sm text-gray-600 transition hover:text-gray-900"
        >
          <ArrowLeft className="h-4 w-4" /> Back to History
        </Link>
        <button
          onClick={handleDelete}
          disabled={deleting}
          className="btn-danger text-sm"
        >
          <Trash2 className="h-4 w-4" />
          {deleting ? "Deleting..." : "Delete"}
        </button>
      </div>

      {/* Title + Meta */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{session.title}</h1>
        <div className="mt-3 flex flex-wrap items-center gap-4 text-sm text-gray-500">
          <span className="flex items-center gap-1.5">
            <Clock className="h-4 w-4" />
            {formatDate(session.created_at)}
          </span>
          <span>{formatDuration(session.audio_duration)}</span>
          {session.language && (
            <span className="flex items-center gap-1.5">
              <Globe className="h-4 w-4" />
              {session.language.toUpperCase()}
            </span>
          )}
          {session.word_count != null && (
            <span className="flex items-center gap-1.5">
              <Hash className="h-4 w-4" />
              {session.word_count} words
            </span>
          )}
          <span
            className={
              session.status === "completed"
                ? "badge-green"
                : session.status === "error"
                  ? "badge-red"
                  : "badge-yellow"
            }
          >
            {session.status}
          </span>
        </div>
      </div>

      {/* Error message */}
      {session.error_message && <ErrorMessage message={session.error_message} />}

      {/* Summary section first (most useful) */}
      <SummaryView
        summary={session.summary}
        keyPoints={session.key_points}
        actionItems={session.action_items}
      />

      {/* Transcript */}
      <TranscriptView
        transcript={session.transcript}
        wordCount={session.word_count}
        language={session.language}
      />
    </div>
  );
}
