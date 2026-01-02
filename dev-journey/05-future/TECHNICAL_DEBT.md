# Technical Debt

## Known Issues
- `src/gui/main_window.py` is large +700 lines. Consider splitting into components.
- ~~Hardcoded paths in some scripts~~ (Fixed).
- ~~`dev_run.py` handles dependency installation manually~~ (Fixed: now uses unified requirements.txt).

## Future Refactoring
- Implement fully modular architecture (Controllers vs Views).
