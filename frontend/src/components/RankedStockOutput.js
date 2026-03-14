import React from 'react';

function RankedStockOutput({ ranked, companyResults, onCompanySelect, selectedCompanyId }) {
  const getVerdictBadge = (verdict) => {
    const variants = {
      'High Conviction': 'bg-green-100 text-green-800 border-green-200',
      'Watchlist': 'bg-amber-100 text-amber-800 border-amber-200',
      'Avoid': 'bg-red-100 text-red-800 border-red-200',
      'Insufficient Data': 'bg-gray-100 text-gray-600 border-gray-200',
    };
    return variants[verdict] || variants['Insufficient Data'];
  };

  const getConfidenceBadge = (confidence) => {
    const variants = {
      'High': 'bg-blue-100 text-blue-800',
      'Medium': 'bg-purple-100 text-purple-800',
      'Low': 'bg-gray-100 text-gray-600',
    };
    return variants[confidence] || variants['Low'];
  };

  return (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-900">Ranked Stock Comparison</h2>
        <p className="text-sm text-gray-500">Click any row to see detailed analysis</p>
      </div>
      
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Rank
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Company
                </th>
                <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Base CAGR
                </th>
                <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Bull CAGR
                </th>
                <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Bear CAGR
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Verdict
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Confidence
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {ranked && ranked.map((item, idx) => {
                const companyDetail = companyResults?.find(c => c.company_id === item.company_id);
                const isSelected = selectedCompanyId === item.company_id;
                
                return (
                  <tr
                    key={item.company_id}
                    onClick={() => onCompanySelect(item.company_id)}
                    className={`cursor-pointer transition-all duration-150 ${
                      isSelected ? 'bg-blue-50 hover:bg-blue-100 shadow-md' : 'hover:bg-gray-50'
                    }`}
                    data-testid={`ranked-row-${item.company_id}`}
                  >
                    <td className="px-6 py-5 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className={`flex-shrink-0 h-10 w-10 rounded-full flex items-center justify-center text-sm font-bold ${
                          idx === 0 ? 'bg-yellow-100 text-yellow-800 shadow-md' :
                          idx === 1 ? 'bg-gray-100 text-gray-700' :
                          idx === 2 ? 'bg-orange-100 text-orange-700' :
                          'bg-gray-50 text-gray-600'
                        }`}>
                          #{idx + 1}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-5 whitespace-nowrap">
                      <div className="text-base font-bold text-gray-900">{item.company_name}</div>
                      <div className="text-xs text-gray-500 font-mono">{item.company_id}</div>
                    </td>
                    <td className="px-6 py-5 whitespace-nowrap text-center">
                      <div className="text-2xl font-bold text-gray-900">
                        {item.base_cagr_pct?.toFixed(1) || '0.0'}%
                      </div>
                    </td>
                    <td className="px-6 py-5 whitespace-nowrap text-center">
                      <div className="text-lg font-semibold text-green-600">
                        {item.bull?.cagr_pct?.toFixed(1) || '0.0'}%
                      </div>
                    </td>
                    <td className="px-6 py-5 whitespace-nowrap text-center">
                      <div className="text-lg font-semibold text-red-600">
                        {item.bear?.cagr_pct?.toFixed(1) || '0.0'}%
                      </div>
                    </td>
                    <td className="px-6 py-5 whitespace-nowrap">
                      <span className={`inline-flex px-3 py-1 text-xs font-semibold rounded-full border ${getVerdictBadge(item.verdict)}`}>
                        {item.verdict}
                      </span>
                    </td>
                    <td className="px-6 py-5 whitespace-nowrap">
                      <span className={`inline-flex px-3 py-1 text-xs font-medium rounded-full ${getConfidenceBadge(companyDetail?.confidence)}`}>
                        {companyDetail?.confidence || 'N/A'}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default RankedStockOutput;
