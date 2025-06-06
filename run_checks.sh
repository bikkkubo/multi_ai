#!/bin/bash

# エラーが発生したら即座に終了
set -euo pipefail

# 仮想環境の有効化（存在する場合）
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# テストの実行
echo "Running tests..."
pytest -q

# リントの実行
echo "Running linter..."
ruff .

# 型チェックの実行
echo "Running type checker..."
mypy --strict .

echo "All checks passed successfully!" 