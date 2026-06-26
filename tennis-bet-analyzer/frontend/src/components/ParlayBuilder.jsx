import React from 'react';

export default function ParlayBuilder({ parlays, bankroll }) {
  if (!parlays || Object.keys(parlays).length === 0) return null;

  return (
    <div className="glass-panel animate-slide-up delay-300" style={{ padding: '2rem' }}>
      <h2 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center' }}>
        <svg style={{ width: '24px', height: '24px', color: 'var(--accent-secondary)', marginRight: '0.5rem' }} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        Recommended Parlays
      </h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
        Optimized EV combinations based on a ${bankroll.toFixed(2)} bankroll.
      </p>

      {Object.entries(parlays).map(([size, combos]) => (
        <div key={size} style={{ marginBottom: '2rem' }}>
          <h3 style={{ fontSize: '1rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '1rem' }}>
            {size.replace('_pick', '')}-Pick Parlays
          </h3>
          {combos.length === 0 ? (
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>No positive EV combos found.</p>
          ) : (
            <div style={{ display: 'grid', gap: '1rem' }}>
              {combos.map((combo, idx) => (
                <div key={idx} style={{ backgroundColor: 'var(--bg-surface-elevated)', borderRadius: 'var(--radius-md)', padding: '1.5rem', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                    <div className="badge badge-strong">+{combo.ev_per_dollar * 100}% EV</div>
                    <div style={{ fontWeight: '700', color: 'var(--accent-secondary)' }}>Stake: ${combo.stake.toFixed(2)}</div>
                  </div>
                  <ul style={{ listStyleType: 'none', margin: 0, padding: 0, marginBottom: '1rem' }}>
                    {combo.legs.map((leg, i) => (
                      <li key={i} style={{ padding: '0.5rem 0', borderBottom: i < combo.legs.length - 1 ? '1px solid var(--border-subtle)' : 'none', display: 'flex', justifyContent: 'space-between' }}>
                        <span>{leg.prop}</span>
                        <span style={{ color: 'var(--text-secondary)' }}>{(leg.true_probability * 100).toFixed(1)}%</span>
                      </li>
                    ))}
                  </ul>
                  <div style={{ display: 'flex', justifyContent: 'space-between', backgroundColor: 'rgba(0,0,0,0.2)', padding: '0.75rem', borderRadius: 'var(--radius-sm)' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>Win Prob: {(combo.combined_probability * 100).toFixed(1)}%</span>
                    <span style={{ fontWeight: '700', color: 'var(--text-primary)' }}>To Win: ${combo.potential_payout.toFixed(2)}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
