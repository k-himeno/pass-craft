"""パスワード生成"""
# -*- coding: utf-8 -*-

# 参考: https://sekika.github.io/2017/05/09/Password/
# 参考と異なりパスワードはパスワード管理アプリで保存する．あくまでも生成のみに用いる．

import base64
import hashlib
import re
import time

import pandas as pd

# TODO GUI使えるなら使いたい
try:
    import tkinter as tk
    from tkinter import messagebox, simpledialog

    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False


def make_password(
    master1, master2, seed="1234", plen=20, char="ans", rm_cha="", start=1, upper=False, lower=False, **kwargs
):
    """パスワードを生成する関数

    Args:
        master1 (str): マスターパスワード1
        master2 (str): マスターパスワード2
        seed (str, optional): サービスごとのパスワード. Defaults to "1234".
        plen (int, optional): パスワードの長さ． Defaults to 20.
        char (str, optional): a[アルファベット], n[数字], s[記号]の組み合わせ. Defaults to "ans".
        rm_cha (bool, optional): NG記号. Defaults to "".
        start (int, optional): パスワードの開始位置. Defaults to 1.
        upper (bool, optional): 大文字縛りがあるか. Defaults to False.
        lower (bool, optional): 小文字縛りがあるか. Defaults to False.
    """

    # 指定されたハッシュ関数を適用する。
    # https://docs.python.jp/3/library/hashlib.html

    seed_tmp = master1 + seed + master2
    h = hashlib.sha512(seed_tmp.encode("utf-8"))

    # 指定された文字の種類にしたがって、パスワードの文字列を作る。

    base = base64.b85encode(h.digest()).decode("utf-8")  # b85
    # !#$%&()*+-;<=>?@^_`{|}~ と文字数字

    if char == ("ans"):  # base85
        p = base
    elif char == ("an"):  # an: アルファベットと数字
        p = re.sub(r"[^a-zA-Z0-9]", "", base)
    elif char == ("a"):  # Aa: アルファベット
        p = re.sub(r"[^a-zA-Z]", "", base)
    elif char == ("n"):  # n: 数字
        # base64
        base = base64.b64encode(h.digest()).decode("utf-8")
        p = re.sub(r"[^0-9]", "", base)
    else:
        raise ValueError(f"char {char} は定義されていません。")

    # rm_chaをpから削除
    for i in rm_cha:
        p = p.replace(i, "")

    if upper:
        p = p.upper()
    if lower:
        p = p.lower()

    # 指定された長さのパスワードを表示する。
    print(p[start : start + plen])

    return {"password": p[start : start + plen], "all_chr": base}


def input_master():
    """マスターパスワードの入力を受け付け，チェック"""

    flag = True
    while flag:
        print("マスター1を入力: ")
        master1 = input()
        print("マスター2を入力: ")
        master2 = input()
        _ = make_password(master1, master2, seed="1234", plen=20, char="ans", rm_cha="", start=1)
        print("マスターパスワードは正しいですか？(y/n)")
        flag = input() == "n"
    return {"master1": master1, "master2": master2}


def get_input_site_info_cui():
    """サイトの情報を入力する"""

    site_name = input("Enter site name: ")
    id = input("Enter id: ")
    seed = input("Enter seed: ")
    plen = input("Enter length (default is 20): ")
    plen = int(plen) if plen else 20
    char = input("Enter char (ans/an/a/n): ")

    # 更新した日も記録
    update_date = time.strftime("%Y/%m/%d", time.localtime())
    return {"site_name": site_name, "id": id, "seed": seed, "plen": plen, "char": char, "update_date": update_date}


def get_input_site_info():
    """サイトの情報を入力する"""
    if GUI_AVAILABLE:
        print("GUI is not available yet.")
        site_info_dict = get_input_site_info_cui()
    else:
        site_info_dict = get_input_site_info_cui()
    return site_info_dict


def append_dict_to_csv(filename, data_dict):
    try:
        df = pd.read_csv(filename)
    except FileNotFoundError:
        df = pd.DataFrame()

    # 現在の列と新しいデータのキーを取得
    existing_columns = set(df.columns)
    new_data_keys = set(data_dict.keys())

    # 新しいデータにはあるがCSVにはない列を特定
    for col in new_data_keys - existing_columns:
        df[col] = ""

    # 新しい行をDataFrameに追加
    df = pd.concat([df, pd.DataFrame([data_dict])], ignore_index=True)
    # CSVファイルに保存
    while True:
        try:
            df.to_csv(filename, index=False)
            break
        except PermissionError:
            input("ファイルがロックされています。ファイルを閉じて、Enterキーを押してください。")


masters = input_master()
site_info = get_input_site_info()
print(site_info)


make_password(**masters, **site_info)

path = "hash_key.csv"
append_dict_to_csv(path, site_info)
