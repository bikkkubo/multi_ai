#!/usr/bin/env bash

# エラーが発生したら即座に終了
set -euo pipefail

# 仮想環境の有効化（存在する場合）
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# テストの実行（カバレッジ付き）
echo "Running tests with coverage..."
pytest -q --cov=.

# リントの実行
echo "Running linter..."
ruff check .

# 型チェックの実行
echo "Running type checker..."
mypy --strict .

echo "All checks passed successfully!" 