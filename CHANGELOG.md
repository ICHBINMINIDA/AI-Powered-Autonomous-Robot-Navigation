# Changelog

All notable repository-level changes are documented here.

## [Unreleased]

### Planned

- Add real demo GIF and video link
- Add selected screenshots from a physical robot run
- Revalidate the refactored application on the target robot
- Consider YAML or environment-based runtime configuration

## [0.3.0] - Sprint 3

### Added

- Final recruiter-facing README aligned with the refactored architecture
- Detailed architecture and runtime sequence documentation
- Code overview and module responsibility guide
- Expanded setup and troubleshooting documentation
- Demo media recording and privacy guide
- Security policy
- GitHub issue and pull-request templates
- Changelog

### Changed

- Updated repository tree, project status, testing section, and design documentation to match Sprint 2
- Removed outdated statements that search, tracking, visualization, and tests were still planned

## [0.2.0] - Sprint 2

### Added

- `RobotController` orchestration layer
- `Navigator`, `SearchController`, and `TrackingController`
- `TargetObservation`, `MotionCommand`, and `SearchPhase` models
- Dedicated `Visualizer`
- Navigation unit tests
- Development requirements

### Changed

- Reduced `main.py` to application startup and shutdown concerns
- Separated deterministic navigation logic from ROS 2 publishing

## [0.1.0] - Sprint 1

### Added

- Initial modular project structure
- Central configuration and state enum
- Dedicated voice, LLM, vision, and ROS 2 modules
- Base README, setup, architecture, and troubleshooting documents
