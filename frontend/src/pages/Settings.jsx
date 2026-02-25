import { useState, useEffect } from "react";
import { Server, CheckCircle, XCircle, Loader2 } from "lucide-react";
import api from "../api/client.js";

export default function Settings() {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function check() {
      try {
        const data = await api.health();
        setHealth(data);
      } catch {
        setHealth(null);
      } finally {
        setLoading(false);
      }
    }
    check();
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="mt-1 text-sm text-gray-600">System configuration and status.</p>
      </div>

      {/* Backend Status */}
      <div className="card">
        <div className="flex items-center gap-2">
          <Server className="h-5 w-5 text-gray-600" />
          <h2 className="font-semibold text-gray-900">Backend Status</h2>
        </div>

        {loading ? (
          <div className="mt-4 flex items-center gap-2 text-sm text-gray-500">
            <Loader2 className="h-4 w-4 animate-spin" />
            Checking connection...
          </div>
        ) : health ? (
          <div className="mt-4 space-y-3">
            <div className="flex items-center gap-2 text-sm text-green-700">
              <CheckCircle className="h-4 w-4" />
              Backend is connected and running
            </div>
            <dl className="grid grid-cols-2 gap-3 rounded-lg bg-gray-50 p-4 text-sm">
              <div>
                <dt className="text-gray-500">Version</dt>
                <dd className="font-medium text-gray-900">{health.version}</dd>
              </div>
              <div>
                <dt className="text-gray-500">Whisper Model</dt>
                <dd className="font-medium text-gray-900">{health.whisper_model}</dd>
              </div>
              <div>
                <dt className="text-gray-500">Mock Mode</dt>
                <dd className="font-medium text-gray-900">
                  {health.mock_mode ? "ON (no real transcription)" : "OFF (real transcription)"}
                </dd>
              </div>
              <div>
                <dt className="text-gray-500">Status</dt>
                <dd className="font-medium text-gray-900">{health.status}</dd>
              </div>
            </dl>
          </div>
        ) : (
          <div className="mt-4 space-y-3">
            <div className="flex items-center gap-2 text-sm text-red-700">
              <XCircle className="h-4 w-4" />
              Cannot reach backend
            </div>
            <p className="text-sm text-gray-600">
              Make sure the backend is running on{" "}
              <code className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-xs">
                http://localhost:8000
              </code>
              . Run:{" "}
              <code className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-xs">
                cd backend && uvicorn app.main:app --reload
              </code>
            </p>
          </div>
        )}
      </div>

      {/* About */}
      <div className="card">
        <h2 className="font-semibold text-gray-900">About VoiceAid</h2>
        <p className="mt-3 text-sm leading-relaxed text-gray-600">
          VoiceAid is an AI-powered speech recognition platform designed for accessibility.
          It helps users with speech impairments or physical disabilities communicate
          effectively by converting voice to structured notes.
        </p>
        <div className="mt-4 space-y-2 text-sm text-gray-600">
          <p>
            <strong>Transcription:</strong> OpenAI Whisper (open-source, runs locally)
          </p>
          <p>
            <strong>Summarization:</strong> Extractive (rule-based, no API keys needed)
          </p>
          <p>
            <strong>Storage:</strong> SQLite (local, no external database)
          </p>
        </div>
      </div>

      {/* Quick Help */}
      <div className="card">
        <h2 className="font-semibold text-gray-900">Quick Start</h2>
        <ol className="mt-3 list-inside list-decimal space-y-2 text-sm text-gray-600">
          <li>Start the backend: <code className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-xs">cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload</code></li>
          <li>Start the frontend: <code className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-xs">cd frontend && npm install && npm run dev</code></li>
          <li>Open <code className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-xs">http://localhost:5173</code> and start recording!</li>
          <li>For testing without Whisper, set <code className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-xs">MOCK_MODE=true</code> in the backend.</li>
        </ol>
      </div>
    </div>
  );
}
