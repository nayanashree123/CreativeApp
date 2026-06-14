# CreativeApp: AI-Powered Dream & Idea Analysis System

Transform your business ideas into actionable insights using 10 specialized AI agents and semantic knowledge retrieval.

![CreativeApp](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Gradio](https://img.shields.io/badge/Gradio-4.0+-blue)
![Copilot](https://img.shields.io/badge/Copilot-gpt--5mini-blue)

<video controls src="AI Dream agent.mp4" title="Title"></video>
---

## 🚀 Quick Start

### Start the Web Interface (30 seconds)

```bash
# 1. Navigate to project
cd /workspaces/CreativeApp

# 2. Activate environment
source venv/bin/activate

# 3. Run the app
python src/ui/app.py
```
---

## 📊 Features

### 10 Specialized AI Agents
Analyze your idea from 10 different expert perspectives:

1. **Dream Understanding** - Parse and structure your idea
2. **Market Analysis** - Assess market opportunity
3. **Resource Analysis** - Estimate budget and team needs
4. **Risk Assessment** - Identify and evaluate risks
5. **Technology Analysis** - Recommend tech stack
6. **Innovation Analysis** - Score novelty and differentiation
7. **Execution Planning** - Define MVP and phases
8. **Reality Synthesis** - Integrate all analyses
9. **Decision Making** - Final go/no-go recommendation
10. **Roadmap Generation** - Create 6-month execution plan

### Knowledge Base
- 18 indexed documents
- 6 startup patterns
- 6 business models  
- 6 case studies
- Semantic search with FAISS

### Web Interface
- 📝 Dream input panel
- 💡 Color-coded decision card
- 📊 6-axis Dream DNA radar chart
- 🤖 Agent analysis table
- 📅 6-month roadmap timeline
- 💾 JSON export
- 🔄 What if simulator
- 📋 Analysis history

---

## 📖 Documentation

### Getting Started
- [QUICK_START_UI.md](QUICK_START_UI.md) - How to use the web interface

### Technical Guides
- [ARCHITECTURE_MASTER.md](docs/ARCHITECTURE_MASTER.md) - System architecture
- [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) - Code organization

### Development
- [IMPLEMENTATION_CHECKLIST.md](docs/IMPLEMENTATION_CHECKLIST.md) - Phase progress
---

## 🎯 How It Works

```
Your Idea
    ↓
Web Interface (localhost:7860)
    ↓
CreativeApp Backend
    ├─ RAG Knowledge Retrieval (18 documents)
    ├─ 10 AI Agents (running in parallel)
    └─ Result Aggregation
        ↓
    LLM (OpenAI gpt-4o)
        ↓
    Final Analysis
    ├─ Decision (PURSUE/PIVOT/DELAY/REJECT)
    ├─ Confidence score (0-100%)
    ├─ Feasibility score (0-100%)
    ├─ Roadmap (6 months)
    └─ Agent insights
        ↓
    Web Interface Display
```

---

## ⚡ Performance

| Metric | Value |
|--------|-------|
| Single agent | 2-5s |
| All 10 agents | 5-15s |
| Full analysis | 30-60s |
| RAG retrieval | <1s |
| UI rendering | <500ms |
| Page load | 2-3s |

---

## 🛠️ Tech Stack

### Backend
- **Language**: Python 3.12
- **LLM**: OpenAI gpt-4o
- **Async**: asyncio
- **Validation**: Pydantic v2
- **RAG**: FAISS + sentence-transformers
- **Prompts**: YAML configuration

### Frontend
- **Framework**: Gradio 4.0+
- **Charts**: Plotly
- **Styling**: Soft theme
- **Browser Support**: Chrome 120+, Firefox 121+, Safari 17+

---

## 📦 Installation

### Prerequisites
- Python 3.12+
- pip

### Setup

```bash
# Clone repository
git clone https://github.com/manu05003/CreativeApp.git
cd CreativeApp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp env.example .env
# Edit .env and add your OPENAI_API_KEY
```

---

## 🔑 Environment Variables

### Required
```
OPENAI_API_KEY=sk-...  # Your OpenAI API key
```

### Optional
```
OPENAI_MODEL=gpt-4o                 # LLM model (default: gpt-4o)
OPENAI_TEMPERATURE=0.3              # Response consistency (default: 0.3)
LOG_LEVEL=INFO                       # Logging level (default: INFO)
```

---

## 📁 Project Structure

```
CreativeApp/
├── src/
│   ├── agents/              # 10 agent classes
│   ├── core/                # Models & config
│   ├── orchestration/       # Orchestrator
│   ├── rag/                 # Knowledge base
│   ├── prompts/             # System prompts
│   ├── ui/                  # Gradio interface
│   └── utils/               # Helpers
├── tests/                   # Test suites
├── knowledge/               # Knowledge base files
├── docs/                    # Documentation
├── requirements.txt         # Dependencies
└── README.md               # This file
```

---

## 🚀 Usage Example

### Web Interface
1. Open http://localhost:7860
2. Describe your idea
3. Click "Analyze Dream"
4. View results in tabs
5. Export as JSON if needed
6. What is Simulation
---

## 🔄 Workflow

### Typical User Journey
1. **Input**: Enter business idea details
2. **Analysis**: AI agents analyze idea (30-60 seconds)
3. **Results**: View decision, radar chart, agent insights
4. **Roadmap**: Get 6-month execution plan
5. **Export**: Download analysis as JSON
6. **Action**: Use roadmap for planning

---
