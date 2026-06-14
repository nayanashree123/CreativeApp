# Data Flow & API Specifications

## End-to-End Data Flow

### Phase 1: Dream Input & Parsing
```
User Input (Text)
    ↓
[Gradio Input Validation]
    ↓
DreamProfile (Pydantic Model)
    ↓
Dream Understanding Agent
    ↓
EnrichedDreamProfile
    ├─ dream_type
    ├─ industry
    ├─ complexity_level
    ├─ timeline
    ├─ budget_range
    ├─ assumptions
    └─ constraints
```

### Phase 2: Parallel Analyzer Execution
```
EnrichedDreamProfile
    │
    ├─→ [RAG Retriever] → Context_Market → [Market Agent]
    ├─→ [RAG Retriever] → Context_Resource → [Resource Agent]
    ├─→ [RAG Retriever] → Context_Risk → [Risk Agent]
    ├─→ [RAG Retriever] → Context_Tech → [Technology Agent]
    ├─→ [RAG Retriever] → Context_Innovation → [Innovation Agent]
    └─→ [RAG Retriever] → Context_Execution → [Execution Agent]
    
    All execute in parallel via asyncio.gather()
    
    ↓ (Wait for all to complete)
    
    AnalyzerOutputs = {
        "market": MarketAgentOutput,
        "resource": ResourceAgentOutput,
        "risk": RiskAgentOutput,
        "technology": TechnologyAgentOutput,
        "innovation": InnovationAgentOutput,
        "execution": ExecutionAgentOutput
    }
```

### Phase 3: Reality Synthesis
```
(EnrichedDreamProfile + AnalyzerOutputs)
    ↓
[Reality Agent]
    - Synthesize all outputs
    - Calculate feasibility score
    - Identify strengths/blockers
    - Detect contradictions
    ↓
RealityAssessment
    ├─ overall_feasibility_score (0.0-1.0)
    ├─ key_strengths
    ├─ major_blockers
    ├─ critical_dependencies
    └─ narrative_summary
```

### Phase 4: Decision Making
```
(EnrichedDreamProfile + RealityAssessment + AnalyzerOutputs)
    ↓
[Decision Agent]
    - Evaluate recommendation framework
    - Make PURSUE/PIVOT/DELAY/REJECT call
    - Generate confidence score
    - Suggest alternatives if needed
    ↓
FinalDecision
    ├─ recommendation (PURSUE|PIVOT|DELAY|REJECT)
    ├─ confidence (0.0-1.0)
    ├─ key_reasoning
    ├─ suggested_pivots
    └─ conditions_for_change
```

### Phase 5: Roadmap & Alternatives
```
(Decision + EnrichedDreamProfile)
    │
    ├─→ [Roadmap Agent] → Roadmap (Week 1, Month 1, 3, 6)
    │
    └─→ [Alternative Generators] → Alternatives
        ├─ Safer Version
        ├─ Faster Version
        ├─ Cheaper Version
        └─ Higher Impact Version
```

### Phase 6: UI Rendering
```
CompleteAnalysisResult
    {
        dream_profile,
        analyzer_outputs,
        reality_assessment,
        final_decision,
        roadmap,
        alternatives,
        rag_matches
    }
    ↓
[Gradio Components]
    ├─ Feasibility Gauge
    ├─ Dream DNA Radar
    ├─ Agent Voting Table
    ├─ Reasoning Cards
    ├─ Roadmap Timeline
    ├─ Alternative Cards
    ├─ Pattern Matches
    └─ What-If Simulator
    ↓
User Dashboard
```

---

## LLM API Integration Specification

### Agent Execution Pattern
```
Steps:
1. Build context (RAG + previous agents)
2. Format input message
3. Call LLM with extended thinking
4. Parse structured JSON output
5. Validate and return typed output
```

### Request/Response Format

