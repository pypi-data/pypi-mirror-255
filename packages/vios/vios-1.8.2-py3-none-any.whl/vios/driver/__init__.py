"""本模块定义设备的驱动基类
所有驱动继承自BaseDriver, 类名统一为Driver, 并要求实现open/close/read/write四个方法。

模板见VirtualDevice
"""


try:
    # import URL from dev in systemq
    from dev import URL
except Exception as e:
    pass
