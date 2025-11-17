import socket
import threading
from wsgiref.simple_server import make_server

from prometheus_client import make_wsgi_app

from pythonprojecttemplate.config.settings import settings
from pythonprojecttemplate.log.logHelper import get_logger

from .alerting import setup_alerting, check_cpu_usage, check_memory_usage
from .prometheus_exporter import setup_metrics

logger = get_logger()


class MonitoringCenter:
    def __init__(self):
        self.running = False
        self.alert_thread = None
        self.should_exit = threading.Event()
        self.http_server = None
        self.http_thread = None
        self.metrics_port = settings.monitoring.prometheus_port

    def start(self, test_mode: bool = False):
        if self.running:
            logger.warning("监控中心已经在运行")
            return

        logger.info("启动监控模块...")
        try:
            port = self._select_port(settings.monitoring.prometheus_port)
            self._start_metrics_server(port)
            setup_metrics()
            self.running = True
            self.should_exit.clear()

            if not test_mode:
                self.alert_thread = threading.Thread(target=self._run_alerting, daemon=True)
                self.alert_thread.start()
            logger.info(f"监控模块已启动，Prometheus 指标可在 http://localhost:{self.metrics_port} 访问")
        except Exception as e:
            logger.error(f"监控模块启动失败: {e}", exc_info=True)

    def _select_port(self, preferred_port: int) -> int:
        if self._is_port_available(preferred_port):
            return preferred_port
        return self._find_available_port()

    def _start_metrics_server(self, port: int) -> None:
        app = make_wsgi_app()
        self.http_server = make_server("127.0.0.1", port, app)
        self.metrics_port = port
        self.http_thread = threading.Thread(target=self.http_server.serve_forever, daemon=True)
        self.http_thread.start()

    def _is_port_available(self, port):
        """检查端口是否可用"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('localhost', port))
                return True
        except OSError:
            return False

    def _find_available_port(self):
        """查找可用端口"""
        for port in range(9967, 9999):
            if self._is_port_available(port):
                return port
        return settings.monitoring.prometheus_port

    def _run_alerting(self):
        setup_alerting()
        while not self.should_exit.is_set():
            try:
                check_cpu_usage()
                check_memory_usage()
            except Exception as e:
                logger.error(f"告警检查失败: {e}")

            if self.should_exit.wait(timeout=60):
                break

    def shutdown(self):
        logger.info("正在关闭监控模块...")
        self.should_exit.set()
        self.running = False

        if self.alert_thread and self.alert_thread.is_alive():
            self.alert_thread.join(timeout=2)

        if self.http_server:
            self.http_server.shutdown()
            self.http_server.server_close()
            self.http_server = None

        if self.http_thread and self.http_thread.is_alive():
            self.http_thread.join(timeout=2)
        self.http_thread = None
        self.alert_thread = None
        self.should_exit = threading.Event()
        logger.info("监控模块已关闭")


monitoring_center = MonitoringCenter()
