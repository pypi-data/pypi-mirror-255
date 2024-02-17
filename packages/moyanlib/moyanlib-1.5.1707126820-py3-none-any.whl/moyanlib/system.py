import os as _os
import moyanlib.Error as _Error


def listdir(path):
    # 列出所有dir
    try:
        obj = _os.listdir(path)
    except:
        raise _Error.PathError(path)
    else:
        return obj


def remove_file(path):
    # 删除文件
    if _os.path.exists(path):
        _os.remove(path)


def move_file(src, dst):
    # 重命名
    if _os.path.exists(src):
        _os.rename(src, dst)


def system(command):
    # 获取system
    obj = _os.popen(command)
    text = obj.read()
    return text
