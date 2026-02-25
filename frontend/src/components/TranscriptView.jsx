import { FileText, Copy, Check } from "lucide-react";
import { useState } from "react";

export default function TranscriptView({ transcript, wordCount, language }) {
  const [copied, setCopied] = useState(false);

  if (!transcript) return null;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(transcript);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback
      const ta = document.createElement("textarea");
      ta.value = transcript;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FileText className="h-5 w-5 text-brand-600" />
          <h3 className="font-semibold text-gray-900">Transcript</h3>
        </div>
        <div className="flex items-center gap-3">
          {wordCount != null && (
            <span className="text-xs text-gray-500">{wordCount} words</span>
          )}
          {language && <span className="badge-blue">{language.toUpperCase()}</span>}
          <button
            onClick={handleCopy}
            className="flex items-center gap-1 rounded-md px-2 py-1 text-xs text-gray-500 transition hover:bg-gray-100 hover:text-gray-700"
          >
            {copied ? (
              <>
                <Check className="h-3.5 w-3.5 text-green-500" /> Copied
              </>
            ) : (
              <>
                <Copy className="h-3.5 w-3.5" /> Copy
              </>
            )}
          </button>
        </div>
      </div>
      <p className="mt-4 whitespace-pre-wrap text-sm leading-relaxed text-gray-700">
        {transcript}
      </p>
    </div>
  );
}
