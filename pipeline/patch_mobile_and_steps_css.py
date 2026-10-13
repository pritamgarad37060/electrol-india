import re

# 1. Update css/style.css for mobile-friendly UI, steps, matrix pills, and insights
with open('css/style.css', 'r', encoding='utf-8') as f:
    css_content = f.read()

mobile_and_step_css = """
/* ═══════════════════════════════════════════════════════════════════
   STEP-BY-STEP PROGRESSIVE CIVIC GATEWAY & MOBILE OPTIMIZATIONS
   ═══════════════════════════════════════════════════════════════════ */
.civic-step-flow-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
  flex-wrap: wrap;
}
.civic-step-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid var(--b);
  border-radius: 20px;
  padding: 4px 12px;
  font-size: 11.5px;
  color: var(--text-2);
}
.civic-step-badge.active {
  background: rgba(255, 153, 51, 0.18);
  border-color: rgba(255, 153, 51, 0.5);
  color: #ff9933;
  font-weight: 700;
}
.civic-step-badge.active-councils {
  background: rgba(56, 189, 248, 0.18);
  border-color: rgba(56, 189, 248, 0.5);
  color: #38bdf8;
  font-weight: 700;
}
.civic-step-arrow {
  color: var(--text-3);
  font-size: 12px;
}

.civic-step-card {
  background: linear-gradient(135deg, rgba(255,107,0,0.10) 0%, rgba(15,23,42,0.92) 50%, rgba(56,189,248,0.08) 100%);
  border: 1px solid rgba(255,153,51,0.35);
  border-radius: 14px;
  padding: 18px 20px;
  margin-bottom: 20px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.35);
}
.civic-step-card.councils-card {
  background: linear-gradient(135deg, rgba(56,189,248,0.12) 0%, rgba(15,23,42,0.92) 50%, rgba(19,136,8,0.08) 100%);
  border-color: rgba(56,189,248,0.35);
}

.civic-step-filters-grid {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 16px;
  align-items: flex-start;
}

/* Mayor & President Insight Cards */
.civic-insight-card {
  background: linear-gradient(135deg, rgba(255,153,51,0.10) 0%, rgba(15,23,42,0.90) 100%);
  border: 1px solid rgba(255,153,51,0.35);
  border-radius: 12px;
  padding: 18px 20px;
  margin-bottom: 18px;
}
.civic-insight-card.council-insight {
  background: linear-gradient(135deg, rgba(56,189,248,0.10) 0%, rgba(15,23,42,0.90) 100%);
  border-color: rgba(56,189,248,0.35);
}

/* Multi-member Prabhag Ward Pills */
.mycorp-matrix-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  max-height: 220px;
  overflow-y: auto;
  padding: 4px 2px;
  -webkit-overflow-scrolling: touch;
}
.mycorp-ward-pill {
  min-width: 44px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  border: 1px solid var(--b);
  background: var(--s2);
  color: var(--text);
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s ease;
  padding: 0 4px;
}
.mycorp-ward-pill:hover,
.mycorp-ward-pill:focus {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.4);
  background: var(--s3);
}

/* Mobile Responsiveness for all screens */
@media (max-width: 768px) {
  .civic-step-filters-grid {
    grid-template-columns: 1fr;
    gap: 14px;
  }
  .munc-compact-toolbar {
    flex-direction: column !important;
    align-items: stretch !important;
    gap: 10px !important;
  }
  .munc-compact-search-box {
    max-width: 100% !important;
    min-width: 100% !important;
  }
  .munc-compact-search-box input,
  #munc-search,
  #mycorp-search-input,
  #mycouncil-search-input {
    width: 100% !important;
    height: 42px !important;
    font-size: 14px !important;
  }
  .munc-compact-toolbar select,
  .munc-filter-group select {
    width: 100% !important;
    height: 40px !important;
    font-size: 13px !important;
  }
  .munc-filter-group {
    flex-direction: column !important;
    align-items: stretch !important;
    width: 100% !important;
  }
  .mycorp-cards-grid {
    grid-template-columns: 1fr !important;
  }
  .mycorp-matrix-grid {
    max-height: 180px;
    gap: 4px;
  }
  .mycorp-ward-pill {
    min-width: 38px;
    height: 30px;
    font-size: 10.5px;
  }
  .mycorp-hero {
    padding: 16px !important;
  }
  .mh-local-hero {
    padding: 16px !important;
  }
  .tab-pills {
    overflow-x: auto !important;
    flex-wrap: nowrap !important;
    -webkit-overflow-scrolling: touch !important;
    padding-bottom: 6px !important;
  }
  .tab-pill {
    flex-shrink: 0 !important;
    font-size: 12px !important;
    padding: 6px 12px !important;
  }
}
"""

if '/* STEP-BY-STEP PROGRESSIVE CIVIC GATEWAY' not in css_content:
    css_content += "\n" + mobile_and_step_css
    with open('css/style.css', 'w', encoding='utf-8') as f:
        f.write(css_content)
    print("Added mobile & step CSS to css/style.css successfully.")
else:
    print("Mobile & step CSS already present in css/style.css.")
