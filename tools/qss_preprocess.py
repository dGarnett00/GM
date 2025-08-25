"""QSS preprocessor and suggestion tool

Usage:
  - To generate suggestions: python tools/qss_preprocess.py --suggest
  - To apply replacements and emit processed QSS: python tools/qss_preprocess.py --apply --outdir build/styles

This tool scans QSS files under gui/styles/, finds hex color literals (#RRGGBB),
suggests variable names, and can apply replacements using a mapping file
or the automatically suggested mapping.
"""
from __future__ import annotations
import re
import os
import argparse
from collections import defaultdict

QSS_DIR = os.path.join('gui', 'styles')
HEX_RE = re.compile(r"#([0-9a-fA-F]{6})")


def find_hex_colors():
    hits = defaultdict(lambda: set())
    for root, _, files in os.walk(QSS_DIR):
        for fn in files:
            if not fn.lower().endswith('.qss'):
                continue
            path = os.path.join(root, fn)
            with open(path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f, 1):
                    for m in HEX_RE.finditer(line):
                        hexv = '#' + m.group(1).lower()
                        rel = os.path.relpath(path)
                        hits[hexv].add((rel, i, line.strip()))
    return hits


def suggest_names(hits):
    # Heuristic mapping: map common hex to theme keys if present, else generate names
    suggestions = {}
    # seed common mappings
    common = {
        '#2a6fdb': 'PRIMARY',
        '#1b59c3': 'PRIMARY_DARK',
        '#3b83f0': 'PRIMARY_HOVER',
        '#1d4fb3': 'PRIMARY_PRESSED',
        '#0f1724': 'BG0',
        '#16324f': 'BG1',
        '#e6eef8': 'TEXT',
        '#ffffff': 'TITLE',
        '#ff6b6b': 'ACCENT',
        '#0f0f12': 'PBP_BG',
        '#121629': 'PANE_BG',
        '#16161f': 'TS_BG'
    }
    for h in sorted(hits.keys()):
        if h in common:
            suggestions[h] = common[h]
        else:
            # generate a name like COLOR_<NN>
            suggestions[h] = f'COLOR_{h[1:]}'
    return suggestions


def write_suggestion_md(suggestions, hits, outpath):
    with open(outpath, 'w', encoding='utf-8') as out:
        out.write('# Suggested QSS variable replacements\n\n')
        out.write('Replace these hex values with variables in `gui/styles/theme_vars.qss` and use $KEY in QSS.\n\n')
        for h, key in suggestions.items():
            out.write(f'- {h} -> {key}\n')
            for (path, line_no, snippet) in sorted(hits[h]):
                out.write(f'  - {path}:{line_no}: {snippet}\n')
        out.write('\n')
    print('Wrote suggestions to', outpath)


def apply_replacements(suggestions, outdir):
    os.makedirs(outdir, exist_ok=True)
    for root, _, files in os.walk(QSS_DIR):
        for fn in files:
            if not fn.lower().endswith('.qss'):
                continue
            path = os.path.join(root, fn)
            rel = os.path.relpath(path, QSS_DIR)
            outpath = os.path.join(outdir, rel)
            os.makedirs(os.path.dirname(outpath), exist_ok=True)
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            # replace each hex literal with $KEY
            for h, key in suggestions.items():
                text = text.replace(h, f'${key}')
                text = text.replace(h.upper(), f'${key}')
            with open(outpath, 'w', encoding='utf-8') as outf:
                outf.write(text)
            print('Wrote', outpath)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--suggest', action='store_true')
    p.add_argument('--apply', action='store_true')
    p.add_argument('--outdir', default=os.path.join('build', 'styles'))
    p.add_argument('--md', default=os.path.join('tools', 'qss_replacements_suggested.md'))
    args = p.parse_args()

    hits = find_hex_colors()
    suggestions = suggest_names(hits)
    if args.suggest:
        write_suggestion_md(suggestions, hits, args.md)
    if args.apply:
        apply_replacements(suggestions, args.outdir)


if __name__ == '__main__':
    main()
