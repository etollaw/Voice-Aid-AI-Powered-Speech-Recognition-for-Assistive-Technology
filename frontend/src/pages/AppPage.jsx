import { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Loader2 } from "lucide-react";
import AudioRecorder from "../components/AudioRecorder.jsx";
import FileUploader from "../components/FileUploader.jsx";
import TranscriptView from "../components/TranscriptView.jsx";
import SummaryView from "../components/SummaryView.jsx";
import ErrorMessage from "../components/ErrorMessage.jsx";
import useRecorder from "../hooks/useRecorder.js";
import api from "../api/client.js";

export default function AppPage() {
  const navigate = useNavigate();
  const recorder = useRecorder();

  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [session, setSession] = useState(null);

  const processFile = useCallback(
    async (file) => {
      setError(null);
      setSession(null);
      setProcessing(true);

      try {
        const result = await api.createSession(file);
        setSession(result);

        if (result.status === "error") {
          setError(result.error_message || "Processing failed. Please try again.");
        }
      } catch (err) {
        setError(err.message || "Something went wrong. Is the backend running?");
      } finally {
        setProcessing(false);
      }
    },
    [],
  );

  // When recording stops and we have a blob, process it
  const handleRecordingStop = useCallback(() => {
    recorder.stopRecording();
  }, [recorder]);

  // Watch for audioBlob changes
  const handleRecordStart = useCallback(() => {
    setSession(null);
    setError(null);
    recorder.startRecording();
  }, [recorder]);

  // Process the recorded blob
  const handleProcessRecording = useCallback(() => {
    if (recorder.audioBlob) {
      const file = new File([recorder.audioBlob], "recording.webm", {
        type: recorder.audioBlob.type || "audio/webm",
      });
      processFile(file);
      recorder.resetRecording();
    }
  }, [recorder, processFile]);

  // Handle file upload
  const handleFileSelected = useCallback(
    (file) => {
      recorder.resetRecording();
      processFile(file);
    },
    [recorder, processFile],
  );

  return (
    <div className="space-y-8">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">New Session</h1>
        <p className="mt-1 text-sm text-gray-600">
          Record audio or upload a file to get started.
        </p>
      </div>

      {/* Error */}
      {(error || recorder.error) && (
        <ErrorMessage
          message={error || recorder.error}
          onDismiss={() => {
            setError(null);
          }}
        />
      )}

      {/* Input section */}
      <div className="grid gap-8 lg:grid-cols-2">
        {/* Recorder */}
        <div className="card flex flex-col items-center justify-center py-10">
          <h2 className="mb-6 text-sm font-medium uppercase tracking-wider text-gray-500">
            Record Audio
          </h2>
          <AudioRecorder
            isRecording={recorder.isRecording}
            duration={recorder.duration}
            onStart={handleRecordStart}
            onStop={handleRecordingStop}
            disabled={processing}
          />
          {recorder.audioBlob && !processing && (
            <button onClick={handleProcessRecording} className="btn-primary mt-6">
              Process Recording
            </button>
          )}
        </div>

        {/* Upload */}
        <div className="card flex flex-col justify-center">
          <h2 className="mb-6 text-sm font-medium uppercase tracking-wider text-gray-500">
            Upload Audio File
          </h2>
          <FileUploader
            onFileSelected={handleFileSelected}
            disabled={processing || recorder.isRecording}
          />
        </div>
      </div>

      {/* Processing indicator */}
      {processing && (
        <div className="card flex items-center justify-center gap-3 py-12">
          <Loader2 className="h-6 w-6 animate-spin text-brand-600" />
          <p className="text-sm font-medium text-gray-700">
            Processing your audio... This may take a moment.
          </p>
        </div>
      )}

      {/* Results */}
      {session && session.status === "completed" && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-gray-900">Results</h2>
            <button
              onClick={() => navigate(`/history/${session.id}`)}
              className="btn-secondary text-sm"
            >
              View Full Detail
            </button>
          </div>

          <TranscriptView
            transcript={session.transcript}
            wordCount={session.word_count}
            language={session.language}
          />

          <SummaryView
            summary={session.summary}
            keyPoints={session.key_points}
            actionItems={session.action_items}
          />
        </div>
      )}
    </div>
  );
}
