import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function Valuation({ company }) {
  const scenarios = company.scenarios || {};
  
  if (!scenarios.bear && !scenarios.base && !scenarios.bull) {
    return (
      <div className="text-center py-12" data-testid="no-valuation">
        <p className="text-sm text-gray-500">Insufficient data for valuation scenarios</p>
      </div>
    );
  }

  const chartData = [
    {
      scenario: 'Bear',
      'Projected EPS': scenarios.bear?.projected_eps || 0,
      'Target Price': scenarios.bear?.target_price || 0,
      'CAGR %': scenarios.bear?.cagr_pct || 0,
    },
    {
      scenario: 'Base',
      'Projected EPS': scenarios.base?.projected_eps || 0,
      'Target Price': scenarios.base?.target_price || 0,
      'CAGR %': scenarios.base?.cagr_pct || 0,
    },
    {
      scenario: 'Bull',
      'Projected EPS': scenarios.bull?.projected_eps || 0,
      'Target Price': scenarios.bull?.target_price || 0,
      'CAGR %': scenarios.bull?.cagr_pct || 0,
    },
  ];

  return (
    <div data-testid="valuation">
      {/* Scenario Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Bear Scenario */}
        {scenarios.bear && (
          <div className="bg-white border-2 border-red-200 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-red-900">Bear Case</h3>
              <span className="text-2xl font-bold text-red-600">{scenarios.bear.cagr_pct.toFixed(1)}%</span>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Projected Revenue</span>
                <span className="font-semibold text-gray-900">₹{scenarios.bear.projected_revenue.toFixed(2)} Cr</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Projected EPS</span>
                <span className="font-semibold text-gray-900">₹{scenarios.bear.projected_eps.toFixed(4)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Projected Margin</span>
                <span className="font-semibold text-gray-900">{scenarios.bear.projected_margin.toFixed(2)}%</span>
              </div>
              <div className="pt-3 border-t border-red-200">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Target Price</span>
                  <span className="text-xl font-bold text-red-900">₹{scenarios.bear.target_price.toFixed(2)}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Base Scenario */}
        {scenarios.base && (
          <div className="bg-white border-2 border-blue-200 rounded-lg p-6 shadow-md">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-blue-900">Base Case</h3>
              <span className="text-2xl font-bold text-blue-600">{scenarios.base.cagr_pct.toFixed(1)}%</span>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Projected Revenue</span>
                <span className="font-semibold text-gray-900">₹{scenarios.base.projected_revenue.toFixed(2)} Cr</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Projected EPS</span>
                <span className="font-semibold text-gray-900">₹{scenarios.base.projected_eps.toFixed(4)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Projected Margin</span>
                <span className="font-semibold text-gray-900">{scenarios.base.projected_margin.toFixed(2)}%</span>
              </div>
              <div className="pt-3 border-t border-blue-200">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Target Price</span>
                  <span className="text-xl font-bold text-blue-900">₹{scenarios.base.target_price.toFixed(2)}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Bull Scenario */}
        {scenarios.bull && (
          <div className="bg-white border-2 border-green-200 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-green-900">Bull Case</h3>
              <span className="text-2xl font-bold text-green-600">{scenarios.bull.cagr_pct.toFixed(1)}%</span>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Projected Revenue</span>
                <span className="font-semibold text-gray-900">₹{scenarios.bull.projected_revenue.toFixed(2)} Cr</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Projected EPS</span>
                <span className="font-semibold text-gray-900">₹{scenarios.bull.projected_eps.toFixed(4)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Projected Margin</span>
                <span className="font-semibold text-gray-900">{scenarios.bull.projected_margin.toFixed(2)}%</span>
              </div>
              <div className="pt-3 border-t border-green-200">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Target Price</span>
                  <span className="text-xl font-bold text-green-900">₹{scenarios.bull.target_price.toFixed(2)}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* CAGR Comparison Chart */}
      <div className="mb-8">
        <h3 className="text-sm font-semibold text-gray-700 mb-4 uppercase tracking-wide">Expected CAGR Comparison</h3>
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="scenario" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} label={{ value: 'CAGR %', angle: -90, position: 'insideLeft' }} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
                formatter={(value) => `${value.toFixed(2)}%`}
              />
              <Bar dataKey="CAGR %" fill="#3b82f6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Target Price Comparison Chart */}
      <div className="mb-8">
        <h3 className="text-sm font-semibold text-gray-700 mb-4 uppercase tracking-wide">Target Price Comparison</h3>
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="scenario" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} label={{ value: 'Price (₹)', angle: -90, position: 'insideLeft' }} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
                formatter={(value) => `₹${value.toFixed(2)}`}
              />
              <Bar dataKey="Target Price" fill="#10b981" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Current vs Target Price */}
      <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 border border-indigo-200 rounded-lg p-6">
        <h3 className="text-sm font-semibold text-indigo-900 mb-4 uppercase tracking-wide">Price Analysis</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div className="text-xs text-indigo-700 mb-1">Current Price</div>
            <div className="text-xl font-bold text-indigo-900">₹{company.current_price?.toFixed(2)}</div>
          </div>
          <div>
            <div className="text-xs text-indigo-700 mb-1">Bear Target</div>
            <div className="text-xl font-bold text-red-600">₹{scenarios.bear?.target_price.toFixed(2) || 'N/A'}</div>
            <div className="text-xs text-red-600 mt-1">
              {scenarios.bear ? ((scenarios.bear.target_price / company.current_price - 1) * 100).toFixed(1) + '%' : ''}
            </div>
          </div>
          <div>
            <div className="text-xs text-indigo-700 mb-1">Base Target</div>
            <div className="text-xl font-bold text-blue-600">₹{scenarios.base?.target_price.toFixed(2) || 'N/A'}</div>
            <div className="text-xs text-blue-600 mt-1">
              {scenarios.base ? ((scenarios.base.target_price / company.current_price - 1) * 100).toFixed(1) + '%' : ''}
            </div>
          </div>
          <div>
            <div className="text-xs text-indigo-700 mb-1">Bull Target</div>
            <div className="text-xl font-bold text-green-600">₹{scenarios.bull?.target_price.toFixed(2) || 'N/A'}</div>
            <div className="text-xs text-green-600 mt-1">
              {scenarios.bull ? ((scenarios.bull.target_price / company.current_price - 1) * 100).toFixed(1) + '%' : ''}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Valuation;
