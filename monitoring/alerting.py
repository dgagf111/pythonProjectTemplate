import time
from log.logHelper import get_logger

logger = get_logger()

def check_cpu_usage(threshold=80):
    cpu_usage = 85  # 这里应该使用实际的 CPU 使用率检查逻辑
    if cpu_usage > threshold:
        logger.warning(f"CPU 使用率过高: {cpu_usage}%")
    return cpu_usage > threshold  # 返回一个布尔值表示是否触发报警

def check_memory_usage(threshold=80):
    # 同样，这里应该使用实际的内存使用率检查逻辑
    memory_usage = 75
    if memory_usage > threshold:
        logger.warning(f"内存使用率过高: {memory_usage}%")
        # 添加发送警报的逻辑

def setup_alerting():
    logger.info("设置报警系统...")
    while True:
        check_cpu_usage()
        check_memory_usage()
        time.sleep(60)  # 每分钟检查一次
