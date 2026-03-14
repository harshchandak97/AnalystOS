import React from 'react';

function AnalystNote({ company, rank, total }) {
  const baseCagr = company.scenarios?.base?.cagr_pct || 0;
  const guidanceStrength = company.guidance_strength || 'Unknown';
  const confidence = company.confidence || 'Unknown';
  const conflictsCount = company.conflicts?.length || 0;
  const quotes = company.quotes || [];
  const keyEvidence = quotes.slice(0, 2).map(q => q.quote);

  return (
    <div className="max-w-4xl" data-testid="analyst-note">
      {/* Investment Summary */}
      <div className="bg-gradient-to-br from-slate-50 to-slate-100 border border-slate-200 rounded-xl p-8 mb-6">
        <h3 className="text-2xl font-bold text-slate-900 mb-4">{company.company_name}</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-lg p-4 border border-slate-200">
            <div className="text-xs text-slate-600 mb-1">Sector Rank</div>
            <div className="text-3xl font-bold text-slate-900">#{rank}</div>
            <div className="text-xs text-slate-500 mt-1">of {total} companies</div>
          </div>
          <div className="bg-white rounded-lg p-4 border border-slate-200">
            <div className="text-xs text-slate-600 mb-1">Base CAGR</div>
            <div className="text-3xl font-bold text-blue-600">{baseCagr.toFixed(1)}%</div>
            <div className="text-xs text-slate-500 mt-1">3-year expected</div>
          </div>
          <div className="bg-white rounded-lg p-4 border border-slate-200">
            <div className="text-xs text-slate-600 mb-1">Verdict</div>
            <div className={`text-2xl font-bold ${
              company.verdict === 'High Conviction' ? 'text-green-600' :
              company.verdict === 'Watchlist' ? 'text-amber-600' :
              company.verdict === 'Avoid' ? 'text-red-600' :
              'text-gray-600'
            }`}>{company.verdict}</div>
          </div>
        </div>
      </div>

      {/* Why This Rank */}
      <div className="mb-6">
        <h4 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3 flex items-center">
          <svg className="w-5 h-5 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          Why This Rank
        </h4>
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <p className="text-gray-700 leading-relaxed">
            <strong>{company.company_name}</strong> ranks <strong>#{rank} of {total}</strong> in the sector based on a base-case expected CAGR of <strong>{baseCagr.toFixed(1)}%</strong> and a <strong className={company.verdict === 'High Conviction' ? 'text-green-600' : company.verdict === 'Watchlist' ? 'text-amber-600' : 'text-red-600'}>{company.verdict}</strong> verdict. The analysis incorporates management guidance extracted from company documents, converted into bear/base/bull scenario assumptions, and valued using a historical median P/E multiple of <strong>{company.target_pe?.toFixed(1)}x</strong>.
          </p>
        </div>
      </div>

      {/* Key Upside Driver */}
      <div className="mb-6">
        <h4 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3 flex items-center">
          <svg className="w-5 h-5 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414 0L8 10.414l-4.293 4.293a1 1 0 01-1.414-1.414l5-5a1 1 0 011.414 0L11 10.586 14.586 7H12z" clipRule="evenodd" />
          </svg>
          Key Upside Driver
        </h4>
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          {keyEvidence.length > 0 ? (
            <div>
              <p className="text-gray-700 leading-relaxed mb-3">
                Management guidance supports the revenue and margin trajectory. Key evidence includes:
              </p>
              {keyEvidence.map((ev, idx) => (
                <blockquote key={idx} className="border-l-4 border-green-500 pl-4 py-2 mb-2 italic text-sm text-gray-600">
                  "{ev}"
                </blockquote>
              ))}
              <p className="text-xs text-green-700 mt-3">
                See <strong>Evidence</strong> tab for complete source traceability.
              </p>
            </div>
          ) : (
            <p className="text-gray-700 leading-relaxed">
              Management guidance supports revenue and margin trajectory. See Evidence tab for complete source details and traceability.
            </p>
          )}
        </div>
      </div>

      {/* Key Risk */}
      <div className="mb-6">
        <h4 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3 flex items-center">
          <svg className="w-5 h-5 text-red-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          Key Risk
        </h4>
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          {confidence === 'Low' || conflictsCount > 0 ? (
            <p className="text-gray-700 leading-relaxed">
              <strong>Limited explicit guidance</strong> or <strong>conflicting statements</strong> across documents. Treat scenario projections as indicative rather than precise forecasts. {conflictsCount > 0 && `${conflictsCount} conflict(s) detected in source documents.`} Additional diligence recommended before acting on this signal.
            </p>
          ) : (
            <p className="text-gray-700 leading-relaxed">
              Primary risks include <strong>execution uncertainty</strong> and <strong>macro dependence</strong>. Monitor next earnings call for guidance reiteration. Order book visibility, capacity utilization, and margin trajectory should be tracked closely.
            </p>
          )}
        </div>
      </div>

      {/* What to Monitor */}
      <div className="mb-6">
        <h4 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3 flex items-center">
          <svg className="w-5 h-5 text-purple-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
          </svg>
          What to Monitor
        </h4>
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
          <ul className="space-y-2 text-gray-700">
            <li className="flex items-start">
              <span className="text-purple-600 mr-2">•</span>
              <span><strong>Next earnings call:</strong> Updated revenue and margin guidance; commentary on demand environment</span>
            </li>
            <li className="flex items-start">
              <span className="text-purple-600 mr-2">•</span>
              <span><strong>Order book trends:</strong> Inflow rates and execution timelines (for operational names)</span>
            </li>
            <li className="flex items-start">
              <span className="text-purple-600 mr-2">•</span>
              <span><strong>Capacity utilization:</strong> Progress on expansion projects and facility ramp-up</span>
            </li>
            <li className="flex items-start">
              <span className="text-purple-600 mr-2">•</span>
              <span><strong>Margin trajectory:</strong> Cost pressures vs. pricing power; mix shifts</span>
            </li>
          </ul>
        </div>
      </div>

      {/* Final Verdict */}
      <div className="bg-gradient-to-br from-slate-800 to-slate-900 text-white rounded-xl p-8">
        <h4 className="text-sm font-semibold uppercase tracking-wide mb-4">Final Verdict</h4>
        <div className="text-lg leading-relaxed">
          <p className="mb-4">
            <strong className="text-2xl">{company.verdict}</strong>
          </p>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-slate-400">Guidance Strength:</span>
              <span className="ml-2 font-semibold">{guidanceStrength}</span>
            </div>
            <div>
              <span className="text-slate-400">Confidence:</span>
              <span className="ml-2 font-semibold">{confidence}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AnalystNote;
