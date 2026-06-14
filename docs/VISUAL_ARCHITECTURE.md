# Visual Architecture Diagrams

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       DREAM-TO-REALITY AI SYSTEM                        │
│                   Multi-Agent Decision Intelligence Platform            │
└─────────────────────────────────────────────────────────────────────────┘

                                    USER
                                     ↓
                        ┌────────────────────────┐
                        │   Gradio Web Interface │
                        └────────────────────────┘
                                     ↓
                        ┌────────────────────────┐
                        │   Dream Text Input     │
                        │   (e.g., Build AI SaaS)│
                        └────────────────────────┘
                                     ↓
                    ╔═══════════════════════════════╗
                    ║  ORCHESTRATION LAYER          ║
                    ║  (Async Coordinator)          ║
                    ╚═══════════════════════════════╝
                                     ↓
                        ┌────────────────────────┐
                        │ Dream Parser Agent     │
                        │ (Structured Input)     │
                        └────────────────────────┘
                                     ↓
                   ┌──────────────────────────────────┐
                   │   RAG Retriever                  │
                   │   (Get Relevant Context)         │
                   │   - Market patterns              │
                   │   - Success/failure cases        │
                   │   - Business models              │
                   └──────────────────────────────────┘
                                     ↓
     ╔═══════════════════════════════════════════════════════════════╗
     ║              6 ANALYZER AGENTS (PARALLEL EXECUTION)           ║
     ╠═══════════════════════════════════════════════════════════════╣
     ║  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        ║
     ║  │   Market     │  │  Resource    │  │    Risk      │        ║
     ║  │   Agent      │  │   Agent      │  │   Agent      │        ║
     ║  │              │  │              │  │              │        ║
     ║  │ ✓ Opp Score  │  │ ✓ Budget     │  │ ✓ Risk Score │        ║
     ║  │ ✓ Competition│  │ ✓ Team Size  │  │ ✓ Major Risks│        ║
     ║  │ ✓ Market Gaps│  │ ✓ Skills     │  │ ✓ Mitigations│        ║
     ║  └──────────────┘  └──────────────┘  └──────────────┘        ║
     ║  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        ║
     ║  │ Technology   │  │ Innovation   │  │  Execution   │        ║
     ║  │   Agent      │  │   Agent      │  │   Agent      │        ║
     ║  │              │  │              │  │              │        ║
     ║  │ ✓ Build      │  │ ✓ Novelty    │  │ ✓ MVP Scope  │        ║
     ║  │   Feasibility│  │ ✓ Unique     │  │ ✓ Milestones │        ║
     ║  │ ✓ Tech Stack │  │ ✓ Advantage  │  │ ✓ Timeline   │        ║
     ║  └──────────────┘  └──────────────┘  └──────────────┘        ║
     ╚═══════════════════════════════════════════════════════════════╝
              All agents emit results simultaneously (~8s)
                                     ↓
                        ┌────────────────────────┐
                        │   Reality Agent        │
                        │   (Synthesizer)        │
                        │                        │
                        │ ✓ Combine all outputs  │
                        │ ✓ Identify blockers    │
                        │ ✓ Calculate feasibility│
                        │ ✓ 0-100 score         │
                        └────────────────────────┘
                                     ↓
                        ┌────────────────────────┐
                        │   Decision Agent       │
                        │   (Final Verdict)      │
                        │                        │
                        │ ✓ PURSUE              │
                        │ ✓ PIVOT               │
                        │ ✓ DELAY               │
                        │ ✓ REJECT              │
                        └────────────────────────┘
                                     ↓
        ┌────────────────────────────────────────────────────┐
        │  Roadmap Agent    │   Alternative Generator        │
        │  (Sequential)     │   (Parallel)                   │
        │                   │                                │
        │  Week 1 Plan      │  ✓ Safer Version              │
        │  Month 1 Plan     │  ✓ Faster Version             │
        │  Month 3 Plan     │  ✓ Cheaper Version            │
        │  Month 6 Plan     │  ✓ Higher-Impact Version      │
        └────────────────────────────────────────────────────┘
                                     ↓
                    ┌──────────────────────────────────┐
                    │  Complete Analysis Result         │
                    │  (All Components Combined)        │
                    └──────────────────────────────────┘
                                     ↓
                    ┌──────────────────────────────────┐
                    │  UI Rendering Layer               │
                    │  (Gradio Dashboard)              │
                    └──────────────────────────────────┘
                                     ↓
     ┌──────────────────────────────────────────────────────────┐
     │            USER SEES COMPREHENSIVE ANALYSIS             │
     │  • Feasibility Score (0-100)                            │
     │  • Dream DNA Radar Chart                                │
     │  • Agent Voting Table                                   │
     │  • Agent Reasoning Cards                                │
     │  • Risk Assessment                                      │
     │  • Roadmap Timeline                                     │
     │  • Alternative Ideas                                    │
     │  • Pattern Matches                                      │
     │  • What-If Simulator                                    │
     └──────────────────────────────────────────────────────────┘
```

---

## Execution Timeline Graph

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    EXECUTION TIMELINE (30-45 seconds)                   │
└─────────────────────────────────────────────────────────────────────────┘

Time (seconds)
0          5          10         15         20         25         30
│          │          │          │          │          │          │
├──────────┼──────────┼──────────┼──────────┼──────────┼──────────┼
│                                                                   │
├─ Parse Dream ────────┤                                          TOTAL
│  (1-2s)              │                                          TIME:
│                      │                                          30-45s
├─ RAG Retrieval ──────────────┤                                 
│  (1-3s)              │        │                                
│                      │        │
├───────────────────────────────┼────── Market Agent ────────────┤
├───────────────────────────────┼────── Resource Agent ──────────┤
├───────────────────────────────┼────── Risk Agent ──────────────┤
├───────────────────────────────┼────── Technology Agent ────────┤
├───────────────────────────────┼────── Innovation Agent ────────┤
├───────────────────────────────┼────── Execution Agent ─────────┤
│                      │        └─ 8 seconds (parallel) ──────┤│
│                      │                                        ││
│                      ├─ Reality Synthesis ────────────────────┤│
│                      │    (1-2s)                              ││
│                      │                                        ││
│                      │        ├─ Decision Making ─────────────┤│
│                      │        │  (1-2s)                       ││
│                      │        │                               ││
│                      │        │  ├─ Roadmap Gen ──┤           ││
│                      │        │  │  ├─ Alt Gen ──┤│           ││
│                      │        │  │  │ └─ Pat... ─┤│           ││
│                      │        │  │  │  (5-10s)   ││           ││
│                      │        │  │  │            ││           ││
└──────────────────────┴────────┴──┴──┴────────────┴┴───────────┴
```

---

## Knowledge Base Organization

```
knowledge/
├─ startup_successes.json (50+ entries)
├─ startup_failures.json (30+ entries)
├─ business_models.json (20+ archetypes)
├─ technology_patterns.json (30+ patterns)
├─ market_patterns.json (25+ patterns)
├─ execution_templates.json (15+ templates)
├─ funding_models.json (10+ models)
└─ industry_reports.json (10+ reports)

RETRIEVAL EXAMPLE:
Query: "Build AI startup for healthcare diagnostics"
     ↓
Embedding: [0.12, 0.45, -0.32, ...]
     ↓
FAISS similarity search (top 5)
     ↓
Results: Similar companies, patterns, and archetypes
```

This visual architecture makes the entire system immediately clear!
