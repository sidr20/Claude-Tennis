import React, { useState } from 'react';

export default function PropInput({ onAnalyze }) {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim()) {
      onAnalyze(input.split('\n').filter(line => line.trim() !== ''));
    }
  };

  return (
    <div className="glass-panel animate-slide-up" style={{ padding: '2rem', marginBottom: '2rem' }}>
      <h2 style={{ marginBottom: '0.5rem' }}>Enter Your Props</h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
        Paste your PrizePicks tennis props below, one per line.
      </p>
      
      <form onSubmit={handleSubmit}>
        <textarea
          className="premium-input"
          rows="5"
          placeholder="e.g. Carlos Alcaraz Aces Over 8.5&#10;Jannik Sinner Games Won 12.5"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          style={{ marginBottom: '1.5rem' }}
        ></textarea>
        
        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <button type="submit" className="btn btn-primary" disabled={!input.trim()}>
            Analyze Bets
            <svg style={{ marginLeft: '0.5rem', width: '18px', height: '18px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
          </button>
        </div>
      </form>
    </div>
  );
}
