import { Sparkles, ListChecks, Target } from "lucide-react";

export default function SummaryView({ summary, keyPoints, actionItems }) {
  const hasContent = summary || keyPoints?.length > 0 || actionItems?.length > 0;
  if (!hasContent) return null;

  return (
    <div className="space-y-4">
      {/* Summary */}
      {summary && (
        <div className="card">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-amber-500" />
            <h3 className="font-semibold text-gray-900">Summary</h3>
          </div>
          <p className="mt-3 text-sm leading-relaxed text-gray-700">{summary}</p>
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2">
        {/* Key Points */}
        {keyPoints?.length > 0 && (
          <div className="card">
            <div className="flex items-center gap-2">
              <Target className="h-5 w-5 text-blue-500" />
              <h3 className="font-semibold text-gray-900">Key Points</h3>
            </div>
            <ul className="mt-3 space-y-2">
              {keyPoints.map((point, i) => (
                <li key={i} className="flex gap-2 text-sm text-gray-700">
                  <span className="mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-blue-400" />
                  {point}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Action Items */}
        {actionItems?.length > 0 && (
          <div className="card">
            <div className="flex items-center gap-2">
              <ListChecks className="h-5 w-5 text-green-500" />
              <h3 className="font-semibold text-gray-900">Action Items</h3>
            </div>
            <ul className="mt-3 space-y-2">
              {actionItems.map((item, i) => (
                <li key={i} className="flex gap-2 text-sm text-gray-700">
                  <span className="mt-1 flex-shrink-0">
                    <input
                      type="checkbox"
                      className="h-4 w-4 rounded border-gray-300 text-brand-600 focus:ring-brand-500"
                    />
                  </span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
