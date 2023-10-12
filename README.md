# pass-craft
パスワード作成ツール

## 概要

[こちらの記事](https://sekika.github.io/2017/05/09/Password/)を参考にしています。`b85encode`を使用することで、頻繁に記号を含むパスワードを生成します。

## 動作確認済み環境

- WSL2
- Visual Studio Code (VSCode) の Jupyter Interactive Window

## 依存関係

- Python3
- pandas

## 使い方

1. パスワードの生成
   `sources/make_pass.py` に保存先としてのパス（サイトごとのseed、作成日などを保持する）を記述し、実行します。

## 今後の展望

保存したseedを用いて、パスワードを再生成する機能を追加予定です。
