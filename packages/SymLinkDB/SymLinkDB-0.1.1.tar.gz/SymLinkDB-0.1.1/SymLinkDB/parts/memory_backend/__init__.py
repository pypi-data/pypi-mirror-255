
# 単純メモリbackend (SLDB-backend) [memory_backend]

import os
import sys
import fies
import atexit
import pickle
from sout import sout, souts

# プログラム終了時にcommitを実行する
commit_target_ls = []	# コミット対象
def cleanup():
	for one_backend in commit_target_ls:
		one_backend.commit()
# プログラム終了時に呼び出す関数を登録
atexit.register(cleanup)

# 初期化されていない場合は初期化
def init_if_needed(data_filename):
	if os.path.exists(data_filename) is True: return None
	fies[data_filename, "pickle"] = {}

# メモリバックエンドのクラス
class Memory_Backend:
	# 初期化処理
	def __init__(self, data_dir):
		# データ保存パス
		self.data_filename = os.path.join(data_dir, "memory_backend_data.pickle")
		# 初期化されていない場合は初期化
		init_if_needed(self.data_filename)
		# ファイルの内容をメモリに展開
		self.data = fies[self.data_filename, "pickle"]
		# プログラム終了時のcommit対象に自身を追加
		commit_target_ls.append(self)
	# create, update共通 [memory_backend]
	def __setitem__(self, key, value): self.data[key] = value
	# key読み出し [memory_backend]
	def __getitem__(self, key): return self.data[key]
	# 削除 [memory_backend]
	def __delitem__(self, key): del self.data[key]
	# 存在確認 [memory_backend]
	def __contains__(self, key): return (key in self.data)
	# 強制commit [memory_backend]
	def commit(self):
		fies[self.data_filename, "pickle"] = self.data
	# 文字列化 (その1, その2)
	def __str__(self): return f"<SLDB-memory_backend {souts(self.data)}>"
	def __repr__(self): return str(self)
	# 非公式API: イテレーション
	def __iter__(self): return iter(self.data)
	# 非公式API: 要素数取得
	def __len__(self): return len(self.data)

# メモリバックエンドへの接続 [memory_backend]
def conn(
	data_dir	# バックエンドの情報を記録するディレクトリ
):
	# メモリバックエンドのクラス
	return Memory_Backend(data_dir)
