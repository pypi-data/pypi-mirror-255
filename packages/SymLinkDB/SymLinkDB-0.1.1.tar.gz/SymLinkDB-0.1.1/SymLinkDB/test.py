
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

# 例外のassert (「例外が発生し、所定のキーワードを含むこと」)
def assert_err(
	proc_func,	# 対象の処理 (ゼロ引数関数)
	msg = ""	# 例外が含むべき文字列 (省略された場合は、「例外は発生すべきだが、文言は問わない」)
):
	try:
		proc_func()
	except Exception as err:
		assert (msg in repr(err))
		return True
	# 正常に処理が完了した場合はassert失敗
	raise Exception("[assert_err error] 例外が発生すべき処理について正常終了したため、想定外です")

# --- テスト準備 ---

# テスト用にディレクトリを削除・再作成
if os.path.exists("./db_dir"): shutil.rmtree("./db_dir")
for dirname in [f"./db_dir/{i+1}/" for i in range(5)]:
	os.makedirs(dirname)	# 消し忘れの場合等はわざとエラーにする

# バックエンドを初期化
m_back1 = SymLinkDB.memory_backend("./db_dir/1/")	# メモリバックエンドの初期化 [SymLinkDB]
m_back2 = SymLinkDB.memory_backend("./db_dir/2/")	# メモリバックエンドの初期化 [SymLinkDB]
m_back3 = SymLinkDB.memory_backend("./db_dir/3/")	# メモリバックエンドの初期化 [SymLinkDB]
m_back4 = SymLinkDB.memory_backend("./db_dir/4/")	# メモリバックエンドの初期化 [SymLinkDB]

# SLDB初期化 [SymLinkDB]
sldb = SymLinkDB.conn(backend = m_back1)

# tableの読み込み (存在しない場合は空で初期化される) [SymLinkDB]
sldb.load_table("user_table", backend = m_back2)
# tableの読み込み (存在しない場合は空で初期化される) [SymLinkDB]
sldb.load_table("tool_table", backend = m_back3)
# linkの読み込み (存在しない場合は空で初期化される) [SymLinkDB]
sldb.load_link(
	"所有関係",	# テーブル名
	("user_table", "所有者", "1"),	# 関係性情報0 (table名, role, 1 or N)
	("tool_table", "所有物", "N"),	# 関係性情報1 (table名, role, 1 or N)
	backend = m_back4
)

# --- SLDBのテスト ---

# 文字列化 (その1, その2)
sldb_str = str(sldb)	# -> '<SymLinkDB tables = ["user_table", "tool_table"]>'
print(sldb_str)
assert sldb_str == '<SymLinkDB tables = ["user_table", "tool_table"]>'

assert len(sldb) == 2	# table数取得 [SymLinkDB]
assert ("user_table" in sldb)	# tableの存在確認 [SymLinkDB]
assert ("dummy_table_name" not in sldb)	# tableの存在確認 [SymLinkDB]
assert list(sldb) == ['user_table', 'tool_table']	# tableのイテレート [SymLinkDB]

# --- tableのテスト ---

# tableの取得 [SymLinkDB]
tool_table = sldb["tool_table"]
# レコードの新規作成 [SymLinkDB]
tool1_rec = tool_table.create(data = "tool1", links = {("所有関係", "所有者"): None})
print(f"tool1_id: {tool1_rec.id}")
tool2_rec = tool_table.create(data = "tool2", links = {"所有者": None})
tool3_rec = tool_table.create(data = "tool3", links = {"所有者": []})
# 文字列化 (その1, その2)
table_str = str(tool_table)	# -> '<SymLinkTable tool_table recs = {"dIMcC": <Rec "tool1">, ... (n = 3)}>'
print(table_str)
assert "<SymLinkTable tool_table recs = " in table_str
assert "(n = 3)" in table_str

user_table = sldb["user_table"]	# tableの取得 [SymLinkDB]

