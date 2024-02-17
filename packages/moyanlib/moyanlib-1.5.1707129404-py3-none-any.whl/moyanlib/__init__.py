import string as _str
import random as _ran
import psutil as _ps
import platform as _pf
import hashlib as _h


def genVerifiCode(wei: int = 4):
    """_summary_

    Keyword Arguments:
        wei -- 位数 (default: {4})

    Returns:
        生成的验证码
    """
    # 生成所有可能出现在验证码中的字符
    characters = _str.ascii_letters + _str.digits

    # 生成8位随机验证码
    verification_code = "".join(_ran.choice(characters) for _ in range(wei))

    return verification_code


def getDeviceID():
    # 获取设备ID
    system_name = _pf.platform()
    computer_name = _pf.node()
    computer_system = _pf.system()
    computer_bit = _pf.architecture()[0]
    cpu_count = _ps.cpu_count()
    mem = _ps.virtual_memory()
    mem_total = format(float(mem.total) / 1024 / 1024 / 1024)
    deviceid = (
        system_name
        + "_"
        + computer_name
        + "_"
        + computer_system
        + "_"
        + computer_bit
        + "_"
        + str(cpu_count)
        + "_"
        + mem_total
    )
    # 对id进行sha1
    hash_id = _h.sha1(deviceid.encode("utf-16be")).hexdigest()
    big_hash_id = str(hash_id).upper()
    return big_hash_id
