
# 単純メモリbackend (SLDB-backend) [memory_backend]
# 【動作確認 / 使用例】

import sys
from sout import sout
from relpath import add_import_path
add_import_path("../")
# 単純メモリbackend (SLDB-backend) [memory_backend]
import memory_backend

# メモリバックエンドへの接続 [memory_backend]
m_back = memory_backend.conn("./test_db/")
print("fuga")

m_back["key_1"] = "hoge"	# create, update共通 [memory_backend]
print(m_back["key_1"])	# key読み出し [memory_backend]
del m_back["key_1"]	# 削除 [memory_backend]
print("key_1" in m_back)	# 存在確認 [memory_backend]
m_back.commit()	# 強制commit [memory_backend]

# (非公式インターフェース) 文字列化
print(m_back)
