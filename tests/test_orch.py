"""AutoGenオーケストレーターのテスト"""

import os
import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from autogen_orch import AutoGenOrchestrator, CodeReview

@pytest.fixture
def orchestrator():
    """テスト用のオーケストレーターインスタンスを作成"""
    return AutoGenOrchestrator(max_rounds=1)

@pytest.fixture
def mock_env_vars(monkeypatch):
    """環境変数のモック"""
    monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_anthropic_key")

def test_normal_case(orchestrator, mock_env_vars):
    """正常系のテスト：フィボナッチ数列の生成"""
    with patch("subprocess.run") as mock_run:
        # テスト、リント、型チェックの結果をモック
        mock_run.return_value = MagicMock(returncode=0)
        
        # コード生成のモック
        with patch.object(orchestrator.user_proxy, "initiate_chat") as mock_chat:
            mock_chat.return_value = None
            mock_chat.side_effect = [
                {"content": "def fib(n): return n if n < 2 else fib(n-1) + fib(n-2)"},
                {"content": "def fib(n): return n if n < 2 else fib(n-1) + fib(n-2)"},
                {"content": "良いコードです"},
                {"content": "良いコードです"},
                {"content": "def fib(n): return n if n < 2 else fib(n-1) + fib(n-2)"},
                {"content": "def fib(n): return n if n < 2 else fib(n-1) + fib(n-2)"},
                {"content": "def fib(n): return n if n < 2 else fib(n-1) + fib(n-2)"}
            ]
            
            result = orchestrator.generate_code("フィボナッチ数列を生成する関数を作成せよ")
            
            assert "def fib" in result
            assert "return n if n < 2" in result

def test_error_case(orchestrator, mock_env_vars):
    """異常系のテスト：引数不足"""
    with pytest.raises(SystemExit):
        with patch.object(sys, "argv", ["autogen_orch.py"]):
            orchestrator.main()

def test_boundary_case(orchestrator, mock_env_vars):
    """境界値のテスト：空のタスク"""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        
        with patch.object(orchestrator.user_proxy, "initiate_chat") as mock_chat:
            mock_chat.return_value = None
            mock_chat.side_effect = [
                {"content": "def empty(): pass"},
                {"content": "def empty(): pass"},
                {"content": "良いコードです"},
                {"content": "良いコードです"},
                {"content": "def empty(): pass"},
                {"content": "def empty(): pass"},
                {"content": "def empty(): pass"}
            ]
            
            result = orchestrator.generate_code("")
            
            assert "def empty" in result
            assert "pass" in result 