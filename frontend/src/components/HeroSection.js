import React from 'react';

function HeroSection({ metrics }) {
  return (
    <div className="mb-8" data-testid="hero-section">
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-2xl shadow-xl p-8 text-white">
        <div className="max-w-3xl">
          <h2 className="text-3xl font-bold mb-2">Sector Analysis Complete</h2>
          <p className="text-blue-100 text-sm mb-6">
            Forward guidance extracted, assumptions built, valuations run across bull/base/bear scenarios
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20" data-testid="top-opportunity-card">
            <div className="text-blue-100 text-xs font-semibold uppercase tracking-wide mb-2">Top Opportunity</div>
            <div className="text-2xl font-bold">{metrics.topOpportunity}</div>
          </div>
          
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20" data-testid="companies-analyzed-card">
            <div className="text-blue-100 text-xs font-semibold uppercase tracking-wide mb-2">Companies Analyzed</div>
            <div className="text-2xl font-bold">{metrics.companiesAnalyzed}</div>
          </div>
          
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20" data-testid="best-cagr-card">
            <div className="text-blue-100 text-xs font-semibold uppercase tracking-wide mb-2">Best Base CAGR</div>
            <div className="text-2xl font-bold">{metrics.bestCagr.toFixed(1)}%</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default HeroSection;
