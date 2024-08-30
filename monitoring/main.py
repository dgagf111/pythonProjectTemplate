from prometheus_client import start_http_server
from .prometheus_exporter import setup_metrics
from .alerting import setup_alerting
from log.logHelper import get_logger
import threading

logger = get_logger()

class MonitoringCenter:
    def __init__(self):
        self.running = False
        self.thread = None

    def start(self, test_mode=False):
        if self.running:
            logger.warning("监控中心已经在运行")
            return

        logger.info("启动监控模块...")
        start_http_server(9966)
        setup_metrics()
        self.running = True
        if not test_mode:
            self.thread = threading.Thread(target=self._run_alerting)
            self.thread.start()
        logger.info("监控模块已启动，Prometheus 指标可在 http://localhost:9966 访问")

    def _run_alerting(self):
        setup_alerting()

    def shutdown(self):
        if not self.running:
            logger.warning("监控中心未在运行")
            return

        logger.info("正在关闭监控模块...")
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("监控模块已关闭")

monitoring_center = MonitoringCenter()
