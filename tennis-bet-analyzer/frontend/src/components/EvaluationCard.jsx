import React from 'react';

export default function EvaluationCard({ evaluation, delay }) {
  const { raw_text, true_probability, edge_pct, rating, notes } = evaluation;
  
  const badgeClass = rating === 'STRONG' ? 'badge-strong' 
                   : rating === 'MODERATE' ? 'badge-moderate' 
                   : 'badge-fade';

  return (
    <div className={`glass-panel animate-slide-up delay-${delay}`} style={{ padding: '1.5rem', marginBottom: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
        <h3 style={{ fontSize: '1.1rem', margin: 0 }}>{raw_text}</h3>
        <span className={`badge ${badgeClass}`}>{rating}</span>
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
        <div style={{ backgroundColor: 'var(--bg-surface-elevated)', padding: '0.75rem', borderRadius: 'var(--radius-sm)' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>True Probability</div>
          <div style={{ fontSize: '1.25rem', fontWeight: '700', fontFamily: 'var(--font-display)' }}>
            {(true_probability * 100).toFixed(1)}%
          </div>
        </div>
        <div style={{ backgroundColor: 'var(--bg-surface-elevated)', padding: '0.75rem', borderRadius: 'var(--radius-sm)' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Calculated Edge</div>
          <div style={{ fontSize: '1.25rem', fontWeight: '700', fontFamily: 'var(--font-display)', color: edge_pct > 0 ? 'var(--status-strong)' : 'var(--status-fade)' }}>
            {edge_pct > 0 ? '+' : ''}{edge_pct}%
          </div>
        </div>
      </div>
      
      <div style={{ backgroundColor: 'rgba(255,255,255,0.03)', padding: '1rem', borderRadius: 'var(--radius-sm)', borderLeft: '3px solid var(--accent-primary)' }}>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', margin: 0 }}>
          <strong style={{ color: 'var(--text-primary)' }}>AI Synthesis:</strong> {notes}
        </p>
      </div>
    </div>
  );
}
