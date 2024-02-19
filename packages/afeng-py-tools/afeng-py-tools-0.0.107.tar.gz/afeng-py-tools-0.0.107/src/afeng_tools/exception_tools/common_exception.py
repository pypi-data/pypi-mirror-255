class AfengException(Exception):
    """自定义异常类，继承自内置的 Exception 类"""

    def __init__(self, message: str):
        """初始化方法，可以接收一个消息作为参数"""
        self.message = message

    def __str__(self):
        """返回异常的字符串表示，通常是异常的消息"""
        return self.message


class HttpException(Exception):
    """自定义异常类，继承自内置的 Exception 类"""

    def __init__(self, status_code: int, message: str):
        """初始化方法，可以接收一个消息作为参数"""
        self.status_code = status_code
        self.message = message

    def __str__(self):
        """返回异常的字符串表示，通常是异常的消息"""
        return f'[{self.status_code}]{self.message}'
