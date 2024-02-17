
# CachedFileDic-backend (SLDB-backend) [cfd_backend]

import os
import sys
import fies
import atexit
import pickle
import slim_id
import CachedFileDic
from sout import sout, souts
from relpath import add_import_path
add_import_path("../")
# 単純メモリbackend (SLDB-backend) [memory_backend]
import memory_backend

# プログラム終了時にcommitを実行する
commit_target_ls = []	# コミット対象
def cleanup():
	for one_backend in commit_target_ls:
		one_backend.commit()
# プログラム終了時に呼び出す関数を登録
atexit.register(cleanup)

# CachedFileDic-backend (SLDB-backend) [cfd_backend]
class CFD_Backend:
	# 初期化処理
	def __init__(self, data_dir):
		# インデックスとデータを格納する2つのディレクトリ
		mem_idx_dir = os.path.join(data_dir, "mem_idx")
		cfd_data_dir = os.path.join(data_dir, "cfd_data")
		if not os.path.exists(mem_idx_dir): os.makedirs(mem_idx_dir)
		if not os.path.exists(cfd_data_dir): os.makedirs(cfd_data_dir)
		# インデックスを格納するmemory_backendの初期化
		self.mem_idx = memory_backend.conn(mem_idx_dir)	# メモリバックエンドへの接続 [memory_backend]
		# データを格納するCachedFileDicの初期化
		self.cfd_data = CachedFileDic.conn(cfd_data_dir)	# 対象ディレクトリに接続 [CachedFileDic]
		# プログラム終了時のcommit対象に自身を追加
		commit_target_ls.append(self)
	# create, update共通 [memory_backend]
	def __setitem__(self, key, value):
		# 新しいinner_keyの生成
		inner_key = slim_id.gen(lambda e: (e in self.cfd_data), length = 22)	# 十分に長いkey
		# 両方の辞書に登録
		self.mem_idx[key] = inner_key
		self.cfd_data[inner_key] = value
	# key読み出し [memory_backend]
	def __getitem__(self, key):
		inner_key = self.mem_idx[key]
		return self.cfd_data[inner_key]
	# 削除 [memory_backend]
	def __delitem__(self, key): del self.mem_idx[key]	# メモリーバックエンドのみから削除
	# 存在確認 [memory_backend]
	def __contains__(self, key): return (key in self.mem_idx)
	# 強制commit [memory_backend]
	def commit(self):
		self.mem_idx.commit()
		self.cfd_data.commit()
	# 文字列化 (その1, その2)
	def __str__(self):
		# memory-backendの非公式APIを利用
		for key_example in self.mem_idx: break	# keyの例を取得
		size = len(self.mem_idx)
		data_str = ("" if size == 0
			else f'{key_example}: {souts(self[key_example])}' +
				("" if size == 1 else f", ...(n={size})")
		)
		return f"<SLDB-CFD_backend {{{data_str}}}>"
	def __repr__(self): return str(self)

# CachedFileDicバックエンドへの接続 [cfd_backend]
def conn(
	data_dir	# バックエンドの情報を記録するディレクトリ
):
	# バックエンドのクラス
	return CFD_Backend(data_dir)
