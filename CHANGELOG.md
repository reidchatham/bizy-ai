# Changelog

All notable changes to Bizy AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2025-10-11

### Fixed
- **Timestamp Consistency** - Standardized ALL timestamps on LOCAL time (was mixing UTC/local)
  - Fixed `created_at` default in models.py to use `datetime.now()` instead of `datetime.utcnow()`
  - Fixed query methods to use LOCAL time consistently
  - Removed incorrect UTC offset calculation in `get_daily_summary()`
  - Tasks now accurately appear on correct days in all reports
- **Weekly Review Stats** - Fixed 0% progress display in `bizy weekly`
  - Updated AI prompt to use correct key names from `get_weekly_task_stats()`
  - Weekly review now shows accurate completion rates and task counts
- **Velocity Consistency** - `bizy stats` now uses 7-day velocity (was 30-day)
  - Matches `bizy weekly` calculation for consistent reporting

### Added
- **Edge Case Tests** - 3 new tests for timestamp boundary conditions
  - Early morning task completion (5 AM)
  - Late night task completion (11:30 PM)
  - LOCAL time consistency verification

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

[1.1.1]: https://github.com/reidchatham/bizy-ai/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/reidchatham/bizy-ai/compare/v1.0.2...v1.1.0
[1.0.2]: https://github.com/reidchatham/bizy-ai/releases/tag/v1.0.2
