# Copilot SDK Setup & Configuration Guide

## Issue Fixed
The application was trying to use an invalid OpenAI API key (`sk-your-api-key-here`) from the `.env` file, causing authentication errors. The system now automatically detects invalid/placeholder API keys and falls back to the GitHub Copilot SDK for LLM calls.

## Changes Made

### 1. Enhanced LLM Client (`src/utils/llm_client.py`)

#### New Feature: Automatic Provider Detection
- **`_is_valid_openai_key()`**: Validates OpenAI API keys
  - Rejects placeholder patterns: `sk-your`, `your-api-key`, etc.
  - Requires valid format: `sk-` prefix + 20+ characters
  - Returns `True` only for real-looking keys

#### Updated Provider Selection Logic
1. **Priority Order** (for demo purposes):
   - If explicit provider forced: use that
   - If valid OpenAI key detected: use OpenAI
   - If Copilot token available: use Copilot SDK (default)
   - Otherwise: raise error

2. **Before**: Checked if API key was non-empty
3. **After**: Validates API key format, detects placeholders

#### Temperature Settings by Provider
- **OpenAI**: Uses `openai_temperature` (typically 0.7)
- **Copilot SDK**: Uses lower `copilot_temperature` (typically 0.2 for consistency)

### 2. Model Updates (`src/core/models.py`)
- Updated `DreamAnalysisResult` to accept `Union[SpecificOutput, FallbackAgentOutput]`
- Allows agents to fail gracefully without validation errors
- Property `overall_feasibility()` handles both success and fallback cases

## How It Works Now

```
LLMClient Initialization
├─ Checks if OPENAI_API_KEY is valid
│  ├─ If valid → Use OpenAI
│  └─ If invalid/placeholder → Continue
├─ Checks if GITHUB_TOKEN or ALTERNATE_GITHUB_TOKEN exists
│  └─ If exists → Use Copilot SDK ✅
└─ If neither → Raise error
```

## Configuration

### Current Setup (`.env`)
```bash
# This is a placeholder - will auto-fallback to Copilot SDK
OPENAI_API_KEY=sk-your-api-key-here

# For real OpenAI use, set a valid key:
# OPENAI_API_KEY=sk-proj-xxxxxxxxxxxx...
```

### GitHub Token Setup (for Copilot SDK)
Set one of these environment variables:
```bash
# Recommended
export ALTERNATE_GITHUB_TOKEN="ghp_xxxxxxxxxxxx..."

# Or use
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx..."
```

## Testing

### Verify Provider Selection
```bash
cd /workspaces/CreativeApp
source .venv/bin/activate

python -c "
from src.core.config import get_settings
from src.utils.llm_client import LLMClient

settings = get_settings()
client = LLMClient(settings)
print(f'Provider: {client.provider}')  # Should print 'copilot'
"
```

### Test Full Orchestrator
```bash
python src/ui/app.py
# Open http://localhost:7860
# Enter dream details and click "Analyze"
```

## Key Features

✅ **Automatic Fallback**: No manual provider selection needed  
✅ **Placeholder Detection**: Rejects dummy API keys  
✅ **Graceful Degradation**: Agents return `FallbackAgentOutput` if LLM fails  
✅ **Type-Safe**: Uses Pydantic Union types for both cases  
✅ **Copilot SDK Priority**: Uses Copilot by default for demo purposes  
✅ **OpenAI Support**: Can still use real OpenAI keys if provided  

## API Key Validation Examples

| API Key | Detected As | Provider |
|---------|------------|----------|
| `sk-your-api-key-here` | Invalid (placeholder) | Copilot SDK |
| `sk-test-key` | Invalid (placeholder) | Copilot SDK |
| `` (empty) | Invalid | Copilot SDK |
| `sk-proj-abc...` (24+ chars) | Valid | OpenAI |

## Troubleshooting

### "No LLM provider configured" Error
Make sure at least one is set:
- Set a valid `OPENAI_API_KEY` (not a placeholder), OR
- Set `GITHUB_TOKEN` or `ALTERNATE_GITHUB_TOKEN`

### "Copilot SDK not installed"
```bash
pip install github-copilot-sdk
```

### Still using OpenAI with placeholder key?
1. Check `.env` - remove `OPENAI_API_KEY` or set it to empty
2. Set `GITHUB_TOKEN` in environment
3. Restart the application

## Next Steps

1. **Add Real OpenAI Key** (Optional)
   - Get key from https://platform.openai.com/api-keys
   - Update `.env`: `OPENAI_API_KEY=sk-proj-...`

2. **Set GitHub Token** (For Copilot SDK)
   - Get from https://github.com/settings/tokens
   - Export: `export GITHUB_TOKEN="ghp_..."`

3. **Deploy**
   - Current setup works out-of-box with Copilot SDK
   - No changes needed for production demo