user1_rec = user_table.create(data = {"name": "user1"}, links = {"所有物": [tool1_rec, tool2_rec]})	# レコードの新規作成 [SymLinkDB]
user2_rec = user_table.create(data = {"name": "user2"}, links = {"所有物": None})	# レコードの新規作成 [SymLinkDB]
user3_rec = user_table.create(data = {"name": "user3"}, links = {})	# レコードの新規作成 [SymLinkDB]
user3_id = user3_rec.id
del user_table[user3_rec]	# レコードの削除 [SymLinkDB]
assert_err(lambda: user3_rec["所有物"], msg = "This record is already deleted.")	# 例外のassert (「例外が発生し、所定のキーワードを含むこと」)
assert user1_rec in user_table	# レコードの存在確認 [SymLinkDB]
assert user1_rec.id in user_table
assert user3_rec.id not in user_table
assert len(user_table) == 2	# レコード数取得 [SymLinkDB]
# tableのイテレート [SymLinkDB]
assert set([rec.id for rec in user_table]) == {user1_rec.id, user2_rec.id}

# レコードの取得 [SymLinkDB]
got_user1_rec = user_table[user1_rec.id]
assert user1_rec.id == got_user1_rec.id

# --- recordのテスト ---

# レコードの文字列化 [SymLinkDB]
rec_str = str(user1_rec)	# -> '<SymLinkRecord user_table.(レコードのID) data = {"name": "user1"} links = [("所有関係", "所有物")]>'
print(rec_str)
assert rec_str == f'<SymLinkRecord user_table.{user1_rec.id} data = {{"name": "user1"}} links = [("所有関係", "所有物")]>'

# 削除済みレコードの文字列化
assert str(user3_rec) == "<SymLinkRecord (deleted)>"

user1_rec.data = {"name": "taro", "age": 23}	# レコードのdataのupdate [SymLinkDB]
assert user1_rec.data == {'name': 'taro', 'age': 23}	# レコードのdataの取得 [SymLinkDB]
print(user1_rec.id)	# レコードのidの取得 [SymLinkDB]
assert user1_rec.table_name == "user_table"	# レコードの所属table名の取得 [SymLinkDB]
table = user1_rec.table	# レコードの所属tableオブジェクトの取得 [SymLinkDB]
assert table.table_id == user_table.table_id

assert set([key for key in user1_rec]) == {('所有関係', '所有物')}	# レコードのイテレート [SymLinkDB]
assert ('所有関係', '所有物') in user1_rec	# 指定されたlinkの存在確認 [SymLinkDB]
assert '所有物' in user1_rec	# 指定されたlinkの存在確認 [SymLinkDB]

# --- link_setのテスト ---

# link_setの取得 [SymLinkDB]
user1_link_set = user1_rec[("所有関係", "所有物")]

# 略指定による取得
assert {r.id for r in user1_rec["所有物"]} == {r.id for r in user1_link_set}

# linkの追加 [SymLinkDB]
user1_link_set.push(tool3_rec)

# linkの削除 [SymLinkDB]
del user1_link_set[tool2_rec]

# linkの存在確認 [SymLinkDB]
assert tool3_rec in user1_link_set
assert tool3_rec.id in user1_link_set	# レコードIDでも存在確認可能
assert tool2_rec not in user1_link_set

# link_set内の要素をイテレート [SymLinkDB]
assert set([rec.id for rec in user1_link_set]) == {tool1_rec.id, tool3_rec.id}

assert len(user1_link_set) == 2	# link_set内の要素数を取得 [SymLinkDB]

# 文字列化 (その1, その2)
u1_l_set_str = str(user1_link_set)	# -> "<LinkSet 所有関係: user_table(所有者;1) -> tool_table(所有物;N;n=2)>"
print(u1_l_set_str)
assert u1_l_set_str == "<LinkSet 所有関係: user_table(所有者;1) -> tool_table(所有物;N;n=2)>"

# 強制コミット [SymLinkDB]
sldb.commit()

# --- 発展的な使い方 ---

