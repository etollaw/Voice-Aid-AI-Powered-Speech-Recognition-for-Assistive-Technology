import { useState, useEffect, useCallback } from "react";
import { Inbox } from "lucide-react";
import { Link } from "react-router-dom";
import SessionCard from "../components/SessionCard.jsx";
import SearchBar from "../components/SearchBar.jsx";
import ErrorMessage from "../components/ErrorMessage.jsx";
import api from "../api/client.js";

export default function History() {
  const [sessions, setSessions] = useState([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const PAGE_SIZE = 20;

  const fetchSessions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.listSessions({ search, page, pageSize: PAGE_SIZE });
      setSessions(data.sessions);
      setTotal(data.total);
    } catch (err) {
      setError(err.message || "Failed to load sessions. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }, [search, page]);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  // Debounce search
  useEffect(() => {
    setPage(1);
  }, [search]);

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Session History</h1>
          <p className="mt-1 text-sm text-gray-600">
            {total} session{total !== 1 ? "s" : ""} total
          </p>
        </div>
        <div className="w-full sm:w-72">
          <SearchBar value={search} onChange={setSearch} placeholder="Search sessions..." />
        </div>
      </div>

      {/* Error */}
      {error && <ErrorMessage message={error} onDismiss={() => setError(null)} />}

      {/* Loading */}
      {loading && (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card animate-pulse">
              <div className="flex items-center gap-4">
                <div className="h-10 w-10 rounded-lg bg-gray-200" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 w-3/4 rounded bg-gray-200" />
                  <div className="h-3 w-1/2 rounded bg-gray-200" />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty state */}
      {!loading && sessions.length === 0 && (
        <div className="card flex flex-col items-center py-16 text-center">
          <Inbox className="h-12 w-12 text-gray-300" />
          <h3 className="mt-4 font-semibold text-gray-900">
            {search ? "No matching sessions" : "No sessions yet"}
          </h3>
          <p className="mt-2 text-sm text-gray-500">
            {search
              ? "Try a different search term."
              : "Record or upload audio to create your first session."}
          </p>
          {!search && (
            <Link to="/app" className="btn-primary mt-6">
              Create First Session
            </Link>
          )}
        </div>
      )}

      {/* Session list */}
      {!loading && sessions.length > 0 && (
        <div className="space-y-3">
          {sessions.map((session) => (
            <SessionCard key={session.id} session={session} />
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-4">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="btn-secondary text-sm"
          >
            Previous
          </button>
          <span className="text-sm text-gray-600">
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="btn-secondary text-sm"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
