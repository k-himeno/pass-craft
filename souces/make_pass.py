"""パスワード生成"""
# -*- coding: utf-8 -*-

# 参考: https://sekika.github.io/2017/05/09/Password/
# 参考と異なりパスワードはパスワード管理アプリで保存する．あくまでも生成のみに用いる．

import base64
import hashlib
import os
import platform
import re
import time

import pandas as pd

# TODO GUI使えるなら使いたい

try:
    import tkinter as tk
    from tkinter import Button, Entry, IntVar, Label, OptionMenu, StringVar, Tk, filedialog

    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False


def input_master_cui():
    print("マスター1を入力: ")
    master1 = input()
    print("マスター2を入力: ")
    master2 = input()
    return master1, master2


def input_site_info_cui():
    """サイトの情報を入力する"""

    site_name = input("Enter site name: ")
    id = input("Enter id: ")
    seed = input("Enter seed: ")
    plen = input("Enter length (default is 20): ")
    plen = int(plen) if plen else 20
    char = input("Enter char (ans/an/a/n) (default is ans): ")
    char = char if char != "" else "ans"

    # 更新した日も記録
    update_date = time.strftime("%Y/%m/%d", time.localtime())
    site_info_dict = {
        "site_name": site_name,
        "id": id,
        "seed": seed,
        "plen": plen,
        "char": char,
        "update_date": update_date,
    }
    return site_info_dict


def input_add_site_info_cui(site_info_dict):
    """最初のinfoで満足できなかった時，追加でサイトの情報を入力する

    Args:
        site_info_dict (dict): input_site_infoの返り値

    Returns:
        dict: site_info_dict (更新された)
    """
    site_info_dict["start"] = int(input("start (default is 1): ") or 1)
    site_info_dict["rm_cha"] = input("rm_cha: ")
    upper_lower = input("upper_lower (both/upper/lower) (default is both): ")
    if upper_lower in ["upper", "lower", "both"]:
        site_info_dict["upper_lower"] = upper_lower
    return site_info_dict


