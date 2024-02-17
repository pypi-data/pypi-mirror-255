
# CachedFileDic-backend (SLDB-backend) [cfd_backend]
# 【動作確認 / 使用例】

import sys
from sout import sout
from relpath import add_import_path
add_import_path("../")
# CachedFileDic-backend (SLDB-backend) [cfd_backend]
import cfd_backend

# CachedFileDicバックエンドへの接続 [cfd_backend]
cfd_back = cfd_backend.conn("./test_db/")

cfd_back["key_1"] = "hoge"	# create, update共通 [cfd_backend]
print(cfd_back["key_1"])	# key読み出し [cfd_backend]
del cfd_back["key_1"]	# 削除 [cfd_backend]
print("key_1" in cfd_back)	# 存在確認 [cfd_backend]
cfd_back.commit()	# 強制commit [cfd_backend]

# (非公式インターフェース) 文字列化
print(cfd_back)
