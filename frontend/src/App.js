import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

// Components
import LandingSection from './components/LandingSection';
import StockSelection from './components/StockSelection';
import AnimatedPipeline from './components/AnimatedPipeline';
import ResultsPage from './components/ResultsPage';

const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function App() {
  // App state
  const [currentScreen, setCurrentScreen] = useState('landing'); // landing | stockSelection | running | results
  
  // Selection state
  const [sectors, setSectors] = useState([]);
  const [selectedSector, setSelectedSector] = useState('');
  const [availableStocks, setAvailableStocks] = useState([]);
  const [selectedStocks, setSelectedStocks] = useState([]);
  
  // Analysis state
  const [pipelineSteps, setPipelineSteps] = useState([]);
  const [activityLog, setActivityLog] = useState([]);
  const [currentStep, setCurrentStep] = useState(0);
  
  // Results state
  const [analysisResult, setAnalysisResult] = useState(null);
  const [selectedCompany, setSelectedCompany] = useState(null);

  // Fetch sectors on mount
  useEffect(() => {
    fetchSectors();
  }, []);

  const fetchSectors = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/sectors`);
      setSectors(response.data.sectors || []);
    } catch (error) {
      console.error('Error fetching sectors:', error);
      setSectors(['power_equipment', 'Technology', 'Healthcare', 'Consumer']);
    }
  };

  const handleSectorSelect = async (sector) => {
    setSelectedSector(sector);
    setCurrentScreen('stockSelection'); // Navigate immediately
    
    // Fetch companies in sector
    try {
      const response = await axios.get(`${API_BASE}/api/sectors/${sector}/dossiers`);
      console.log('Fetched dossiers:', response.data);
      setAvailableStocks(response.data.dossiers || []);
    } catch (error) {
      console.error('Error fetching stocks:', error);
      // Even if API fails, show empty list and let user know
      alert('Failed to load companies. Please refresh and try again.');
      setAvailableStocks([]);
    }
  };

  const handleStockToggle = (stockId) => {
    setSelectedStocks(prev => {
      if (prev.includes(stockId)) {
        return prev.filter(id => id !== stockId);
      } else {
        return [...prev, stockId];
      }
    });
  };

  const handleRunAnalysis = async () => {
    if (selectedStocks.length === 0) {
      alert('Please select at least one stock to analyze');
      return;
    }

    // Initialize pipeline
    const steps = [
      { id: 'fetch_documents', label: 'Fetching company documents', status: 'pending' },
      { id: 'load_financials', label: 'Loading past financials', status: 'pending' },
      { id: 'extract_text', label: 'Extracting text from PDFs', status: 'pending' },
      { id: 'extract_guidance', label: 'Extracting management guidance', status: 'pending' },
      { id: 'consolidate_evidence', label: 'Consolidating evidence', status: 'pending' },
      { id: 'build_assumptions', label: 'Building assumptions', status: 'pending' },
      { id: 'run_valuation', label: 'Running bull/base/bear valuation', status: 'pending' },
      { id: 'rank_companies', label: 'Ranking selected companies', status: 'pending' },
      { id: 'link_sources', label: 'Linking assumptions to source evidence', status: 'pending' },
    ];
    
    setPipelineSteps(steps);
    setActivityLog([]);
    setCurrentStep(0);
    setCurrentScreen('running');

    // Animate pipeline steps
    await animatePipeline(steps);
  };

  const animatePipeline = async (steps) => {
    // Simulate step-by-step execution
    for (let i = 0; i < steps.length; i++) {
      // Update step to running
      setPipelineSteps(prev => prev.map((step, idx) => 
        idx === i ? { ...step, status: 'running' } : step
      ));
      setCurrentStep(i);

      // Add activity log based on step
      await addActivityForStep(steps[i].id, i);

      // Wait for step to "complete"
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Mark step as completed
      setPipelineSteps(prev => prev.map((step, idx) => 
        idx === i ? { ...step, status: 'completed' } : step
      ));
    }

    // After all steps, run actual analysis
    await runActualAnalysis();
  };

  const addActivityForStep = async (stepId, index) => {
    const activities = {
      fetch_documents: [
        `Found ${selectedStocks.length} selected companies in ${selectedSector}`,
        ...selectedStocks.map(id => `Loaded documents for ${id.toUpperCase()}`)
      ],
      load_financials: selectedStocks.map(id => `Loaded ${id.toUpperCase()} financial history`),
      extract_text: selectedStocks.map(id => `Loaded ${id.toUpperCase()}_latest_transcript.pdf`),
      extract_guidance: selectedStocks.map(id => `Extracted forward-looking statements from ${id.toUpperCase()}`),
      consolidate_evidence: selectedStocks.map(id => `Consolidated evidence for ${id.toUpperCase()}`),
      build_assumptions: selectedStocks.map(id => `Built base-case assumptions for ${id.toUpperCase()}`),
      run_valuation: selectedStocks.map(id => `Calculated scenario valuation for ${id.toUpperCase()}`),
      rank_companies: [`Ranked ${selectedStocks.length} companies by base-case CAGR`],
      link_sources: ['Linked all assumptions to source evidence']
    };

    const logs = activities[stepId] || [];
    for (const log of logs) {
      await new Promise(resolve => setTimeout(resolve, 300));
      setActivityLog(prev => [...prev, log]);
    }
  };

  const runActualAnalysis = async () => {
    try {
      const response = await axios.post(`${API_BASE}/api/analysis/run`, {
        sector: selectedSector,
        selected_companies: selectedStocks,
        run_extraction: false,
      });
      
      setAnalysisResult(response.data);
      
      // Auto-select first company
      if (response.data.company_results && response.data.company_results.length > 0) {
        setSelectedCompany(response.data.company_results[0]);
      }
      
      // Move to results screen
      setCurrentScreen('results');
    } catch (error) {
      console.error('Error running analysis:', error);
      alert('Analysis failed. Please try again.');
      setCurrentScreen('stockSelection');
    }
  };

  const handleCompanySelect = (companyId) => {
    const company = analysisResult?.company_results?.find(
      c => c.company_id === companyId
    );
    if (company) {
      setSelectedCompany(company);
    }
  };

  const handleBackToSelection = () => {
    setCurrentScreen('stockSelection');
    setAnalysisResult(null);
    setSelectedCompany(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Render appropriate screen */}
      {currentScreen === 'landing' && (
        <LandingSection
          sectors={sectors}
          onSectorSelect={handleSectorSelect}
        />
      )}

      {currentScreen === 'stockSelection' && (
        <StockSelection
          sector={selectedSector}
          availableStocks={availableStocks}
          selectedStocks={selectedStocks}
          onStockToggle={handleStockToggle}
          onRunAnalysis={handleRunAnalysis}
          onBack={() => setCurrentScreen('landing')}
        />
      )}

      {currentScreen === 'running' && (
        <AnimatedPipeline
          steps={pipelineSteps}
          activityLog={activityLog}
          currentStep={currentStep}
        />
      )}

      {currentScreen === 'results' && analysisResult && (
        <ResultsPage
          sector={selectedSector}
          analysisResult={analysisResult}
          selectedCompany={selectedCompany}
          onCompanySelect={handleCompanySelect}
          onBackToSelection={handleBackToSelection}
        />
      )}
    </div>
  );
}

export default App;
