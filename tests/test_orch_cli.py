"""AutoGenオーケストレーターのCLIテスト"""

import os
import subprocess
from pathlib import Path
from typing import List, Tuple

import pytest

def get_latest_output_files() -> Tuple[List[Path], List[Path]]:
    """最新の出力ファイルを取得
    
    Returns:
        (Pythonファイルのリスト, JSONファイルのリスト)のタプル
    """
    output_dir = Path("output")
    if not output_dir.exists():
        return [], []
    
    py_files = sorted(output_dir.glob("output_*.py"))
    json_files = sorted(output_dir.glob("summary_*.json"))
    
    return py_files, json_files

def test_cli_execution():
    """CLIの実行テスト"""
    # 実行前のファイル数を記録
    py_files_before, json_files_before = get_latest_output_files()
    
    # CLIを実行
    result = subprocess.run(
        ["python", "autogen_orch.py", "2乗のテーブルを出力せよ"],
        capture_output=True,
        text=True
    )
    
    # 終了コードの確認
    assert result.returncode == 0, f"CLI execution failed: {result.stderr}"
    
    # 実行後のファイル数を確認
    py_files_after, json_files_after = get_latest_output_files()
    
    # 新しいファイルが生成されたことを確認
    assert len(py_files_after) > len(py_files_before), "No new Python file was generated"
    assert len(json_files_after) > len(json_files_before), "No new JSON file was generated"
    
    # 最新のファイルの内容を確認
    latest_py = py_files_after[-1]
    latest_json = json_files_after[-1]
    
    # Pythonファイルが存在することを確認
    assert latest_py.exists(), f"Generated Python file not found: {latest_py}"
    
    # JSONファイルが存在し、有効なJSONであることを確認
    assert latest_json.exists(), f"Generated JSON file not found: {latest_json}"
    with open(latest_json) as f:
        import json
        summary = json.load(f)
        assert "files" in summary, "JSON summary missing 'files' field"
        assert "status" in summary, "JSON summary missing 'status' field"
        assert summary["status"] in ["green", "red"], "Invalid status in JSON summary" 