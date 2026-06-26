import React, { useEffect, useState } from 'react';

export default function ResearchProgress({ propsList, onComplete }) {
  const [currentPropIndex, setCurrentPropIndex] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (currentPropIndex >= propsList.length) {
      setTimeout(() => onComplete(), 500);
      return;
    }

    const timer = setInterval(() => {
      setProgress(p => {
        if (p >= 100) {
          clearInterval(timer);
          setTimeout(() => {
            setCurrentPropIndex(i => i + 1);
            setProgress(0);
          }, 400);
          return 100;
        }
        return p + 25; // simulate progress
      });
    }, 500);

    return () => clearInterval(timer);
  }, [currentPropIndex, propsList, onComplete]);

  if (currentPropIndex >= propsList.length) return null;

  return (
    <div className="glass-panel animate-fade-in" style={{ padding: '2rem', marginBottom: '2rem', textAlign: 'center' }}>
      <div style={{ marginBottom: '1rem' }}>
        <svg className="animate-pulse" style={{ width: '40px', height: '40px', color: 'var(--accent-primary)', margin: '0 auto' }} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>
      <h3 style={{ marginBottom: '0.5rem' }}>AI Agent Researching...</h3>
      <p style={{ color: 'var(--accent-primary)', fontWeight: '500', marginBottom: '1.5rem' }}>
        {propsList[currentPropIndex]}
      </p>
      
      <div style={{ width: '100%', height: '8px', backgroundColor: 'var(--bg-surface-elevated)', borderRadius: '999px', overflow: 'hidden' }}>
        <div 
          style={{ 
            height: '100%', 
            width: `${progress}%`, 
            backgroundColor: 'var(--accent-primary)',
            transition: 'width 0.3s ease-out'
          }} 
        />
      </div>
      <p style={{ color: 'var(--text-tertiary)', fontSize: '0.8rem', marginTop: '1rem' }}>
        Searching recent matches, head-to-head stats, and injury reports.
      </p>
    </div>
  );
}
