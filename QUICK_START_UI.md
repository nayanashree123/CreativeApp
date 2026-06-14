# Phase 7: UI Quick Start Guide

## Start the App (3 ways)

### Option 1: Direct Python (Recommended)
```bash
cd /workspaces/CreativeApp
source venv/bin/activate
python src/ui/app.py
```

### Option 2: Using Python Launcher
```bash
cd /workspaces/CreativeApp
python start_ui.py
```

### Option 3: Bash Script
```bash
cd /workspaces/CreativeApp
chmod +x run_ui.sh
./run_ui.sh
```

---

## Access the Interface

Once started, open your browser and go to:

**http://localhost:7860**

You should see the CreativeApp interface with:
- Dream input panel
- Analyze button
- Output tabs for results

---

## How to Use

### 1. Enter Your Idea
- **Dream Description**: Write your business idea (4 lines)
- **Project Name**: Give it a name
- **Target Market**: Who is the customer?
- **Budget Range**: Choose from 5 options
- **Timeline**: Choose from 5 options

### 2. Click Analyze
Press the "🔮 Analyze Dream" button

### 3. Wait for Results
- Analysis takes 30-60 seconds
- Status field shows progress
- Results appear in tabs

### 4. Review Outputs
- **Tab 1**: Decision & Feasibility (color-coded recommendation)
- **Tab 2**: Dream DNA Radar (6-axis visualization)
- **Tab 3**: Agent Analysis (10 agents with confidence scores)
- **Tab 4**: Roadmap (6-month execution plan)
- **Tab 5**: Export (JSON download)

### 5. View History
- Expand "Analysis History" accordion
- See last 5 analyses

---

## What's Happening Behind the Scenes

When you click Analyze:

1. **Input Validation**
   - Dream text checked for content
   - DreamProfile created

2. **RAG Retrieval**
   - Knowledge base searched
   - 3 relevant documents per agent
   - Context injected into prompts

3. **Agent Execution** (Parallel)
   - 10 agents run simultaneously
   - Each uses gpt-4o LLM
   - Results aggregated

4. **Component Generation**
   - HTML cards built
   - Charts rendered
   - Tables formatted

5. **Display Update**
   - Results populate tabs
   - History updated
   - Status shows completion

---

## Troubleshooting

### App Won't Start

**Error**: `ModuleNotFoundError: No module named 'src'`
- **Fix**: Make sure you're in `/workspaces/CreativeApp` directory
- Run: `cd /workspaces/CreativeApp && python src/ui/app.py`

**Error**: `Port 7860 already in use`
- **Fix**: Edit `src/ui/app.py` and change port number
- Look for: `server_port=7860`
- Change to: `server_port=7861`

### App Starts But No Results

**Issue**: Analysis runs but no output appears
- **Cause**: Missing OPENAI_API_KEY
- **Fix**: Set environment variable:
  ```bash
  export OPENAI_API_KEY="sk-your-key-here"
  ```
- Or add to `.env` file

### Browser Can't Connect

**Issue**: http://localhost:7860 won't load
- **Check**: App is running (should see "Running on local URL" in terminal)
- **Try**: 
  - Refresh browser (Ctrl+R or Cmd+R)
  - Try different browser
  - Check port is not blocked

### Analysis Takes Too Long

**Expected**: 30-60 seconds is normal
- First run downloads models (slower)
- Subsequent runs are faster
- 10 agents running in parallel
- Each calls gpt-4o API

---

## Environment Variables

### Required (for full functionality)
```bash
OPENAI_API_KEY=sk-...        # Your OpenAI API key
```

### Optional
```bash
OPENAI_MODEL=gpt-4o           # Default model
OPENAI_TEMPERATURE=0.3        # Response consistency
LOG_LEVEL=INFO                # Logging level (DEBUG, INFO, WARNING)
```

### Set Variables

**Bash/Linux/Mac:**
```bash
export OPENAI_API_KEY="sk-..."
python src/ui/app.py
```

**Or use .env file:**
```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
LOG_LEVEL=INFO
```

---

## Features Explained

### Decision Card (Tab 1)
- **Color-coded recommendation**:
  - 🟢 PURSUE - Go ahead!
  - 🟠 PIVOT - Change approach
  - 🔵 DELAY - Wait for timing
  - 🔴 REJECT - Not recommended
- **Confidence**: 0-100% certainty
- **Feasibility**: 0-100% doable
- **Key Actions**: What to do next

### Dream DNA Radar (Tab 2)
- **6 dimensions**:
  - Clarity: How clear is the idea?
  - Market: Market opportunity
  - Resources: Budget/team availability
  - Risk: Risk level
  - Technology: Tech feasibility
  - Innovation: Novelty factor
