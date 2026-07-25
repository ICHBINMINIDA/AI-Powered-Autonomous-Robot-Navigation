# v1.0.0 — First Public Release

This release presents the first public portfolio version of the AI-powered autonomous robot navigation system.

## Highlights

- Wake-word activation and offline speech recognition with VOSK
- Natural-language target extraction through a locally hosted Ollama model
- Text-guided object segmentation through a SAM-compatible service
- Reactive ROS 2 search, visual alignment, approach, and stopping behavior
- Modular separation of orchestration, navigation, ROS I/O, vision, voice, LLM, and UI logic
- Unit-tested framework-independent navigation decisions
- Setup, architecture, troubleshooting, contribution, and security documentation

## Scope

The project is a working prototype validated in its original university robot environment. It uses reactive navigation and does not claim SLAM, global path planning, or complete obstacle avoidance.
