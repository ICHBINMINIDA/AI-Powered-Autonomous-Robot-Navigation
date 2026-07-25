# Contributing

Contributions that improve portability, testing, documentation, or safe robot behavior are welcome.

## Development setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
pytest -q
```

ROS 2 and hardware integration require an appropriate external environment.

## Design rules

- Keep `src/main.py` small.
- Keep navigation logic independent of ROS 2 where possible.
- Return `MotionCommand` values from decision modules instead of publishing directly.
- Put service and topic values in `Settings` rather than hard-coding them in controllers.
- Add or update tests when changing search, alignment, approach, or stop behavior.
- Do not claim SLAM, path planning, or complete obstacle avoidance unless those features are actually implemented and validated.
- Document any hardware assumptions and safety implications.

## Pull requests

A useful pull request should include:

- a clear description of the problem and solution;
- affected modules;
- test results;
- hardware validation notes when relevant;
- screenshots or logs only after removing private infrastructure details.

## Code style

Use descriptive names, type hints, concise docstrings, and standard Python formatting. Avoid placing unrelated responsibilities in one class.
