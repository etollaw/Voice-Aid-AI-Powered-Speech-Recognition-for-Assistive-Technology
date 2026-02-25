import { Link } from "react-router-dom";
import { Mic, FileText, Sparkles, ListChecks, Clock, ArrowRight } from "lucide-react";

const FEATURES = [
  {
    icon: Mic,
    title: "Record or Upload",
    description: "Record audio directly from your microphone or upload existing audio files.",
    color: "text-brand-600",
    bg: "bg-brand-50",
  },
  {
    icon: FileText,
    title: "Instant Transcription",
    description: "AI-powered speech recognition converts your audio to accurate text.",
    color: "text-blue-600",
    bg: "bg-blue-50",
  },
  {
    icon: Sparkles,
    title: "Smart Summaries",
    description: "Get concise summaries with key points extracted automatically.",
    color: "text-amber-600",
    bg: "bg-amber-50",
  },
  {
    icon: ListChecks,
    title: "Action Items",
    description: "Action items and to-dos are identified and listed for easy follow-up.",
    color: "text-green-600",
    bg: "bg-green-50",
  },
  {
    icon: Clock,
    title: "Session History",
    description: "All your sessions are saved and searchable — find anything instantly.",
    color: "text-purple-600",
    bg: "bg-purple-50",
  },
];

export default function Landing() {
  return (
    <div className="min-h-screen">
      {/* Header */}
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-2.5 text-xl font-bold text-brand-600">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600">
            <Mic className="h-4 w-4 text-white" />
          </div>
          VoiceAid
        </div>
        <Link to="/app" className="btn-primary">
          Get Started
          <ArrowRight className="h-4 w-4" />
        </Link>
      </nav>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-brand-50 via-white to-blue-50" />
        <div className="relative mx-auto max-w-4xl px-4 py-24 text-center sm:px-6 sm:py-32 lg:px-8">
          <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl lg:text-6xl">
            Your voice,{" "}
            <span className="bg-gradient-to-r from-brand-600 to-blue-600 bg-clip-text text-transparent">
              understood
            </span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-gray-600">
            VoiceAid transforms your audio into structured notes with AI-powered transcription,
            smart summaries, and automatic action item detection. Designed for accessibility.
          </p>
          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link to="/app" className="btn-primary px-8 py-3 text-base">
              <Mic className="h-5 w-5" />
              Start Recording
            </Link>
            <Link to="/history" className="btn-secondary px-8 py-3 text-base">
              View History
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-6xl px-4 py-20 sm:px-6 lg:px-8">
        <h2 className="text-center text-2xl font-bold text-gray-900">
          Everything you need from voice to action
        </h2>
        <p className="mx-auto mt-3 max-w-xl text-center text-gray-600">
          Record, transcribe, summarize, and organize — all in one place.
        </p>

        <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map(({ icon: Icon, title, description, color, bg }) => (
            <div
              key={title}
              className="card group transition hover:shadow-md hover:border-brand-200"
            >
              <div className={`mb-4 inline-flex rounded-lg p-2.5 ${bg}`}>
                <Icon className={`h-5 w-5 ${color}`} />
              </div>
              <h3 className="font-semibold text-gray-900">{title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-gray-600">{description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white">
        <div className="mx-auto max-w-6xl px-4 py-8 text-center text-sm text-gray-500 sm:px-6 lg:px-8">
          VoiceAid — AI-Powered Speech Recognition for Assistive Technology. Open source.
        </div>
      </footer>
    </div>
  );
}
