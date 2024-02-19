# ###############################################
# 自作moduleをimportするための設定
import sys
import os

# スクリプトの現在のディレクトリを取得
current_dir = os.path.dirname(os.path.abspath(__file__))
# プロジェクトのルートディレクトリへのパスを取得
project_root = os.path.dirname(current_dir)
# Pythonの検索パスにプロジェクトのルートディレクトリを追加
sys.path.insert(0, project_root)
# ###############################################

# 実行中のPythonのバージョンを取得
python_version = sys.version_info

# バージョンに基づいて特定のモジュールをインポート
if (python_version.major, python_version.minor) == (3, 10):
    from .python_version_3_10.src import *
elif (python_version.major, python_version.minor) == (3, 11):
    from .python_version_3_11.src import *
else:
    raise ImportError("このパッケージはPython 3.10.x または 3.11.x でのみサポートされています")