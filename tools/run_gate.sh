#!/bin/sh
# Release gate for this project. Exempts folders whose text legitimately contains
# the gate's trigger words: the build and gate scripts themselves, the map
# template, the vendored map libraries, and CDC's pages saved unchanged.
cd "$(dirname "$0")/.." && python3 tools/publish_gate.py . \
  --allow-draft-in code/ tools/ site_src/ docs/vendor/ data/raw/ docs/GLOSSARY.md docs/VERIFY_CHECKLIST.md docs/PUBLISH_GUIDE.md
