# @Time    : 2023/10/30 16:34
# @Author  : fyq
# @File    : exception.py
# @Software: PyCharm

__author__ = 'fyq'


class PoeException(Exception):
    pass


class ReachedLimitException(PoeException):
    pass
