#!/usr/bin/env python3
"""AutoGenオーケストレーター

ChatGPTとClaudeを並列で呼び出し、相互レビューと自己修正を行うツール。
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

import autogen
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

@dataclass
class CodeReview:
    """コードレビューの結果を保持するクラス"""
    code: str
    feedback: str
    test_status: bool
    lint_status: bool
    type_check_status: bool

class AutoGenOrchestrator:
    """AutoGenオーケストレーターのメインクラス"""
    
    def __init__(self, max_rounds: int = 3) -> None:
        """初期化
        
        Args:
            max_rounds: 最大レビューラウンド数
        """
        self.max_rounds = max_rounds
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
        # エージェントの設定
        self.config_list = [
            {
                "model": "gpt-4-turbo-preview",
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
            {
                "model": "claude-3-opus-20240229",
                "api_key": os.getenv("ANTHROPIC_API_KEY"),
            }
        ]
        
        # エージェントの初期化
        self.chatgpt = autogen.AssistantAgent(
            name="ChatGPT",
            llm_config={"config_list": [self.config_list[0]]},
            system_message="""あなたはPythonエキスパートです。PEP 8とPEP 484に従ってコードを生成してください。
生成するコードには必ず以下の関数を含めてください：
def run_task(n: int) -> List[int]:
    \"\"\"タスクを実行する関数
    
    Args:
        n: 入力値
        
    Returns:
        実行結果のリスト
    \"\"\"
    # 実装
"""
        )
        
        self.claude = autogen.AssistantAgent(
            name="Claude",
            llm_config={"config_list": [self.config_list[1]]},
            system_message="""あなたはPythonエキスパートです。PEP 8とPEP 484に従ってコードを生成してください。
生成するコードには必ず以下の関数を含めてください：
def run_task(n: int) -> List[int]:
    \"\"\"タスクを実行する関数
    
    Args:
        n: 入力値
        
    Returns:
        実行結果のリスト
    \"\"\"
    # 実装
"""
        )
        
        self.arbitrator = autogen.AssistantAgent(
            name="Arbitrator",
            llm_config={"config_list": [self.config_list[0]]},
            system_message="あなたはコードレビューの仲裁者です。最適なコードを選択してください。"
        )
        
        self.user_proxy = autogen.UserProxyAgent(
            name="User",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config={"work_dir": "workspace"},
            llm_config=False,
            system_message="タスクの実行と結果の確認を行います。"
        )

    def run_checks(self, code: str) -> str:
        """コードの検証を実行
        
        Args:
            code: 検証するコード
            
        Returns:
            失敗ログ（成功時は空文字列）
        """
        # 一時ファイルにコードを保存
        temp_file = Path("workspace/temp.py")
        temp_file.parent.mkdir(exist_ok=True)
        temp_file.write_text(code)
        
        logs = []
        
        # テストの実行
        test_result = subprocess.run(
            ["pytest", "-q", str(temp_file)],
            capture_output=True,
            text=True
        )
        if test_result.returncode != 0:
            logs.append(f"=== Test Failures ===\n{test_result.stdout}\n{test_result.stderr}")
        
        # リントの実行
        lint_result = subprocess.run(
            ["ruff", "check", str(temp_file)],
            capture_output=True,
            text=True
        )
        if lint_result.returncode != 0:
            logs.append(f"=== Lint Errors ===\n{lint_result.stdout}\n{lint_result.stderr}")
        
        # 型チェックの実行
        type_check_result = subprocess.run(
            ["mypy", "--strict", str(temp_file)],
            capture_output=True,
            text=True
        )
        if type_check_result.returncode != 0:
            logs.append(f"=== Type Check Errors ===\n{type_check_result.stdout}\n{type_check_result.stderr}")
        
        return "\n\n".join(logs) if logs else ""

    def generate_code(self, task: str) -> str:
        """コード生成を実行
        
        Args:
            task: タスクの説明
            
        Returns:
            生成されたコード
        """
        # 初期コード生成
        self.user_proxy.initiate_chat(
            self.chatgpt,
            message=f"以下のタスクを実行してください：\n{task}\n\nコードは完全な形で、importからif __name__ == '__main__'まで含めてください。"
        )
        
        chatgpt_code = self.user_proxy.last_message()["content"]
        
        self.user_proxy.initiate_chat(
            self.claude,
            message=f"以下のタスクを実行してください：\n{task}\n\nコードは完全な形で、importからif __name__ == '__main__'まで含めてください。"
        )
        
        claude_code = self.user_proxy.last_message()["content"]
        
        # レビューループ
        for round_num in range(self.max_rounds):
            # ChatGPTのコードをClaudeがレビュー
            self.user_proxy.initiate_chat(
                self.claude,
                message=f"以下のコードをレビューしてください：\n\n{chatgpt_code}"
            )
            claude_feedback = self.user_proxy.last_message()["content"]
            
            # ClaudeのコードをChatGPTがレビュー
            self.user_proxy.initiate_chat(
                self.chatgpt,
                message=f"以下のコードをレビューしてください：\n\n{claude_code}"
            )
            chatgpt_feedback = self.user_proxy.last_message()["content"]
            
            # 自己修正
            self.user_proxy.initiate_chat(
                self.chatgpt,
                message=f"以下のフィードバックに基づいてコードを修正してください：\n\n{claude_feedback}"
            )
            chatgpt_code = self.user_proxy.last_message()["content"]
            
            self.user_proxy.initiate_chat(
                self.claude,
                message=f"以下のフィードバックに基づいてコードを修正してください：\n\n{chatgpt_feedback}"
            )
            claude_code = self.user_proxy.last_message()["content"]
            
            # 検証とフィードバック
            chatgpt_log = self.run_checks(chatgpt_code)
            claude_log = self.run_checks(claude_code)
            
            # 両方のコードが合格したら終了
            if not chatgpt_log and not claude_log:
                break
            
            # 失敗ログをフィードバック
            if chatgpt_log:
                self.user_proxy.initiate_chat(
                    self.chatgpt,
                    message=f"[CHECK_FAIL]\n{chatgpt_log}\n\n上記のエラーを修正してください。"
                )
                chatgpt_code = self.user_proxy.last_message()["content"]
            
            if claude_log:
                self.user_proxy.initiate_chat(
                    self.claude,
                    message=f"[CHECK_FAIL]\n{claude_log}\n\n上記のエラーを修正してください。"
                )
                claude_code = self.user_proxy.last_message()["content"]
        
        # 最終的なコードの選択
        self.user_proxy.initiate_chat(
            self.arbitrator,
            message=f"以下の2つのコードから最適なものを選択してください：\n\nChatGPT:\n{chatgpt_code}\n\nClaude:\n{claude_code}"
        )
        
        final_code = self.user_proxy.last_message()["content"]
        
        # 結果の保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"output_{timestamp}.py"
        output_file.write_text(final_code)
        
        # サマリーの保存
        summary = {
            "files": [str(output_file)],
            "status": "green" if not self.run_checks(final_code) else "red"
        }
        summary_file = self.output_dir / f"summary_{timestamp}.json"
        summary_file.write_text(json.dumps(summary, indent=2))
        
        return final_code

def main() -> None:
    """メイン関数"""
    if len(sys.argv) != 2:
        print("Usage: python autogen_orch.py \"<task description>\"")
        sys.exit(1)
    
    task = sys.argv[1]
    orchestrator = AutoGenOrchestrator()
    orchestrator.generate_code(task)

if __name__ == "__main__":
    main() 