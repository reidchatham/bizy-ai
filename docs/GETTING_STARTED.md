# Getting Started with Business Agent (Claude Code)

This project is now set up for development with Claude Code!

## Quick Setup

1. **Install Dependencies**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
```

3. **Initialize Database**
```bash
python scripts/init_db.py
```

4. **Test It**
```bash
python scripts/morning_brief.py
```

## Project Structure

- `agent/` - Core modules (models, tasks, planner, core, research)
- `scripts/` - Executable scripts (morning_brief, evening_review, etc.)
- `templates/` - Configuration templates
- `main.py` - Scheduler for automation
- `data/` - Database and logs (created on first run)

## Development with Claude Code

### Common Tasks

**Run morning briefing:**
```bash
python scripts/morning_brief.py
```

**Create a new goal:**
```bash
python scripts/agent_cli.py goal add "Your goal" -h quarterly
```

**Break down goal with AI:**
```bash
python scripts/agent_cli.py goal breakdown 1
```

**View tasks:**
```bash
python scripts/agent_cli.py task list
```

**Research a topic:**
```bash
python scripts/agent_cli.py research topic "your topic"
```

### Key Files to Understand

1. **agent/models.py** - Database schema (Tasks, Goals, DailyLog, etc.)
2. **agent/planner.py** - AI-powered goal breakdown logic
3. **agent/core.py** - Main AI agent (briefings, reviews)
4. **agent/tasks.py** - Task management operations
5. **agent/research.py** - Research and intelligence gathering

### Making Changes

The codebase is modular:
- Modify `agent/core.py` to change briefing/review prompts
- Modify `agent/planner.py` to adjust goal breakdown logic
- Modify `agent/research.py` to add new research capabilities
- Add new scripts in `scripts/` for new features

### Testing Changes

```bash
# Test specific module
python -c "from agent.planner import BusinessPlanner; p = BusinessPlanner()"

# Run full workflow
python scripts/morning_brief.py
```

## Next Development Steps

Current: **Phase 1 - Python MVP** ✅

Future phases:
- Phase 2: CLI dashboard, calendar integration
- Phase 3: Web interface (FastAPI + React)
- Phase 4: Cloud deployment + mobile

## Getting Help

- Check `README.md` for full documentation
- See `QUICKSTART.md` for quick reference
- Review `PROJECT_SUMMARY.md` for architecture overview

---

**Happy coding with Claude! 🚀**
