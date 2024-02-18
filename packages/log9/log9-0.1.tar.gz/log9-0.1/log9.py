
import logging
from colorlog import ColoredFormatter

def setup_logging(level=logging.INFO):
    # 清除所有已添加的处理器，防止重复输出日志
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
        
    # 定义日志格式和颜色
    fmt = "%(log_color)s%(asctime)s %(levelname)s %(message)s"
    log_colors = {
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
    formatter = ColoredFormatter(fmt, log_colors=log_colors, style='%')

    # 创建流处理器，并添加到日志记录器
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    
    # 获取日志记录器
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(stream_handler)