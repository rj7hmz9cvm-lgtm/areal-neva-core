#!/bin/bash
# Паттерны хранятся отдельно чтобы скрипт не сканировал сам себя
PATTERN_FILE="/root/.areal-neva-core/.secret_patterns"

if [ ! -f "$PATTERN_FILE" ]; then
  echo "SECRET_SCAN_SKIP: pattern file not found"
  exit 0
fi

FOUND=0
while IFS= read -r line; do
  [[ "$line" =~ ^\+ ]] || continue
  while IFS= read -r pattern; do
    if echo "$line" | grep -qE "$pattern"; then
      echo "SECRET FOUND: $pattern"
      FOUND=1
    fi
  done < "$PATTERN_FILE"
done < <(git diff --cached)

[ $FOUND -eq 1 ] && echo "ABORT: секреты в коммите" && exit 1
echo "SECRET_SCAN_OK"
exit 0
