# Installing Bizy CLI Globally

## Quick Install

```bash
# 1. Clone/navigate to the repository
cd /path/to/business-agent

# 2. Install globally (editable mode)
pip install -e .

# 3. Migrate your database (one-time)
mkdir -p ~/.business-agent
cp data/tasks.db ~/.business-agent/tasks.db

# 4. Set up environment (if not already done)
cp .env.example ~/.business-agent/.env
# Edit ~/.business-agent/.env and add your ANTHROPIC_API_KEY
```

## Usage

Once installed, you can use `bizy` from **any directory**:

```bash
# Task management
bizy task list
bizy task add "New task" -d "Description" -p 1 -c development -h 2.5
bizy task complete <task_id>

# Goal management
bizy goal list
bizy goal add "My Goal" -d "Description" -h yearly -t 2026-10-06
bizy goal breakdown <goal_id>

# Research
bizy research topic "AI trends" -g "Understand market"
bizy research competitors "AI tools" "Business assistant"

# Statistics
bizy stats
```

## Database Location

The global installation uses:
- **Database**: `~/.business-agent/tasks.db`
- **Environment**: Can use `BUSINESS_AGENT_DB` env variable to override

To use a custom database location:
```bash
export BUSINESS_AGENT_DB=/custom/path/to/tasks.db
bizy task list
```

## Uninstall

```bash
pip uninstall business-agent
```

## Development Mode

The `-e` flag installs in "editable" mode, meaning changes to the code are immediately reflected without reinstalling. Perfect for development!
