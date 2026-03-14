import React, { useState } from 'react';

function LandingSection({ sectors, onSectorSelect }) {
  const [selectedSector, setSelectedSector] = useState('');

  const handleContinue = () => {
    if (selectedSector) {
      onSectorSelect(selectedSector);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="max-w-4xl mx-auto px-6 py-12 text-center">
        {/* Title */}
        <h1 className="text-6xl font-bold text-gray-900 mb-4" data-testid="landing-title">
          AnalystOS
        </h1>
        
        {/* Subtitle */}
        <p className="text-2xl text-gray-600 mb-6">
          AI-native sector analyst workflow
        </p>
        
        {/* Description */}
        <p className="text-lg text-gray-700 leading-relaxed mb-12 max-w-3xl mx-auto">
          Select a sector, choose companies, and AnalystOS will automatically read company documents, 
          extract management guidance, build model-ready assumptions, run scenario analysis, and rank 
          opportunities with full source traceability.
        </p>

        {/* Sector Selection Card */}
        <div className="bg-white rounded-2xl shadow-xl p-12 max-w-2xl mx-auto border border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Select Sector</h2>
          
          <div className="grid grid-cols-1 gap-4 mb-8">
            {sectors.map(sector => (
              <button
                key={sector}
                onClick={() => setSelectedSector(sector)}
                className={`p-6 rounded-xl border-2 transition-all duration-200 text-left ${
                  selectedSector === sector
                    ? 'border-blue-600 bg-blue-50 shadow-md'
                    : 'border-gray-200 bg-white hover:border-blue-300 hover:bg-gray-50'
                }`}
                data-testid={`sector-${sector}`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">
                      {sector.replace('_', ' ').toUpperCase()}
                    </h3>
                    <p className="text-sm text-gray-500 mt-1">
                      {sector === 'power_equipment' ? '3 companies available' : 'Select to view companies'}
                    </p>
                  </div>
                  {selectedSector === sector && (
                    <svg className="w-8 h-8 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  )}
                </div>
              </button>
            ))}
          </div>

          <button
            onClick={handleContinue}
            disabled={!selectedSector}
            className="w-full py-4 px-8 bg-blue-600 text-white font-bold text-lg rounded-xl hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-300 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg"
            data-testid="continue-button"
          >
            Continue to Stock Selection →
          </button>
        </div>

        {/* Footer note */}
        <p className="text-sm text-gray-500 mt-8">
          All data sourced from local company documents and financial records
        </p>
      </div>
    </div>
  );
}

export default LandingSection;
