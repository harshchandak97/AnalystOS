import React from 'react';

function SectorSelector({ sectors, selectedSector, onSectorChange, onRunAnalysis, loading }) {
  return (
    <div className="flex items-center space-x-4">
      <select
        value={selectedSector}
        onChange={(e) => onSectorChange(e.target.value)}
        disabled={loading}
        className="block w-48 px-3 py-2 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed text-sm font-medium text-gray-700"
        data-testid="sector-selector"
      >
        {sectors.map(sector => (
          <option key={sector} value={sector}>
            {sector.replace('_', ' ').toUpperCase()}
          </option>
        ))}
      </select>
      
      <button
        onClick={onRunAnalysis}
        disabled={loading}
        className="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200 text-sm"
        data-testid="run-analysis-button"
      >
        {loading ? 'Running...' : 'Run Analysis'}
      </button>
    </div>
  );
}

export default SectorSelector;
