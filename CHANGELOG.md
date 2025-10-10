# Changelog

All notable changes to Bizy AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-10-10

### Added
- **Accurate Weekly Stats** - New `get_weekly_task_stats()` method using `completed_at` timestamps
- **Improved Velocity Calculation** - Now uses actual task completion dates instead of DailyLog
- **TDD Workflow** - Comprehensive Test-Driven Development guidelines in `.clinerules`
- **Goal Assignment** - Interactive goal selection when creating tasks
- **Test Suite** - 33 comprehensive tests covering all core functionality
- **Database Environments** - Separate test/development/production databases

### Fixed
- **Weekly Summary** - Tasks completed this week now show correctly in stats
- **Plan Show Command** - No longer crashes with KeyError on stats display
- **Velocity Display** - Shows accurate tasks/day based on completed_at timestamps
- **UTC Timezone Consistency** - Fixed date comparison issues between database and queries

### Changed
- Weekly stats now use `completed_at` instead of `DailyLog` entries
- Stats keys updated for consistency:
  - `tasks_completed_this_week` (was `total_tasks_completed`)
  - `tasks_created_this_week` (was `total_tasks_planned`)
  - `completion_rate` (was `average_completion_rate`)

### Developer Experience
- Added comprehensive TDD documentation
- Created `.clinerules` for Claude Code integration
- Updated `.claude_code.json` with development methodology
- All database operations now protect production data
- Makefile commands for common development tasks

## [1.0.2] - 2025-10-09

### Initial Release
- AI-powered goal breakdown
- Daily morning briefings
- Evening reviews
- Weekly strategic reports
- Research agent
- Task management with priorities
- CLI tool (`bizy` command)
- SQLite database
- Automated scheduling

[1.1.0]: https://github.com/reidchatham/bizy-ai/compare/v1.0.2...v1.1.0
[1.0.2]: https://github.com/reidchatham/bizy-ai/releases/tag/v1.0.2
