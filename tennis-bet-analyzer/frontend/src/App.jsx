import React, { useState } from 'react';
import PropInput from './components/PropInput';
import ResearchProgress from './components/ResearchProgress';
import EvaluationCard from './components/EvaluationCard';
import ParlayBuilder from './components/ParlayBuilder';
import './App.css'; // Just keeping it for basic Vite scaffolding if needed, but styling is in index.css

// Mock Data to simulate Python Backend response
const MOCK_RESULTS = {
  evaluations: [
    {
      raw_text: "Naomi Osaka Aces Over 8.5",
      true_probability: 0.65,
      edge_pct: 12.5,
      rating: "STRONG",
      notes: "Osaka is in great form on grass, reaching her first SF on the surface since 2018. Her serve has been a weapon, hitting 7 aces in both the R16 and QF."
    },
    {
      raw_text: "Carlos Alcaraz Games Won Over 12.5",
      true_probability: 0.58,
      edge_pct: 4.2,
      rating: "MODERATE",
      notes: "Alcaraz is performing consistently, but his opponent is a strong returner. The edge is positive but not overwhelming."
    },
    {
      raw_text: "Jannik Sinner Double Faults Over 3.5",
      true_probability: 0.42,
      edge_pct: -8.1,
      rating: "FADE",
      notes: "Sinner's second serve has been extremely reliable this tournament. He hasn't exceeded 2 double faults in his last 4 matches."
    }
  ],
  parlays: {
    "2_pick": [
      {
        ev_per_dollar: 0.22,
        stake: 5.0,
        potential_payout: 15.0,
        combined_probability: 0.377,
        legs: [
          { prop: "Naomi Osaka Aces Over 8.5", true_probability: 0.65 },
          { prop: "Carlos Alcaraz Games Won Over 12.5", true_probability: 0.58 }
        ]
      }
    ],
    "3_pick": []
  },
  bankroll: 20.0
};

function App() {
  const [propsList, setPropsList] = useState([]);
  const [isResearching, setIsResearching] = useState(false);
  const [results, setResults] = useState(null);

  const handleAnalyze = (props) => {
    setPropsList(props);
    setResults(null);
    setIsResearching(true);
  };

  const handleResearchComplete = () => {
    setIsResearching(false);
    // In the future, this is where we actually display the results from the backend.
    // For now, we just use MOCK_RESULTS.
    setResults(MOCK_RESULTS);
  };

  const handleReset = () => {
    setPropsList([]);
    setResults(null);
    setIsResearching(false);
  };

  return (
    <div className="container" style={{ paddingTop: '3rem', paddingBottom: '3rem' }}>
      <header style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', background: 'linear-gradient(to right, #fff, #94a3b8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          Tennis Prop Analyzer
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>
          AI-Powered Edge Evaluation & Parlay Builder
        </p>
      </header>

      {!isResearching && !results && (
        <PropInput onAnalyze={handleAnalyze} />
      )}

      {isResearching && (
        <ResearchProgress propsList={propsList} onComplete={handleResearchComplete} />
      )}

      {results && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
            <h2 style={{ fontSize: '1.5rem', margin: 0 }}>Analysis Complete</h2>
            <button className="btn" style={{ backgroundColor: 'var(--bg-surface-elevated)', color: 'var(--text-primary)', border: '1px solid var(--border-subtle)' }} onClick={handleReset}>
              Analyze New Props
            </button>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '2rem' }}>
            <div>
              <h3 style={{ color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '1rem', fontSize: '0.9rem' }}>
                Prop Evaluations
              </h3>
              {results.evaluations.map((evalItem, idx) => (
                <EvaluationCard key={idx} evaluation={evalItem} delay={idx * 100} />
              ))}
            </div>

            <ParlayBuilder parlays={results.parlays} bankroll={results.bankroll} />
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
