# Technical Debt

## Known Issues
- `src/gui/main_window.py` is large +700 lines. Consider splitting into components.
- Hardcoded paths in some scripts (now fixed/checked).
- `dev_run.py` handles dependency installation manually; could rely more on `requirements.txt` with consistent venv.

## Future Refactoring
- Implement fully modular architecture (Controllers vs Views).
