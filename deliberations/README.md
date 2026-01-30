# Council Deliberations Archive

This directory contains the complete archive of all LLM Council deliberations. Each deliberation is stored in a structured format for future reference and analysis.

## Directory Structure

Each deliberation is saved in a timestamped directory:

```
YYYY-MM-DD-HH-MM-SS-question-slug/
├── metadata.json              # Deliberation metadata
├── question.md                # The original question
├── full-deliberation.md       # Complete deliberation in one file
├── stage1/                    # Individual model responses
│   ├── model-1.md
│   ├── model-2.md
│   ├── model-3.md
│   └── model-4.md
├── stage2/                    # Peer rankings
│   ├── rankings.json         # Machine-readable rankings
│   └── rankings.md           # Human-readable rankings
└── stage3/                   # Final answer
    └── final-answer.md       # Chairman's synthesis
```

## Metadata

Each deliberation includes:
- **Timestamp**: When the deliberation occurred
- **Models Participated**: Number and names of models
- **Chairman**: Which model synthesized the final answer
- **Web Search**: Whether real-time web search was used
- **Rankings**: How models ranked each other
- **Aggregate Rankings**: Statistical analysis of peer evaluations

## Usage

### Browse Deliberations

```bash
# List recent deliberations
python browse_deliberations.py list

# List more
python browse_deliberations.py list 20

# View a specific deliberation
python browse_deliberations.py view 2026-01-30-16-43-32-what-are-the-top-3-benefits-of-using-a-multi-model

# Search deliberations
python browse_deliberations.py search "roadmap"
python browse_deliberations.py search "API integration"
```

### In Python

```python
from backend.deliberations import list_deliberations, get_deliberation, search_deliberations

# List recent
recent = list_deliberations(limit=5)

# Get specific deliberation
delib = get_deliberation("2026-01-30-16-43-32-what-are-the-top-3-benefits-of-using-a-multi-model")

# Search
results = search_deliberations("MCP integration")
```

## Future Use Cases

This archive enables:

1. **Historical Analysis**: Track how the council's opinions evolve over time
2. **Context for Future Deliberations**: Reference past discussions on similar topics
3. **Model Performance Tracking**: Analyze which models consistently provide valuable insights
4. **Training Data**: Potential use for fine-tuning or meta-learning
5. **API/MCP Integration**: Serve past deliberations as context to other AI systems
6. **Public Knowledge Base**: Publish deliberations to GitHub Pages for public access

## Automatic Archiving

All council deliberations are automatically archived by the `run_full_council()` function. No manual intervention required.