# CachedFileDicバックエンドの利用
cfd_backend = SymLinkDB.cfd_backend("./db_dir/5/")	# CachedFileDicバックエンドの初期化 [SymLinkDB]
sldb.load_table("example_table", backend = cfd_backend)	# tableの読み込み (存在しない場合は空で初期化される) [SymLinkDB]

# dataの型は任意
rec = user_table.create(data = b"binary_data")
print(rec)	# -> "<SymLinkRecord user_table.(レコードのID) data = b'binary_data' links = [("所有関係", "所有物")]>"

# バックエンドを明示的に指定しない場合は、SymLinkDB.conn()時のbackendが使われる
sldb.load_table("pictures_table")	# tableの読み込み (存在しない場合は空で初期化される) [SymLinkDB]

# --- 異常系や複雑な場合のテスト ---

# 1-N関係を無視したpush
def err_push_1(): tool1_rec["所有者"].push(user2_rec)
assert_err(err_push_1, "Violation of 1-N constraint")

# 既にあるIDのpush
def err_push_2(): tool1_rec["所有者"].push(user1_rec)
assert_err(err_push_2, "This is a link that has already been added")

# 全く無関係なIDのpush
def err_push_3(): tool1_rec["所有者"].push(tool2_rec.id)
assert_err(err_push_3, "specified record ID does not exist in the table")

# 複数同時delete, push
del user1_link_set[tool1_rec, tool3_rec.id]
user1_link_set.push([tool1_rec, tool2_rec.id])
assert {rec.id for rec in user1_link_set} == {tool1_rec.id, tool2_rec.id}

# link両端のrole名が被っているときに例外を出す
def err_link_1():
	sldb.load_link(	# linkの読み込み (存在しない場合は空で初期化される) [SymLinkDB]
		"友人関係",	# テーブル名
		("user_table", "人", "1"),	# 関係性情報0 (table名, role, 1 or N)
		("user_table", "人", "1"),	# 関係性情報1 (table名, role, 1 or N)
	)
assert_err(err_link_1, "The role names at both ends of the link must be different.")

# 1-table内関係・N-N関係
sldb.load_link(	# linkの読み込み (存在しない場合は空で初期化される) [SymLinkDB]
	"親子関係",	# テーブル名
	("user_table", "親", "N"),	# 関係性情報0 (table名, role, 1 or N)
	("user_table", "子", "N"),	# 関係性情報1 (table名, role, 1 or N)
)
child_link_set_1 = user1_rec["子"]
user4_rec = user_table.create("user4")
user5_rec = user_table.create("user5")
child_link_set_1.push([user2_rec, user4_rec])
user4_rec["親"].push(user5_rec)
assert {rec.id for rec in user2_rec["親"]} == {user1_rec.id}
assert {rec.id for rec in user4_rec["親"]} == {user1_rec.id, user5_rec.id}
assert {rec.id for rec in user5_rec["子"]} == {user4_rec.id}
assert {rec.id for rec in user1_rec["子"]} == {user2_rec.id, user4_rec.id}

# table - del済みレコードのdel
def err_del_1():
	del user_table[user3_id]	# レコードの削除 [SymLinkDB]
assert_err(err_del_1, "You cannot delete a record that does not exist")

# delete時のlink自動削除
del tool_table[tool2_rec]
assert tool2_rec not in user1_rec["所有物"]
sys.exit()

# rec数の大きなテーブルでCRUD速度テスト
large_n = 1000000
sldb.load_table("large_data_test_table")
ldt_table = sldb["large_data_test_table"]
print("creating...")
for i in tqdm(range(large_n)):
	ldt_table.create(data = {"hoge": f"data_{i%10}" * (10000 // 6)})
print("reading and updating...")
for rec in tqdm(ldt_table):
	now_data = rec.data
	rec.data = {**now_data, "fuga": "new_data"}
print('running "contains"...')
for rec in tqdm(ldt_table): (rec in ldt_table)
print('reading ids...')
rec_id_ls = [rec.id for rec in tqdm(ldt_table)]
print('deleting...')
for rec in tqdm(rec_id_ls):
	del ldt_table[rec]
