import logging
import sys

_logger = None


def get_logger(name: str = "ecommerce_agent") -> logging.Logger:
    """获取全局唯一 logger 实例（单例），避免重复添加 handler。"""
    global _logger

    if _logger is not None:
        return _logger

    _logger = logging.getLogger(name)
    _logger.setLevel(logging.INFO)

    # 避免重复添加——如果已有同类型 handler 则跳过
    if not any(isinstance(h, logging.StreamHandler) for h in _logger.handlers):
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        _logger.addHandler(handler)

    return _logger
