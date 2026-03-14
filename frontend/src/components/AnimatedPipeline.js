import React from 'react';

function AnimatedPipeline({ steps, activityLog, currentStep }) {
  const getStatusIcon = (status) => {
    if (status === 'completed') {
      return (
        <svg className="w-6 h-6 text-green-500" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
        </svg>
      );
    } else if (status === 'running') {
      return (
        <svg className="w-6 h-6 text-blue-500 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      );
    }
    return (
      <svg className="w-6 h-6 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm0-2a6 6 0 100-12 6 6 0 000 12z" clipRule="evenodd" />
      </svg>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-blue-900 flex items-center justify-center p-6">
      <div className="max-w-5xl w-full">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">
            AnalystOS Running
          </h1>
          <p className="text-xl text-blue-200">
            Processing your selected companies...
          </p>
        </div>

        {/* Pipeline Steps */}
        <div className="bg-white rounded-2xl shadow-2xl p-8 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Analysis Pipeline</h2>
          
          <div className="space-y-4">
            {steps.map((step, idx) => {
              const isActive = idx === currentStep;
              
              return (
                <div
                  key={step.id}
                  className={`flex items-center p-4 rounded-xl transition-all duration-500 ${
                    step.status === 'completed' ? 'bg-green-50' :
                    step.status === 'running' ? 'bg-blue-50 shadow-lg transform scale-105' :
                    'bg-gray-50'
                  }`}
                  data-testid={`step-${step.id}`}
                >
                  <div className="flex-shrink-0 mr-4">
                    {getStatusIcon(step.status)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className={`font-semibold ${
                        step.status === 'completed' ? 'text-green-900' :
                        step.status === 'running' ? 'text-blue-900' :
                        'text-gray-500'
                      }`}>
                        {idx + 1}. {step.label}
                      </span>
                      {step.status === 'running' && (
                        <span className="text-sm text-blue-600 font-medium animate-pulse">
                          Processing...
                        </span>
                      )}
                      {step.status === 'completed' && (
                        <span className="text-sm text-green-600 font-medium">
                          Complete
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Progress Bar */}
          <div className="mt-8">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Overall Progress</span>
              <span className="text-sm font-bold text-gray-900">
                {Math.round(((currentStep + 1) / steps.length) * 100)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
              <div
                className="bg-blue-600 h-3 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Activity Log */}
        <div className="bg-slate-800 rounded-2xl shadow-2xl p-8 max-h-96 overflow-y-auto">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center">
            <svg className="w-5 h-5 mr-2 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            Activity Log
          </h2>
          
          <div className="space-y-2">
            {activityLog.length === 0 ? (
              <p className="text-gray-400 text-sm italic">Initializing...</p>
            ) : (
              activityLog.map((log, idx) => (
                <div
                  key={idx}
                  className="text-sm text-gray-300 font-mono bg-slate-700 px-3 py-2 rounded animate-fade-in"
                  style={{ animationDelay: `${idx * 50}ms` }}
                >
                  <span className="text-blue-400 mr-2">›</span>
                  {log}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default AnimatedPipeline;
