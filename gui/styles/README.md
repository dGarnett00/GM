Style system overview

- Location: gui/styles/
  - base.qss           - global baseline rules (loaded first)
  - theme_vars.qss     - simple key=value file for color and small tokens
  - windows/           - per-window QSS files (loaded after base, sorted)
  - components/        - per-component QSS files (loaded after windows, sorted)

How it works

1. At startup, main.py collects QSS files in this order:
   - base.qss
   - all files in gui/styles/windows/ (sorted)
   - all files in gui/styles/components/ (sorted)

2. main.py also loads gui/styles/theme_vars.qss and parses lines of the form:
   KEY=VALUE
   Blank lines and lines starting with # are ignored.

3. Before applying the combined stylesheet, main.py replaces occurrences of $KEY in the QSS text
   with the corresponding VALUE from theme_vars.qss. This allows simple theming without a
   full preprocessor.

Writing styles

- Prefer variables for colors and sizes that may change across themes.
  Example in a QSS file:
    QPushButton#StartButton {
      background: $PRIMARY;
      color: $TEXT;
    }

- Keep component rules scoped by objectName where possible to avoid global selectors.

Regenerating resources

- Icon and SVG resources are compiled into Python modules (rc_*.py) and committed to the repo.
- If you update SVGs, run the helper script `build_resources.bat` (Windows) to recompile resources.

Notes

- The substitution implemented in main.py is intentionally simple. It does a literal text
  replacement of $KEY with the provided value. Avoid using $ in QSS for unrelated purposes.
- For more advanced preprocessing (expressions, color functions), implement a small preprocessor
  or use a build-time tool to generate final QSS.
