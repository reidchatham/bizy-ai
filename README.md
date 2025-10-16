# Bizy AI - AI-Powered Business Planning & Execution Agent

[![PyPI version](https://badge.fury.io/py/bizy-ai.svg)](https://badge.fury.io/py/bizy-ai)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An autonomous AI agent that runs daily to help you execute your business plan, manage tasks, conduct research, and stay on track toward your goals.

## 🎯 Current Status: Phase 2 Complete! ✅

**Phase 1 Complete** ✅ - Local Python MVP with AI-powered features
**Phase 2 Complete** ✅ - Charts, PDF export, dashboard, calendar, and analytics!

---

## Quick Start

### Installation

```bash
# Install globally via pip
pip install business-agent

# Set up your API key
mkdir -p ~/.business-agent
echo "ANTHROPIC_API_KEY=your-key-here" > ~/.business-agent/.env

# Initialize database
python -c "from agent.models import init_database; init_database()"

# Use the CLI
bizy task list
bizy goal list
```

### Development Setup

```bash
# Clone the repository
git clone https://github.com/reidchatham/business-agent.git
cd business-agent

# Install in editable mode
pip install -e .

# Run setup script
./setup.sh
```

See **[INSTALL.md](docs/INSTALL.md)** for detailed installation options.

---

## Development

### Test-Driven Development (TDD)

This project follows TDD principles. All new features must:

1. **Write tests first** - Define expected behavior
2. **Run tests (they should fail)** - Red phase
3. **Implement feature** - Green phase
4. **Refactor** - Clean up code

### Running Tests

```bash
# Run all tests with coverage
make test

# Run tests in watch mode
make test-watch

# Run specific test file
pytest tests/test_tasks.py -v
```

### Database Environments

- **Production**: `~/.business-agent/tasks.db` - Your actual business data 🔒
- **Development**: `~/.business-agent/dev_tasks.db` - Safe for experimentation ⚙️
- **Test**: In-memory - Isolated, clean for each test 🧪

```bash
# Use development database
export BIZY_ENV=development
make dev

# Use production database (default)
export BIZY_ENV=production
```

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for detailed development guidelines.

---

## Features

### ✅ Phase 1 - Core AI Features (Complete)

✅ **AI-Powered Goal Breakdown** - Claude breaks big goals into 5-10 actionable tasks
✅ **Daily Morning Briefings** - Personalized insights and prioritized tasks
✅ **Evening Reviews** - Reflect with AI analysis
✅ **Weekly Strategic Reports** - Comprehensive progress analysis
✅ **Research Agent** - Market research and competitive intelligence
✅ **Task Management** - Priorities, dependencies, progress tracking
✅ **CLI Tool** - Quick command-line interactions
✅ **Automated Scheduling** - Runs briefings/reviews automatically

### ⚡ Phase 2 - Enhanced Analytics (In Progress)

✅ **Live Dashboard** - Real-time terminal UI with task/goal/stats views (`bizy dashboard`)
✅ **iCal Export** - Export tasks to .ics files for calendar import (`bizy calendar export`)
✅ **Velocity Predictions** - AI predicts goal completion dates based on historical velocity (`bizy predict goal <id>`)
✅ **Terminal Charts** - Beautiful visualizations with plotext (`bizy chart velocity|goals|categories|burndown|...`)
- Velocity trends with 7-day rolling average
- Goal progress bar charts
- Category distribution charts
- Burndown charts for sprint tracking
- Productivity heatmaps by day of week
- Priority breakdown charts
- Period comparison charts

✅ **PDF Reports** - Professional reports with ReportLab (`bizy pdf weekly|monthly|goal|...`)
- Weekly/monthly summary reports with stats tables
- Individual goal reports with task breakdowns
- All goals overview reports
- Custom date range reports
- Velocity analysis reports
- Beautiful formatting with colors and tables

✅ **Calendar View** - Interactive month/week calendar (`bizy calendar view`)
- Month view with task indicators
- Task list for selected date
- Navigation: ← → months, ↑ ↓ weeks
- Color-coded highlighting (today, selected date)
- Status and priority indicators
- Keyboard shortcuts for quick navigation

🔜 **Google Calendar Sync** - Two-way sync (coming soon)
🔜 **Email Integration** - Email briefings/reports (coming soon)

---

## 📈 Development Roadmap

The project is designed to evolve through 4 phases:

### Phase 2: Enhanced Python (Weeks 4-6) ✅ Complete!
- ✅ Live CLI dashboard with real-time updates
- ✅ Local iCal file export/import
- ✅ Velocity-based predictions and analytics
- ✅ Terminal charts with plotext
- ✅ PDF report generation
- ✅ Native CLI calendar view
- 🔜 Google Calendar integration (two-way sync) - Moved to Phase 2.5
- 🔜 Email integration (Gmail API) - Moved to Phase 2.5

### Phase 3: Web Interface (Weeks 7-10)
- FastAPI backend
- React + TypeScript frontend
- PostgreSQL database
- Real-time WebSocket updates
- Multi-device access
- User authentication

### Phase 4: Production & Scale (Weeks 11-14)
- Cloud deployment (AWS/Railway)
- Mobile apps (PWA/React Native)
- Team collaboration
- Payment integration (Stripe)
- Integration marketplace
- Advanced analytics

**See [ROADMAP.md](ROADMAP.md) for complete migration plan and technical details.**

---

## Project Structure

```
business-agent/
├── agent/                   # Core modules
│   ├── core.py             # AI agent (briefings, reviews)
│   ├── models.py           # Database schema
│   ├── tasks.py            # Task management
│   ├── planner.py          # Goal planning & AI breakdown
│   └── research.py         # Research & intelligence
│
├── scripts/                 # Automation scripts
│   ├── init_db.py          # Database setup
│   ├── morning_brief.py    # Morning briefing
│   ├── evening_review.py   # Evening review
│   ├── weekly_review.py    # Weekly report
│   └── agent_cli.py        # CLI tool
│
├── templates/               # Configuration
│   └── business_plan_template.yaml
│
├── main.py                  # Scheduler daemon
├── requirements.txt         # Python dependencies
├── setup.sh                 # Automated setup
│
└── Documentation
    ├── README.md            # This file
    ├── QUICKSTART.md        # 5-minute quick start
    ├── ROADMAP.md           # Complete development roadmap
    ├── GETTING_STARTED.md   # Development guide
    └── PROJECT_COMPLETE.md  # Setup summary
```

---

## Essential Commands

### Daily Use
```bash
# Morning briefing
bizy brief

# View live dashboard
bizy dashboard

# Complete a task
bizy task complete <ID>

# Evening review
bizy review
```

### Task Management
```bash
# Add task
bizy task add "Task title" -p 1 -h 3 -c category

# List tasks
bizy task list

# Complete task
bizy task complete <ID>
```

### Goal Management
```bash
# Add goal
bizy goal add "Goal title" -h quarterly -t 2025-12-31

# List goals
bizy goal list

# AI breakdown (creates tasks automatically)
bizy goal breakdown <ID>
```

### Analytics & Predictions
```bash
# Show statistics
bizy stats

# Predict goal completion
bizy predict goal <ID>

# Show all predictions
bizy predict all

# Calculate required velocity
bizy predict required <ID>
```

### Charts & Visualizations
```bash
# Velocity trend chart
bizy chart velocity --days 30

# Goal progress charts
bizy chart goals

# Burndown chart for goal
bizy chart burndown <goal_id>

# Category distribution
bizy chart categories --days 30

# Productivity heatmap
bizy chart productivity --days 30

# Priority breakdown
bizy chart priorities --days 30

# Period comparison
bizy chart comparison --days 7
```

### PDF Reports
```bash
# Weekly report
bizy pdf weekly

# Monthly report
bizy pdf monthly

# Goal report
bizy pdf goal <ID>

# All goals report
bizy pdf all-goals

# Velocity analysis
bizy pdf velocity --days 30

# Custom date range
bizy pdf daterange 2025-01-01 2025-01-31
```

### Calendar Integration
```bash
# Launch interactive calendar view
bizy calendar view

# Export tasks to iCal
bizy calendar export --filter pending

# Export single task
bizy calendar export-task <ID>

# Show calendar directory
bizy calendar path
```

### Research
```bash
# Research topic
bizy research topic "market trends"

# Competitor analysis
bizy research competitors "domain" "offering"
```

### Automation
```bash
# Start scheduler (runs morning/evening/weekly automatically)
python main.py
```

---

## Technology Stack

### Phase 1 (Current)
- **Python 3.8+**
- **Claude (Anthropic API)** - AI intelligence
- **SQLAlchemy + SQLite** - Database
- **Rich** - Beautiful terminal UI
- **Click** - CLI framework
- **Schedule** - Task automation

### Phase 2 (Planned)
- **Textual** - Advanced TUI
- **Google Calendar API** - Calendar sync
- **Gmail API** - Email integration
- **Plotext** - Terminal charts
- **ReportLab** - PDF generation

### Phase 3 (Planned)
- **FastAPI** - Backend framework
- **PostgreSQL** - Production database
- **React + TypeScript** - Frontend
- **TailwindCSS** - Styling
- **WebSockets** - Real-time updates

### Phase 4 (Planned)
- **AWS/Railway** - Cloud hosting
- **React Native/PWA** - Mobile apps
- **Stripe** - Payments
- **Redis** - Caching
- **Celery** - Background jobs

---

## Development with Claude Code

This project is configured for Claude Code development:

```bash
# The project includes:
.claude_code.json          # Claude Code workspace config
GETTING_STARTED.md         # Development guide
ROADMAP.md                 # Migration path details
```

Open this directory in Claude Code to start developing with AI assistance!

---

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[ROADMAP.md](ROADMAP.md)** - Complete development roadmap with migration plans
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Development guide for Claude Code
- **[PROJECT_COMPLETE.md](PROJECT_COMPLETE.md)** - Setup summary and status
- **[templates/business_plan_template.yaml](templates/business_plan_template.yaml)** - Business plan with roadmap

---

## Key Benefits

✅ **Never forget important tasks** - AI breaks down goals automatically  
✅ **Stay on track daily** - Morning briefings keep you focused  
✅ **Learn from patterns** - Evening reviews capture insights  
✅ **Make informed decisions** - Research agent gathers intelligence  
✅ **Adapt your strategy** - Weekly reviews suggest improvements  
✅ **Build momentum** - Daily habit creates consistent progress  

---

## Examples

### Create Your First Goal
```bash
# 1. Create a quarterly goal
python scripts/agent_cli.py goal add "Launch MVP Product" \
  -h quarterly \
  -t 2025-06-30

# 2. Let AI break it down into tasks
python scripts/agent_cli.py goal breakdown 1

# Output: Claude creates 5-10 actionable tasks like:
#   - Design database schema (3h, priority 1)
#   - Implement user authentication (6h, priority 1)
#   - Build frontend UI (16h, priority 2)
#   - etc.

# 3. View your tasks
python scripts/agent_cli.py task list

# 4. Get your morning briefing
python scripts/morning_brief.py
```

---

## How It Works

```
1. YOU define goals
   ↓
2. AI breaks down goals into tasks
   ↓
3. Morning briefing prioritizes today's tasks
   ↓
4. YOU work on tasks throughout the day
   ↓
5. Evening review captures learnings
   ↓
6. AI analyzes patterns and suggests improvements
   ↓
7. Weekly review provides strategic insights
   ↓
8. Cycle repeats, continuously improving
```

---

## Troubleshooting

### API Key Issues
```bash
# Check .env file exists
ls -la .env

# Verify key is set
cat .env | grep ANTHROPIC_API_KEY
```

### Virtual Environment
```bash
# Always activate first
source venv/bin/activate

# Check Python version
python --version  # Should be 3.8+
```

### Database Issues
```bash
# Reset database
rm data/tasks.db
python scripts/init_db.py
```

### Permission Issues
```bash
# Make scripts executable
chmod +x setup.sh main.py scripts/*.py
```

---

## Cost Estimate

Based on typical usage with Claude Sonnet:

- Morning briefing: ~1,000 tokens (~$0.003)
- Evening review: ~1,500 tokens (~$0.005)
- Weekly review: ~3,000 tokens (~$0.009)
- Goal breakdown: ~2,000 tokens per goal (~$0.006)
- Research: ~3,000-5,000 tokens per query (~$0.009-0.015)

**Monthly estimate**: $5-15 depending on usage

---

## Contributing to This Project

This is a personal business tool, but if you're building something similar:

1. Fork the repository
2. Check the [ROADMAP.md](ROADMAP.md) for upcoming features
3. Build Phase 2 features
4. Share your improvements!

---

## Roadmap Highlights

### 🔜 Next Up: Phase 2 (Weeks 4-6)

**Top priorities:**
1. **Live Dashboard** - Real-time task updates in terminal
2. **Calendar Integration** - Sync with Google Calendar
3. **Velocity Predictions** - AI predicts completion dates
4. **Email Integration** - Daily briefings via email

**Timeline:** 3 weeks  
**Start Date:** This week!

See [ROADMAP.md](ROADMAP.md) for detailed implementation plans.

---

## Requirements

- Python 3.8 or higher
- Anthropic API access (Claude)
- ~50MB disk space
- Works on: macOS, Linux, Windows

---

## License

MIT License - feel free to use and modify for your business.

---

## Support

- 📖 **Documentation**: Check the docs in this directory
- 🐛 **Issues**: Check error logs in `data/logs/`
- 💬 **Questions**: Review `GETTING_STARTED.md` and `ROADMAP.md`
- 🚀 **Updates**: Follow the roadmap for upcoming features

---

## Next Steps

### If You're Just Getting Started:
1. Run `./setup.sh` to set up the environment
2. Add your Anthropic API key to `.env`
3. Run `python scripts/morning_brief.py` to test
4. Create your first goal and let AI break it down
5. Start using daily for one week

### If You Want to Develop:
1. Review [ROADMAP.md](ROADMAP.md) for migration path
2. Check [GETTING_STARTED.md](GETTING_STARTED.md) for dev guide
3. Open in Claude Code for AI-assisted development
4. Start building Phase 2 features
5. Test with beta users

### If You Want to Understand the Vision:
1. Read [templates/business_plan_template.yaml](templates/business_plan_template.yaml)
2. Review the 4-phase roadmap
3. Understand the migration from Python → Web → Production
4. See how each phase builds on the previous

---

**Ready to execute your business plan? Let's go! 🚀**

Built with ❤️ using Claude (Anthropic)
