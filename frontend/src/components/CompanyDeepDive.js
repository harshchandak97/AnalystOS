import React, { useState } from 'react';
import HistoricalFinancials from './HistoricalFinancials';
import Evidence from './Evidence';
import Assumptions from './Assumptions';
import Valuation from './Valuation';
import AnalystNote from './AnalystNote';

function CompanyDeepDive({ company, rank, total }) {
  const [activeTab, setActiveTab] = useState('financials');

  const tabs = [
    { id: 'financials', label: 'Historical Financials' },
    { id: 'evidence', label: 'Evidence' },
    { id: 'assumptions', label: 'Assumptions' },
    { id: 'valuation', label: 'Valuation' },
    { id: 'note', label: 'Analyst Note' },
  ];

  return (
    <div className="mb-8" data-testid="company-deep-dive">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Company Deep Dive</h2>
          <p className="text-sm text-gray-500 mt-1">
            {company.company_name} — Rank #{rank} of {total}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className={`inline-flex px-3 py-1 text-xs font-semibold rounded-full ${
            company.verdict === 'High Conviction' ? 'bg-green-100 text-green-800 border border-green-200' :
            company.verdict === 'Watchlist' ? 'bg-amber-100 text-amber-800 border border-amber-200' :
            company.verdict === 'Avoid' ? 'bg-red-100 text-red-800 border border-red-200' :
            'bg-gray-100 text-gray-600 border border-gray-200'
          }`}>
            {company.verdict}
          </span>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-6 text-sm font-medium border-b-2 transition-colors duration-200 ${
                  activeTab === tab.id
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                data-testid={`tab-${tab.id}`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {activeTab === 'financials' && (
            <HistoricalFinancials company={company} />
          )}
          {activeTab === 'evidence' && (
            <Evidence company={company} />
          )}
          {activeTab === 'assumptions' && (
            <Assumptions company={company} />
          )}
          {activeTab === 'valuation' && (
            <Valuation company={company} />
          )}
          {activeTab === 'note' && (
            <AnalystNote company={company} rank={rank} total={total} />
          )}
        </div>
      </div>
    </div>
  );
}

export default CompanyDeepDive;
