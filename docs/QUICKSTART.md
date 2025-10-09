# Business Agent - Quick Start Guide

Get your AI business agent running in 5 minutes!

## Installation

```bash
cd /Users/reidchatham/Developer/business-agent

# Run automated setup
chmod +x setup.sh
./setup.sh
```

Or manually:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Initialize database
python scripts/init_db.py
```

## Quick Test

```bash
# Activate virtual environment
source venv/bin/activate

# Test morning briefing
python scripts/morning_brief.py
```

## Your First Goal

```bash
# Create a goal (this will be used by Claude to break down into tasks)
python scripts/agent_cli.py goal add "Launch MVP" -h quarterly -t 2025-12-31

# Let AI break it down into actionable tasks
python scripts/agent_cli.py goal list  # Get the goal ID
python scripts/agent_cli.py goal breakdown 1  # Replace 1 with your goal ID
```

## View Your Tasks

```bash
python scripts/agent_cli.py task list
```

## Start Automation

```bash
# This will run:
# - Morning briefings at 8 AM (Mon-Fri)
# - Evening reviews at 6 PM (Mon-Fri)
# - Weekly reviews at 7 PM (Sundays)

python main.py
```

Keep this terminal running or use `nohup python main.py &` to run in background.

## Essential Commands

### Tasks
```bash
# Add task
python scripts/agent_cli.py task add "Task title" -p 1 -h 3 -c development

# Complete task
python scripts/agent_cli.py task complete 5

# List tasks
python scripts/agent_cli.py task list
```

### Research
```bash
# Research a topic
python scripts/agent_cli.py research topic "SaaS pricing strategies"

# Competitor analysis
python scripts/agent_cli.py research competitors "AI automation" "business agent"
```

### Stats
```bash
python scripts/agent_cli.py stats
```

## Troubleshooting

### API Key Issues
- Make sure `.env` file exists in project root
- Check that `ANTHROPIC_API_KEY` is set correctly
- Get your key from: https://console.anthropic.com/

### Virtual Environment
Always activate before running:
```bash
source venv/bin/activate
```

### Database Issues
If you get database errors:
```bash
rm data/tasks.db
python scripts/init_db.py
```

## Next Steps

1. Fill out `templates/business_plan_template.yaml` with your business details
2. Create your goal hierarchy
3. Use AI to break down goals
4. Run the agent for 1 week to build the habit

## Pro Tips

✨ **Let AI do the work** - Use goal breakdown to generate tasks automatically

🎯 **Be specific** - Better goals = better task breakdowns

📝 **Daily reflection** - Evening reviews take 2 minutes but provide huge value

🔍 **Research first** - Use the research agent before making decisions

---

**Ready to start? Run your first morning briefing! 🚀**