- **Interactive**: Hover to see values
- **Scale**: 0-100 for each dimension

### Agent Table (Tab 3)
- **10 agents**:
  1. Dream Understanding
  2. Market Analysis
  3. Resource Analysis
  4. Risk Assessment
  5. Technology Analysis
  6. Innovation Analysis
  7. Execution Planning
  8. Reality Synthesis
  9. Decision Making
  10. Roadmap Generation

- **Information**:
  - Agent name
  - Confidence (0-100%)
  - Key insight excerpt

### Roadmap (Tab 4)
- **4 phases** over 6 months:
  - Phase 1: MVP development
  - Phase 2: Alpha testing
  - Phase 3: Beta launch
  - Phase 4: Public release
- **For each phase**:
  - Duration
  - Milestones
  - Deliverables

### Export (Tab 5)
- **JSON format** with:
  - All agent outputs
  - Final decision
  - Roadmap details
  - Metadata

---

## Example Workflow

### Try This Idea:
"Build an AI-powered customer support chatbot for SMB businesses"

### Input:
- Dream: "AI chatbot that handles customer support tickets, routes complex issues to humans"
- Name: "ChatSupport Pro"
- Market: "SMB SaaS"
- Budget: "$100K-$250K"
- Timeline: "6 months"

### Expected Output:
- Decision: PURSUE (likely)
- Feasibility: 85-95%
- Key Actions: Validate demand, build MVP, find first customers
- Timeline: Realistic 6-month plan

---

## Tips & Best Practices

### Writing Good Dreams
- ✅ Be specific about the problem
- ✅ Describe the solution clearly
- ✅ Mention target users
- ❌ Don't be vague
- ❌ Don't describe 5 different ideas

### Interpreting Results
- 🎯 Multiple agents should agree (look for patterns)
- 🚨 If one agent disagrees, check their reasoning
- 📊 Radar chart shows weak spots (address low scores)
- 📅 Use roadmap as baseline (adjust as needed)

### Following Up
- Use the roadmap for planning
- Validate market assumptions first
- Address high-risk items early
- Share with your team for feedback

---

## Performance Notes

- **First load**: 2-3 seconds (models download)
- **Analysis time**: 30-60 seconds (all 10 agents)
- **UI response**: <100ms
- **Memory**: 200-300 MB
- **Browser**: Chrome 120+, Firefox 121+, Safari 17+

---

## System Architecture

```
You (Browser)
    ↓
http://localhost:7860
    ↓
Gradio Web Interface
    ↓
CreativeAppUI (Python)
    ├─ Input validation
    ├─ DreamProfile creation
    └─ Orchestrator call
        ↓
DreamAnalysisOrchestrator
    ├─ RAG retrieval (18 documents)
    ├─ 10 agents (parallel)
    ├─ LLM calls (gpt-4o)
    └─ Result aggregation
        ↓
Component Builders
    ├─ HTML generation
    ├─ Chart rendering
    └─ Table formatting
        ↓
Gradio Tabs
    └─ Display results
        ↓
You see results!
```

---

## Keyboard Shortcuts

- `Ctrl+Enter`: Submit analysis (in dream textbox)
- `Tab`: Navigate between fields
- `Escape`: Close modals
- `Ctrl+R`: Refresh page
- `F12`: Developer tools (if debugging)

---

## Support & Debugging

### Check Logs
Look at terminal output while app is running:
- INFO level: Normal operation
- WARNING level: Something unexpected
- ERROR level: Something failed

### Test Backend Directly
```bash
# Test orchestrator
python tests/test_orchestrator_structure.py

# Test RAG
python tests/test_rag_integration.py

# Test all components
python tests/test_backend_integration.py
```

### Enable Debug Mode
```bash
export LOG_LEVEL=DEBUG
python src/ui/app.py
```

---

## What's Next

- **Phase 8**: Add what-if simulator
- **Phase 9**: Deploy to cloud
- **Phase 10**: Add team collaboration

---

## Quick Reference

| What | Command |
|------|---------|
| Start app | `python src/ui/app.py` |
| Stop app | `Ctrl+C` |
| Access | http://localhost:7860 |
| Change port | Edit `src/ui/app.py` line ~442 |
| Set API key | `export OPENAI_API_KEY=sk-...` |
| View logs | Check terminal output |
| Run tests | `python tests/test_*.py` |
| View source | `src/ui/app.py` (800+ lines) |

---

**Ready to analyze your first idea? Start the app and begin!** 🚀
