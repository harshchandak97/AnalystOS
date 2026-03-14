import React from 'react';

function Assumptions({ company }) {
  const assumptions = company.assumptions || {};
  const quotes = company.quotes || [];
  
  // Find evidence for revenue and margin
  const revenueEvidence = quotes.filter(q => 
    q.metric === 'revenue_growth' && q.type === 'explicit'
  );
  const marginEvidence = quotes.filter(q => 
    ['ebitda_margin', 'pat_margin', 'margin', 'margin_floor'].includes(q.metric) && q.type === 'explicit'
  );

  return (
    <div data-testid="assumptions">
      {/* Assumptions Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Revenue Growth Assumptions */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-4 uppercase tracking-wide">Revenue Growth Assumptions (%)</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg border border-red-200">
              <span className="text-sm font-medium text-red-900">Bear Case</span>
              <span className="text-2xl font-bold text-red-900">
                {assumptions.bear_revenue_growth !== null ? `${assumptions.bear_revenue_growth}%` : 'N/A'}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200">
              <span className="text-sm font-medium text-blue-900">Base Case</span>
              <span className="text-2xl font-bold text-blue-900">
                {assumptions.base_revenue_growth !== null ? `${assumptions.base_revenue_growth}%` : 'N/A'}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-200">
              <span className="text-sm font-medium text-green-900">Bull Case</span>
              <span className="text-2xl font-bold text-green-900">
                {assumptions.bull_revenue_growth !== null ? `${assumptions.bull_revenue_growth}%` : 'N/A'}
              </span>
            </div>
          </div>
          
          {/* Revenue Evidence */}
          {revenueEvidence.length > 0 && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <h4 className="text-xs font-semibold text-gray-600 mb-2 uppercase">Supporting Evidence</h4>
              {revenueEvidence.map((ev, idx) => (
                <div key={idx} className="text-xs text-gray-600 mb-2 p-2 bg-gray-50 rounded">
                  <div className="font-medium text-gray-900">{ev.source} (Page {ev.source_page})</div>
                  <p className="italic mt-1">"{ev.quote?.substring(0, 100)}..."</p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Margin Assumptions */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-4 uppercase tracking-wide">Margin Assumptions (%)</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg border border-red-200">
              <span className="text-sm font-medium text-red-900">Bear Case</span>
              <span className="text-2xl font-bold text-red-900">
                {assumptions.bear_margin !== null ? `${assumptions.bear_margin}%` : 'N/A'}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200">
              <span className="text-sm font-medium text-blue-900">Base Case</span>
              <span className="text-2xl font-bold text-blue-900">
                {assumptions.base_margin !== null ? `${assumptions.base_margin}%` : 'N/A'}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-200">
              <span className="text-sm font-medium text-green-900">Bull Case</span>
              <span className="text-2xl font-bold text-green-900">
                {assumptions.bull_margin !== null ? `${assumptions.bull_margin}%` : 'N/A'}
              </span>
            </div>
          </div>
          
          {/* Margin Evidence */}
          {marginEvidence.length > 0 && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <h4 className="text-xs font-semibold text-gray-600 mb-2 uppercase">Supporting Evidence</h4>
              {marginEvidence.map((ev, idx) => (
                <div key={idx} className="text-xs text-gray-600 mb-2 p-2 bg-gray-50 rounded">
                  <div className="font-medium text-gray-900">{ev.source} (Page {ev.source_page})</div>
                  <p className="italic mt-1">"{ev.quote?.substring(0, 100)}..."</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Valuation Parameters */}
      <div className="bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 rounded-lg p-6">
        <h3 className="text-sm font-semibold text-purple-900 mb-4 uppercase tracking-wide">Valuation Parameters</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <div className="text-xs text-purple-700 mb-1">Target P/E Multiple</div>
            <div className="text-2xl font-bold text-purple-900">{company.target_pe?.toFixed(1)}x</div>
            <div className="text-xs text-purple-600 mt-1">From historical median</div>
          </div>
          <div>
            <div className="text-xs text-purple-700 mb-1">Current Price</div>
            <div className="text-2xl font-bold text-purple-900">₹{company.current_price?.toFixed(2)}</div>
          </div>
          <div>
            <div className="text-xs text-purple-700 mb-1">Current EPS</div>
            <div className="text-2xl font-bold text-purple-900">₹{company.current_eps?.toFixed(2)}</div>
          </div>
        </div>
      </div>

      {/* Methodology Note */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h4 className="text-xs font-semibold text-blue-900 mb-2 uppercase">Methodology</h4>
        <p className="text-xs text-blue-800 leading-relaxed">
          <strong>Bear scenario:</strong> Uses minimum guidance value. <strong>Base scenario:</strong> Uses midpoint of guidance range. <strong>Bull scenario:</strong> Uses maximum guidance value. EPS is projected using revenue growth assumptions over a 3-year horizon. Target price = Projected EPS × Historical Median P/E.
        </p>
      </div>
    </div>
  );
}

export default Assumptions;
