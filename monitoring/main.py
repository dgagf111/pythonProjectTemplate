from prometheus_client import start_http_server
from .prometheus_exporter import setup_metrics
from .alerting import setup_alerting
from log.logHelper import get_logger
import threading
import time
import socket

logger = get_logger()

class MonitoringCenter:
    def __init__(self):
        self.running = False
        self.thread = None
        self.should_exit = threading.Event()
        self.http_server = None

    def start(self, test_mode=False):
        if self.running:
            logger.warning("监控中心已经在运行")
            return

        logger.info("启动监控模块...")
        try:
            # 检查端口是否可用
            port = 9966
            if not self._is_port_available(port):
                port = self._find_available_port()
            
            start_http_server(port)
            setup_metrics()
            self.running = True
            
            if not test_mode:
                self.thread = threading.Thread(target=self._run_alerting, daemon=True)
                self.thread.start()
            logger.info(f"监控模块已启动，Prometheus 指标可在 http://localhost:{port} 访问")
        except Exception as e:
            logger.error(f"监控模块启动失败: {e}")
    
    def _is_port_available(self, port):
        """检查端口是否可用"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('localhost', port))
                return True
        except:
            return False
    
    def _find_available_port(self):
        """查找可用端口"""
        for port in range(9967, 9999):
            if self._is_port_available(port):
                return port
        return 9966  # 默认端口

    def _run_alerting(self):
        while not self.should_exit.is_set():
            try:
                setup_alerting()
            except Exception as e:
                logger.error(f"告警检查失败: {e}")
            
            # 使用wait而不sleep，以便可以被中断
            if self.should_exit.wait(timeout=60):
                break

    def shutdown(self):
        logger.info("正在关闭监控模块...")
        self.should_exit.set()
        self.running = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        
        self.thread = None
        logger.info("监控模块已关闭")

monitoring_center = MonitoringCenter()
