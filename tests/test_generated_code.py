"""生成されたコードのテスト"""

import importlib.util
import sys
from pathlib import Path
from typing import Any, List, Optional

import pytest

def load_generated_module() -> Any:
    """最新の生成されたモジュールを読み込む
    
    Returns:
        読み込まれたモジュール
    """
    output_dir = Path("output")
    if not output_dir.exists():
        pytest.skip("No output directory found")
    
    # 最新のPythonファイルを取得
    py_files = sorted(output_dir.glob("output_*.py"))
    if not py_files:
        pytest.skip("No generated Python files found")
    
    latest_file = py_files[-1]
    
    # モジュールとして読み込む
    spec = importlib.util.spec_from_file_location("generated_code", latest_file)
    if spec is None or spec.loader is None:
        pytest.skip(f"Could not load module from {latest_file}")
    
    module = importlib.util.module_from_spec(spec)
    sys.modules["generated_code"] = module
    spec.loader.exec_module(module)
    
    return module

def test_generated_code():
    """生成されたコードの機能テスト"""
    module = load_generated_module()
    
    # 公開APIの存在確認
    assert hasattr(module, "run_task"), "Generated code missing run_task function"
    
    # 関数の実行と結果の確認
    result = module.run_task(5)
    expected = [1, 4, 9, 16, 25]
    
    assert result == expected, f"Expected {expected}, but got {result}"
    
    # エッジケースのテスト
    assert module.run_task(0) == [], "Empty table should return empty list"
    assert module.run_task(1) == [1], "Single item table should return [1]"
    
    # 負の値のテスト
    with pytest.raises(ValueError):
        module.run_task(-1) 