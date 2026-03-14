import React from 'react';

function StockSelection({ sector, availableStocks, selectedStocks, onStockToggle, onRunAnalysis, onBack }) {
  console.log('StockSelection render:', { sector, availableStocks, selectedStocks });
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">AnalystOS</h1>
              <p className="text-sm text-gray-500 mt-1">
                {sector.replace('_', ' ').toUpperCase()} — Select companies to analyze
              </p>
            </div>
            <button
              onClick={onBack}
              className="px-4 py-2 text-gray-600 hover:text-gray-900 font-medium"
            >
              ← Back to Sectors
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Select Companies</h2>
          <p className="text-gray-600">
            Choose one or more companies to analyze. AnalystOS will extract guidance, build assumptions, and rank opportunities.
          </p>
        </div>

        {/* Loading or Empty State */}
        {!availableStocks || availableStocks.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading companies...</p>
          </div>
        ) : (
          <>
            {/* Stock Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
              {availableStocks.map(stock => {
            const isSelected = selectedStocks.includes(stock.company_id);
            
            return (
              <button
                key={stock.company_id}
                onClick={() => onStockToggle(stock.company_id)}
                className={`p-6 rounded-xl border-2 transition-all duration-200 text-left ${
                  isSelected
                    ? 'border-blue-600 bg-blue-50 shadow-lg transform scale-105'
                    : 'border-gray-200 bg-white hover:border-blue-300 hover:shadow-md'
                }`}
                data-testid={`stock-${stock.company_id}`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-gray-900">
                      {stock.company_name}
                    </h3>
                    <p className="text-sm text-gray-500 font-mono mt-1">
                      {stock.company_id.toUpperCase()}
                    </p>
                  </div>
                  <div className={`flex-shrink-0 w-6 h-6 rounded border-2 flex items-center justify-center ${
                    isSelected ? 'bg-blue-600 border-blue-600' : 'border-gray-300'
                  }`}>
                    {isSelected && (
                      <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center text-sm text-gray-600">
                    <svg className="w-4 h-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span>{stock.pdf_files?.length || 0} documents available</span>
                  </div>
                  {stock.has_guidance && (
                    <div className="flex items-center text-sm text-gray-600">
                      <svg className="w-4 h-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      <span>Guidance extracted</span>
                    </div>
                  )}
                </div>
              </button>
            );
          })}
        </div>

        {/* Selection Summary & CTA */}
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-200 sticky bottom-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 mb-1">Selected Companies</p>
              <p className="text-3xl font-bold text-gray-900">
                {selectedStocks.length} of {availableStocks.length}
              </p>
              {selectedStocks.length > 0 && (
                <p className="text-sm text-gray-600 mt-2">
                  {selectedStocks.map(id => id.toUpperCase()).join(', ')}
                </p>
              )}
            </div>
            <button
              onClick={onRunAnalysis}
              disabled={selectedStocks.length === 0}
              className="px-12 py-4 bg-blue-600 text-white font-bold text-xl rounded-xl hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-300 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg"
              data-testid="run-analystos-button"
            >
              Run AnalystOS →
            </button>
          </div>
        </div>
        </>
        )}
      </div>
    </div>
  );
}

export default StockSelection;
