from prometheus_client import start_http_server
from .prometheus_exporter import setup_metrics
from .alerting import setup_alerting
from log.logHelper import get_logger

logger = get_logger()

def run(test_mode=False):
    logger.info("启动监控模块...")
    # 启动 Prometheus 指标 HTTP 服务器
    start_http_server(9966)
    # 设置指标
    setup_metrics()
    # 设置报警
    setup_alerting(test_mode)
    logger.info("监控模块已启动，Prometheus 指标可在 http://localhost:9966 访问")
