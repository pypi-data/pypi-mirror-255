
# 双方向グラフDB [SymLinkDB]
# 【動作確認 / 使用例】

import os
import sys
import shutil
from tqdm import tqdm
from sout import sout
from ezpip import load_develop
# 双方向グラフDB [SymLinkDB]
SymLinkDB = load_develop("SymLinkDB", "../", develop_flag = True)

# データベースディレクトリの準備
db_dir = "./document_test"
if not os.path.exists(db_dir):
    os.makedirs(db_dir)

# バックエンドの初期化
backend = SymLinkDB.memory_backend(db_dir)  # デフォルトの単純なバックエンド

# データベース接続の確立
sldb = SymLinkDB.conn(backend=backend)

# テーブルのロード
sldb.load_table("user_table")
sldb.load_table("tool_table")

# リンクのロード
sldb.load_link(
    "所有関係",
    ("user_table", "所有者", "1"),
    ("tool_table", "所有物", "N")
)

# user_tableにレコードを追加
user_rec = sldb["user_table"].create(data={"name": "Alice"})

# tool_tableにレコードを追加し、所有関係を設定
tool_rec = sldb["tool_table"].create(data="Hammer", links={("所有関係", "所有者"): user_rec})

# 逆向きのリンクも自動的に追加されている
print(tool_rec in user_rec["所有物"])  # -> True

# レコードのデータを更新
user_rec.data = {"name": "Alice", "age": 30}

# 特定のレコードをIDを使用して取得
retrieved_rec = sldb["user_table"][user_rec.id]

# レコードのデータを読み出し
retrieved_data = retrieved_rec.data
print(retrieved_data)   # -> {'name': 'Alice', 'age': 30}

# del sldb["user_table"][user_rec]

# 新しいリンクを追加
new_tool_rec = sldb["tool_table"].create(data="Screwdriver")
link_set = user_rec["所有物"]    # 対象レコードに関係するリンク群 (link_set) を取得
# link_set = user_rec[("所有関係", "所有物")]    # role名のみでは指定が曖昧になる場合は、このようにタプルを用いた正式な参照を用いる
link_set.push(new_tool_rec)

# link_set内の要素をイテレート [SymLinkDB]
for rec in link_set: print(rec) # リンク先のレコードが順次取得される

flag = (new_tool_rec in link_set)    # linkの存在確認 [SymLinkDB]
print(len(link_set))  # link_set内の要素数を取得 [SymLinkDB]

# リンクを削除
del link_set[new_tool_rec]