**Agent Input Format**:
```json
{
    "dream_profile": {
        "dream_text": "Build an AI platform for healthcare diagnostics",
        "dream_type": "Startup",
        "industry": "HealthTech",
        "timeline": "12 months",
        "budget_range": "100K-500K",
        "target_audience": "Hospitals and clinics",
        "assumptions": [
            "Existing healthcare providers will adopt AI",
            "We can build MVP in 3 months"
        ],
        "constraints": [
            "Limited biomedical expertise",
            "Regulatory complexity"
        ]
    },
    "rag_context": {
        "market_patterns": [...],
        "similar_companies": [...]
    }
}
```

**Agent Output Format** (JSON String):
```json
{
    "agent_name": "market_agent",
    "confidence": 0.78,
    "reasoning": "Based on analysis...",
    "metadata": {
        "rag_sources": 3,
        "model": "gpt-4o",
        "tokens_used": 1250
    },
    "output": {
        "opportunity_score": 0.72,
        "competition_level": "High",
        "market_gaps": [...]
    }
}
```

---

## RAG Integration Specification

### Knowledge Base Structure

```python
{
    "startup_successes": [...],
    "startup_failures": [...],
    "business_models": [...],
    "technology_patterns": [...],
    "market_patterns": [...]
}
```

### Retrieval for Each Agent

**Market Agent**: Retrieve market patterns, competitor analysis templates

**Risk Agent**: Retrieve failure patterns and risk archetypes

**Execution Agent**: Retrieve execution templates and roadmap examples

---

## Orchestrator API Specification

### Main Orchestration Interface

```python
async def analyze(dream_text: str) -> DreamAnalysisResult:
    """
    Main entry point for dream analysis.
    """
    
    # Step 1: Parse dream
    dream_profile = await self.dream_agent.execute(dream_text)
    
    # Step 2: Retrieve RAG context
    rag_contexts = await self.rag_retriever.retrieve_all(dream_profile)
    
    # Step 3: Run analyzer agents in parallel
    analyzer_outputs = await self._run_analyzers(dream_profile, rag_contexts)
    
    # Step 4: Reality synthesis
    reality = await self.reality_agent.execute(
        dream_profile,
        analyzer_outputs,
        rag_contexts
    )
    
    # Step 5: Final decision
    decision = await self.decision_agent.execute(
        dream_profile,
        reality,
        analyzer_outputs
    )
    
    # Step 6: Roadmap
    roadmap = await self.roadmap_agent.execute(
        dream_profile,
        decision
    )
    
    # Step 7: Alternatives & patterns
    alternatives = await self._generate_alternatives(dream_profile, decision)
    rag_matches = await self.rag_retriever.find_similar_cases(...)
    
    # Step 8: Compile result
    return DreamAnalysisResult(...)
```

---

## Gradio UI API Specification

### Main Callback Pattern

```python
async def on_analyze(self, dream_text: str) -> Tuple:
    """Main callback for analysis."""
    try:
        result = await self.orchestrator.analyze(dream_text)
        self.current_analysis = result
        return self._format_outputs(result)
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return self._format_error(e)
```

### Output Formatting

```python
def _format_outputs(self, result: DreamAnalysisResult) -> Tuple:
    """Format analysis result for UI display."""
    return (
        self._format_status_update(result),
        self._render_feasibility_gauge(result),
        self._render_decision_card(result),
        self._render_agent_table(result),
        self._render_dream_dna(result),
        self._render_agent_cards(result),
        self._render_roadmap(result),
        self._render_alternatives(result),
        self._render_patterns(result),
    )
```

---

## Error Handling & Resilience

### Error Categories

- **LLMError**: LLM API call failed
- **RAGError**: RAG retrieval failed
- **ValidationError**: Input validation failed
- **TimeoutError**: Agent execution timeout

### Fallback Strategies

1. **LLM Failure**: Use synthetic high-confidence responses
2. **RAG Failure**: Continue with minimal context
3. **Agent Timeout**: Use partial output from completed agents
4. **API Rate Limiting**: Implement exponential backoff
5. **Network Issues**: Retry up to 3 times with timeout

---

## Performance Metrics

### Expected Metrics
- Total analysis time: 30-45 seconds
- Per-agent time: 3-8 seconds
- Total LLM tokens: 15,000-25,000
- Cost per analysis: $0.40-$0.80
