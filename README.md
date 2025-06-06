# AutoGen + pytest + ruff + mypy 二頭脳コードジェネレータ

ChatGPTとClaudeを並列で呼び出し、相互レビューと自己修正を行うコード生成ツールです。

## 機能

- ChatGPTとClaudeによる並列コード生成
- 相互レビューと自己修正の自動化
- テスト、リント、型チェックの自動実行
- 最終コードの自動選択と保存

## セットアップ

1. 必要なパッケージのインストール:
```bash
pip install -r requirements.txt
```

2. 環境変数の設定:
`.env`ファイルを作成し、以下の内容を設定:
```
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

## 使用方法

1. コード生成の実行:
```bash
python autogen_orch.py "2乗のテーブルを出力せよ"
```

2. 生成されたコードは`output/`ディレクトリに保存されます:
- `output_YYYYMMDD_HHMMSS.py`: 生成されたコード
- `summary_YYYYMMDD_HHMMSS.json`: 実行結果のサマリー

## テストと検証

以下のコマンドでテスト、リント、型チェックを実行:
```bash
./run_checks.sh
```

## 注意事項

- Python 3.13.1以上が必要です
- 外部依存は`requirements.txt`に記載のもののみ使用
- 生成されたコードは必ずテストと検証を実行してください

## ライセンス

MIT License 