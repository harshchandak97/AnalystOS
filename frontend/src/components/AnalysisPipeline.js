import React from 'react';

function AnalysisPipeline({ stepStatuses, activityLog }) {
  const steps = [
    { id: 'fetch_documents', label: 'Fetch Documents' },
    { id: 'extract_text', label: 'Extract Text' },
    { id: 'extract_guidance', label: 'Extract Guidance' },
    { id: 'consolidate_evidence', label: 'Consolidate Evidence' },
    { id: 'build_assumptions', label: 'Build Assumptions' },
    { id: 'run_valuation', label: 'Run Valuation' },
    { id: 'rank_companies', label: 'Rank Companies' },
    { id: 'link_sources', label: 'Link Sources' },
  ];

  const getStatusIcon = (status) => {
    if (status === 'completed') {
      return (
        <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
        </svg>
      );
    } else if (status === 'running') {
      return (
        <svg className="w-5 h-5 text-blue-500 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      );
    } else if (status === 'failed') {
      return (
        <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
        </svg>
      );
    }
    return (
      <svg className="w-5 h-5 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm0-2a6 6 0 100-12 6 6 0 000 12z" clipRule="evenodd" />
      </svg>
    );
  };

  return (
    <div className="mb-8" data-testid="analysis-pipeline">
      <h2 className="text-xl font-bold text-gray-900 mb-4">Analysis Pipeline</h2>
      
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="grid grid-cols-1 lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-gray-200">
          {/* Step Tracker */}
          <div className="p-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-4 uppercase tracking-wide">Workflow Steps</h3>
            <div className="space-y-3">
              {steps.map(step => {
                const status = stepStatuses?.[step.id] || 'pending';
                return (
                  <div key={step.id} className="flex items-center space-x-3" data-testid={`step-${step.id}`}>
                    {getStatusIcon(status)}
                    <span className={`text-sm font-medium ${
                      status === 'completed' ? 'text-gray-900' :
                      status === 'running' ? 'text-blue-600' :
                      status === 'failed' ? 'text-red-600' :
                      'text-gray-400'
                    }`}>
                      {step.label}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Activity Log */}
          <div className="p-6 bg-gray-50">
            <h3 className="text-sm font-semibold text-gray-700 mb-4 uppercase tracking-wide">Activity Log</h3>
            <div className="space-y-2 max-h-64 overflow-y-auto" data-testid="activity-log">
              {activityLog && activityLog.length > 0 ? (
                activityLog.slice(-10).reverse().map((log, idx) => (
                  <div key={idx} className="text-xs text-gray-600 font-mono bg-white px-3 py-2 rounded border border-gray-200">
                    {log}
                  </div>
                ))
              ) : (
                <p className="text-sm text-gray-400 italic">No activity yet</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AnalysisPipeline;