def make_password(master1, master2, seed, plen=20, char="ans", rm_cha="", start=1, upper_lower="both", **kwargs):
    """パスワードを生成する関数

    Args:
        master1 (str): マスターパスワード1
        master2 (str): マスターパスワード2
        seed (str, optional): サービスごとのパスワード.
        plen (int, optional): パスワードの長さ． Defaults to 20.
        char (str, optional): a[アルファベット], n[数字], s[記号]の組み合わせ. Defaults to "ans".
        rm_cha (str, optional): NG記号. Defaults to "".
        start (int, optional): パスワードの開始位置. Defaults to 1.
        upper_lower (str, optional): 大文字小文字縛りがあるか. Defaults to "both".
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

    if upper_lower == "upper":
        p = p.upper()
    elif upper_lower == "lower":
        p = p.lower()

    # rm_chaをpから削除
    for i in rm_cha:
        p = p.replace(i, "")

    # 指定された長さのパスワードを表示する。
    print(p[start : start + plen])

    return {"password": p[start : start + plen], "all_chr": base}


def get_input_master():
    """マスターパスワードの入力を受け付け，チェック"""

    flag = True
    while flag:
        master1, master2 = input_master_cui()
        _ = make_password(master1, master2, seed="1234", plen=20, char="ans", rm_cha="", start=1)
        print("マスターパスワードは正しいですか？(y/n)")
        flag = input() == "n"
    return master1, master2


def append_dict_to_csv(csv_path, data_dict):
    """CSVファイルに辞書を追加する

    Args:
        csv_path (str): csv_path
        data_dict (dict): site_info_dict
    """
    try:
        df = pd.read_csv(csv_path)
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
            df.to_csv(csv_path, index=False)
            break
        except PermissionError:
            input("ファイルがロックされています。ファイルを閉じて、Enterキーを押してください。")


def check_and_regenerate_password(master1, master2, password_data, site_info_dict):
    """パスワードの確認と再生成を行う

    Args:
        master1 (str): master1
        master2 (str): master2
        password_data (dict): make_passwordの返り値
        site_info_dict (dict): input_site_infoの返り値

    Returns:
        site_info_dict: 最終的なsite_info_dict
    """
    while True:
        if input(password_data["password"] + "\n パスワードは満足ですか？(y/n): ") != "n":
            break
        print("全ての文字列: ", password_data["all_chr"])
        site_info_dict = input_add_site_info_cui(site_info_dict)
        password_data = make_password(master1, master2, **site_info_dict)
    return site_info_dict


# GUIによる入力
class GetInputMasterGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Password Generator")

        # Widgets initialization
        Label(self, text="Master1").grid(row=0, column=0)
        self.master1_entry = Entry(self, show="*")
        self.master1_entry.grid(row=0, column=1)

        Label(self, text="Master2").grid(row=1, column=0)
        self.master2_entry = Entry(self, show="*")
        self.master2_entry.grid(row=1, column=1)

        # Button
        submit_button = Button(self, text="Generate Password", command=self.submit)
        submit_button.grid(row=2, column=0, columnspan=2)

        # Result
        self.result_var = StringVar()
        Label(self, text="Generated Password:").grid(row=3, column=0)
        Label(self, textvariable=self.result_var).grid(row=3, column=1)

        # Finish Button
        finish_button = Button(self, text="Finish", command=self.finish)
        finish_button.grid(row=4, column=0, columnspan=2)

    def submit(self):  # 入力の受付と計算
        self.master1 = self.master1_entry.get()
        self.master2 = self.master2_entry.get()

        # make_password function call and display result
        password_data = make_password(
            self.master1, self.master2, seed="1234"
        )  # Assuming make_password function is defined elsewhere
        self.result_var.set(password_data["password"])

    def finish(self):
        self.destroy()  # Close the application


class PasswordGeneratorGUI(tk.Tk):
    def __init__(self, master1, master2):
        super().__init__()
        self.master1 = master1
        self.master2 = master2
        self.title("Password Generator")

        # Layout and widgets
        self.create_widgets()

    def create_widgets(self):
        # Entries for site_info
        Label(self, text="Site Name").grid(row=0, column=0)
        self.site_name_entry = Entry(self)
        self.site_name_entry.grid(row=0, column=1)

        Label(self, text="ID").grid(row=1, column=0)
        self.id_entry = Entry(self)
        self.id_entry.grid(row=1, column=1)

        Label(self, text="Seed").grid(row=2, column=0)
        self.seed_entry = Entry(self)
        self.seed_entry.grid(row=2, column=1)

        Label(self, text="Password Length").grid(row=3, column=0)
        self.plen_entry = Entry(self)
        self.plen_entry.insert(0, "20")
        self.plen_entry.grid(row=3, column=1)

        Label(self, text="Start").grid(row=4, column=0)
        self.start_entry = Entry(self)
        self.start_entry.insert(0, "1")
        self.start_entry.grid(row=4, column=1)

        Label(self, text="Char").grid(row=5, column=0)
        self.char_var = StringVar(self)
        self.char_var.set("ans")
        self.char_options = OptionMenu(self, self.char_var, "ans", "an", "a", "n")
        self.char_options.grid(row=5, column=1)

        Label(self, text="Upper/Lower").grid(row=6, column=0)
        self.upper_lower_var = StringVar(self)
        self.upper_lower_var.set("both")
        self.upper_lower_options = OptionMenu(self, self.upper_lower_var, "both", "upper", "lower")
        self.upper_lower_options.grid(row=6, column=1)

        Label(self, text="Remove Characters").grid(row=7, column=0)
        self.rm_cha_entry = Entry(self)
        self.rm_cha_entry.grid(row=7, column=1)

        # Generate password button
        self.generate_btn = Button(self, text="Generate Password", command=self.generate_password)
        self.generate_btn.grid(row=8, column=0, columnspan=2)

        # Labels to display generated password and all characters
        self.password_var = StringVar()
        self.all_chr_var = StringVar()

        Label(self, text="Password:").grid(row=9, column=0)
        password_entry = Entry(self, textvariable=self.password_var, state="readonly")
        password_entry.grid(row=9, column=1)
        Label(self, text="All Characters:").grid(row=10, column=0)
        Label(self, textvariable=self.all_chr_var).grid(row=10, column=1)

        # Finish button
        self.finish_btn = Button(self, text="Finish", command=self.finish)
        self.finish_btn.grid(row=11, column=0, columnspan=2)

    def generate_password(self):
        self.site_info = {
            "site_name": self.site_name_entry.get(),
            "id": self.id_entry.get(),
            "seed": self.seed_entry.get(),
            "plen": int(self.plen_entry.get()),
            "start": int(self.start_entry.get()),
            "char": self.char_var.get(),
            "upper_lower": self.upper_lower_var.get(),
            "rm_cha": self.rm_cha_entry.get(),
            "update_date": time.strftime("%Y/%m/%d", time.localtime()),
        }
        password_data = make_password(self.master1, self.master2, **self.site_info)
        self.password_var.set(password_data["password"])
        self.all_chr_var.set(password_data["all_chr"])

    def finish(self):
        # Extracting all the info

        # ここで `site_info` を保存や出力したい処理を追加できます。
        # 例: ファイルへの保存、データベースへの保存など

        # GUIを閉じる

        self.destroy()


def get_csv_path(private_path):
    current_os = "posix" if os.name == "posix" else "nt"

    # privateフォルダ内のpathを保存したテキストファイルを確認
    if os.path.exists(private_path):
        with open(private_path, "r") as f:
            for line in f.readlines():
                os_name, saved_path = line.strip().split(":")
                if os_name == current_os and os.path.exists(saved_path):
                    return saved_path

    # GUIが利用可能な場合、ファイルダイアログでパスを選択
    if GUI_AVAILABLE:
        root = Tk()
        root.withdraw()  # メインウィンドウを表示しない
        path = filedialog.askopenfilename(
            title="Please select a CSV file", filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )
        root.destroy()
        if path:  # ダイアログでファイルが選択された場合
            with open(private_path, "a") as f:  # 'a' mode to append
                f.write(f"{current_os}:{path}\n")
            return path

    # GUIが利用不可、またはダイアログでキャンセルされた場合、CUIで入力を求める

    path = input("Please enter the CSV path (press Enter to use default): ").strip()
    with open(private_path, "a") as f:
        f.write(f"{current_os}:{path}\n")
    return path


if __name__ == "__main__":
    # ファイルがあるパスに移動
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    private_path = os.path.join("..", "private", "saved_path.txt")
    path = get_csv_path(private_path)

    if GUI_AVAILABLE:
        masterGUI = GetInputMasterGUI()
        masterGUI.mainloop()
        # これでmaster1, master2が取得できる
        app = PasswordGeneratorGUI(masterGUI.master1, masterGUI.master2)
        app.mainloop()
        append_dict_to_csv(path, app.site_info)

    else:
        # マスターパスワードを入力．
        # 正しいかをチェックするために，内部でmake_passwordを呼び出す．
        master1, master2 = get_input_master()

        # サイト情報を入力
        site_info_dict = input_site_info_cui()

        # 最初のパスワードを生成
        password_data = make_password(master1, master2, **site_info_dict)

        # パスワードに満足したかの質問
        site_info_dict = check_and_regenerate_password(master1, master2, password_data, site_info_dict)
