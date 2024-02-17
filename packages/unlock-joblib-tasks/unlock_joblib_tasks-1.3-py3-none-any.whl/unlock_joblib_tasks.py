"""
@author: PlumeSoft
@date: 2024-02-06

Unlock the limit of 63 tasks in Windows for the Python joblib library.
为 Python joblib 库解锁在 Windows 下最大 63 个任务数的限制的补丁包。

How to use:
使用方法:
    :import unlock_joblib_tasks
    :unlock_joblib_tasks.please()

This software is released under the BSD3 license, and anyone can use it for free without any restrictions.
该软件在BSD3协议下发布，任何人都可无限制免费使用，希望对你有用！
"""
__version__ = '1.3'

import sys

# 用于保存被 Hook 的 API
Saved_WaitForMultipleObjects = None

# 解锁以后支持的最大任务数
_UNLOCKED_MAX_WINDOWS_WORKERS = 510

if sys.platform == "win32":
    # 只在 Windows 平台下使用
    from typing import Sequence
    import _winapi

    def Hacked_WaitForMultipleObjects(__handle_seq: Sequence[int], __wait_flag: bool, __milliseconds: int = 0xFFFFFFFF) -> int:
        max_wait_objects = 63
        if len(__handle_seq) >= max_wait_objects:
            ret_list = []
            for idx in range(0, len(__handle_seq), max_wait_objects):
                tmp_seq = __handle_seq[idx:min(idx+max_wait_objects, len(__handle_seq))]
                # 只有第一组使用等待时间，后面组不等待直接查结果，避免实际等待时间超出参数值
                ret = Saved_WaitForMultipleObjects(tmp_seq, __wait_flag, __milliseconds if idx == 0 else 0)
                ret_list.append(ret)
                if ret == _winapi.WAIT_TIMEOUT:
                    # 等待当前组超时了
                    if __wait_flag:
                        # 如果等待全部事件则返回超时
                        return ret
                    else:
                        # 如果不是等待全部则继续处理下一组
                        continue
                elif ret == _winapi.WAIT_ABANDONED_0:
                    # 当前组全部成功
                    if __wait_flag:
                        # 如果等待全部事件则继续处理下一组
                        continue
                    else:
                        # 不是全部等待也要看后面的组是不是全部完成了
                        continue
                elif ret >= _winapi.WAIT_OBJECT_0:
                    # 只有部分事件成功了
                    if not __wait_flag:
                        # 不是等待全部时直接返回成功的对象序号，如果不是第一组需要加上当前组的起始序号 idx
                        return idx + ret - _winapi.WAIT_OBJECT_0
                    else:
                        continue
            
            # 只有不是全部等待并且中间也没有事件成功才会执行到这里，检查所有分组的返回值
            if all(x == _winapi.WAIT_ABANDONED_0 for x in ret_list):
                # 所有组都完全成功
                return _winapi.WAIT_ABANDONED_0
            elif all(x == _winapi.WAIT_TIMEOUT for x in ret_list):
                # 所有组都超时了
                return _winapi.WAIT_TIMEOUT
            else:
                # 有成功有超时，返回超时
                return _winapi.WAIT_TIMEOUT
        else:
            return Saved_WaitForMultipleObjects(__handle_seq, __wait_flag, __milliseconds)

def please() -> bool:
    if sys.platform == "win32":
        # 只在 Windows 平台下使用
        global Saved_WaitForMultipleObjects
        if Saved_WaitForMultipleObjects is None:
            # 避免重复 Hook API
            Saved_WaitForMultipleObjects = _winapi.WaitForMultipleObjects
            _winapi.WaitForMultipleObjects = Hacked_WaitForMultipleObjects

        try:
            # 新版本的 joblib 中有 _MAX_WINDOWS_WORKERS 对任务数进行了限制，此处需要强制修改该参数
            import joblib.externals.loky.backend.context as context
            if hasattr(context, '_MAX_WINDOWS_WORKERS'):
                setattr(context, '_MAX_WINDOWS_WORKERS', _UNLOCKED_MAX_WINDOWS_WORKERS)
            import joblib.externals.loky.process_executor as process_executor
            if hasattr(process_executor, '_MAX_WINDOWS_WORKERS'):
                setattr(process_executor, '_MAX_WINDOWS_WORKERS', _UNLOCKED_MAX_WINDOWS_WORKERS)
        except:
            pass
        return True
    else:
        return False