import React, { useState } from 'react';

function Evidence({ company }) {
  const [expandedQuote, setExpandedQuote] = useState(null);
  const quotes = company.quotes || [];
  const conflicts = company.conflicts || [];

  const getCategoryBadge = (category) => {
    const variants = {
      'direct_financial': 'bg-blue-100 text-blue-800 border-blue-200',
      'operational_modeling': 'bg-purple-100 text-purple-800 border-purple-200',
      'directional_context': 'bg-gray-100 text-gray-700 border-gray-200',
    };
    return variants[category] || variants['directional_context'];
  };

  const getTypeBadge = (type) => {
    return type === 'explicit' ? 'bg-green-100 text-green-800' : 'bg-amber-100 text-amber-700';
  };

  const getConfidenceBadge = (confidence) => {
    const variants = {
      'high': 'text-green-600',
      'medium': 'text-amber-600',
      'low': 'text-gray-500',
    };
    return variants[confidence] || variants['low'];
  };

  if (quotes.length === 0) {
    return (
      <div className="text-center py-12" data-testid="no-evidence">
        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p className="mt-2 text-sm text-gray-500">No guidance evidence available</p>
      </div>
    );
  }

  return (
    <div data-testid="evidence">
      {/* Evidence Cards */}
      <div className="space-y-4 mb-8">
        {quotes.map((quote, idx) => (
          <div key={idx} className="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-shadow duration-200">
            <div className="p-4">
              {/* Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded border ${getCategoryBadge(quote.category)}`}>
                      {quote.category?.replace('_', ' ').toUpperCase() || 'UNKNOWN'}
                    </span>
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${getTypeBadge(quote.type)}`}>
                      {quote.type?.toUpperCase()}
                    </span>
                  </div>
                  <h4 className="text-sm font-bold text-gray-900 uppercase tracking-wide">
                    {quote.metric?.replace('_', ' ')}
                  </h4>
                </div>
                <button
                  onClick={() => setExpandedQuote(expandedQuote === idx ? null : idx)}
                  className="text-blue-600 hover:text-blue-700 text-xs font-medium"
                  data-testid={`view-source-${idx}`}
                >
                  {expandedQuote === idx ? 'Hide Source' : 'View Source'}
                </button>
              </div>

              {/* Value Display */}
              {(quote.value_min !== null || quote.value_max !== null) && (
                <div className="mb-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
                  <div className="flex items-baseline space-x-2">
                    <span className="text-2xl font-bold text-gray-900">
                      {quote.value_min === quote.value_max 
                        ? quote.value_min 
                        : `${quote.value_min || '?'} - ${quote.value_max || '?'}`}
                    </span>
                    {quote.unit && (
                      <span className="text-sm text-gray-600">
                        {quote.unit.replace('_', ' ')}
                      </span>
                    )}
                    {quote.timeline && (
                      <span className="text-xs text-gray-500 ml-2">
                        ({quote.timeline})
                      </span>
                    )}
                  </div>
                </div>
              )}

              {/* Quote */}
              <blockquote className="border-l-4 border-blue-500 pl-4 py-2 mb-3 bg-blue-50 rounded-r">
                <p className="text-sm text-gray-700 italic leading-relaxed">
                  "{quote.quote}"
                </p>
              </blockquote>

              {/* Metadata */}
              <div className="flex items-center justify-between text-xs text-gray-500">
                <div className="flex items-center space-x-4">
                  <span className="flex items-center">
                    <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    {quote.source || 'Unknown'}
                  </span>
                  {quote.source_page && (
                    <span>Page {quote.source_page}</span>
                  )}
                  {quote.source_type && (
                    <span className="capitalize">{quote.source_type}</span>
                  )}
                </div>
                <span className={`font-medium ${getConfidenceBadge(quote.confidence)}`}>
                  {quote.confidence?.toUpperCase()} CONFIDENCE
                </span>
              </div>

              {/* Expanded Source Details */}
              {expandedQuote === idx && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <h5 className="text-xs font-semibold text-gray-700 mb-2 uppercase">Source Details</h5>
                  <div className="grid grid-cols-2 gap-3 text-xs">
                    <div>
                      <span className="text-gray-500">Document:</span>
                      <span className="ml-2 text-gray-900 font-medium">{quote.source || 'N/A'}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Page:</span>
                      <span className="ml-2 text-gray-900 font-medium">{quote.source_page || 'N/A'}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Type:</span>
                      <span className="ml-2 text-gray-900 font-medium capitalize">{quote.source_type || 'N/A'}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Method:</span>
                      <span className="ml-2 text-gray-900 font-medium">{quote.extraction_method || 'N/A'}</span>
                    </div>
                  </div>
                  {quote.notes && (
                    <div className="mt-3 p-2 bg-amber-50 border border-amber-200 rounded">
                      <p className="text-xs text-amber-800">{quote.notes}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Conflicts Section */}
      {conflicts.length > 0 && (
        <div className="mt-8">
          <h3 className="text-sm font-semibold text-gray-700 mb-4 uppercase tracking-wide flex items-center">
            <svg className="w-5 h-5 text-red-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            Conflicts Detected
          </h3>
          <div className="space-y-4">
            {conflicts.map((conflict, idx) => (
              <div key={idx} className="bg-red-50 border border-red-200 rounded-lg p-4">
                <h4 className="text-sm font-bold text-red-900 mb-2">
                  {conflict.metric?.toUpperCase().replace('_', ' ')}
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                  <div className="bg-white p-3 rounded border border-red-200">
                    <div className="font-semibold text-gray-700 mb-1">Source A: {conflict.source_a}</div>
                    <p className="text-gray-600 italic">"{conflict.quote_a}"</p>
                  </div>
                  <div className="bg-white p-3 rounded border border-red-200">
                    <div className="font-semibold text-gray-700 mb-1">Source B: {conflict.source_b}</div>
                    <p className="text-gray-600 italic">"{conflict.quote_b}"</p>
                  </div>
                </div>
                {conflict.notes && (
                  <p className="text-xs text-red-700 mt-2">{conflict.notes}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default Evidence;
