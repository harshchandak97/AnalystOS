import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';

function HistoricalFinancials({ company }) {
  const financials = company.financials || {};
  const annual = financials.annual_financials || {};
  const metadata = financials.metadata || {};

  // Key metrics
  const currentPrice = metadata.current_price || company.current_price || 0;
  const currentEps = company.current_eps || 0;
  const historicalMedianPE = company.target_pe || 0;

  // Prepare chart data
  const periods = annual.periods || [];
  const salesData = annual.sales || {};
  const netProfitData = annual.net_profit || {};
  const profitBeforeTaxData = annual.profit_before_tax || {};

  const chartData = periods.map(period => ({
    period,
    sales: salesData[period] || 0,
    netProfit: netProfitData[period] || 0,
    profitBeforeTax: profitBeforeTaxData[period] || 0,
    margin: salesData[period] ? ((netProfitData[period] || 0) / salesData[period] * 100).toFixed(1) : 0,
  }));

  if (!company.has_financials) {
    return (
      <div className="text-center py-12" data-testid="no-financials">
        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p className="mt-2 text-sm text-gray-500">
          No financial data available for {company.company_name}
        </p>
        <p className="text-xs text-gray-400 mt-1">
          Add data/financials/{company.company_id.toLowerCase()}.json to see historical financials
        </p>
      </div>
    );
  }

  return (
    <div data-testid="historical-financials">
      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-6 border border-blue-200">
          <div className="text-xs font-semibold text-blue-700 uppercase tracking-wide mb-2">Current Price</div>
          <div className="text-3xl font-bold text-blue-900">₹{currentPrice.toFixed(2)}</div>
        </div>
        
        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-6 border border-green-200">
          <div className="text-xs font-semibold text-green-700 uppercase tracking-wide mb-2">Current EPS</div>
          <div className="text-3xl font-bold text-green-900">₹{currentEps.toFixed(2)}</div>
        </div>
        
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-6 border border-purple-200">
          <div className="text-xs font-semibold text-purple-700 uppercase tracking-wide mb-2">Historical Median P/E</div>
          <div className="text-3xl font-bold text-purple-900">{historicalMedianPE.toFixed(1)}x</div>
        </div>
      </div>

      {/* Revenue Chart */}
      <div className="mb-8">
        <h3 className="text-sm font-semibold text-gray-700 mb-4 uppercase tracking-wide">Revenue History (₹ Cr)</h3>
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="period" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
                formatter={(value) => `₹${value.toFixed(2)} Cr`}
              />
              <Bar dataKey="sales" fill="#3b82f6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Profitability Chart */}
      <div className="mb-8">
        <h3 className="text-sm font-semibold text-gray-700 mb-4 uppercase tracking-wide">Profitability History (₹ Cr)</h3>
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="period" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
                formatter={(value) => `₹${value.toFixed(2)} Cr`}
              />
              <Legend />
              <Line type="monotone" dataKey="profitBeforeTax" stroke="#8b5cf6" strokeWidth={2} name="Profit Before Tax" />
              <Line type="monotone" dataKey="netProfit" stroke="#10b981" strokeWidth={2} name="Net Profit (PAT)" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Margin Chart */}
      <div className="mb-8">
        <h3 className="text-sm font-semibold text-gray-700 mb-4 uppercase tracking-wide">Net Margin History (%)</h3>
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="period" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
                formatter={(value) => `${value}%`}
              />
              <Line type="monotone" dataKey="margin" stroke="#f59e0b" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Financial Table */}
      <div>
        <h3 className="text-sm font-semibold text-gray-700 mb-4 uppercase tracking-wide">Annual Financials Summary</h3>
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Metric</th>
                  {periods.map(period => (
                    <th key={period} className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase">{period}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                <tr>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">Sales (₹ Cr)</td>
                  {periods.map(period => (
                    <td key={period} className="px-4 py-3 text-sm text-right text-gray-700">{(salesData[period] || 0).toFixed(2)}</td>
                  ))}
                </tr>
                <tr className="bg-gray-50">
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">Net Profit (₹ Cr)</td>
                  {periods.map(period => (
                    <td key={period} className="px-4 py-3 text-sm text-right text-gray-700">{(netProfitData[period] || 0).toFixed(2)}</td>
                  ))}
                </tr>
                <tr>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">Net Margin (%)</td>
                  {periods.map(period => {
                    const margin = salesData[period] ? ((netProfitData[period] || 0) / salesData[period] * 100) : 0;
                    return (
                      <td key={period} className="px-4 py-3 text-sm text-right text-gray-700">{margin.toFixed(1)}%</td>
                    );
                  })}
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

export default HistoricalFinancials;
