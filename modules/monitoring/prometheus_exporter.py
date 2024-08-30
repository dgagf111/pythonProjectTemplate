from prometheus_client import Counter, Gauge, Histogram
import psutil

# 定义一些示例指标
REQUEST_COUNT = Counter('app_requests_total', 'Total app HTTP requests')
RESPONSE_TIME = Histogram('app_response_latency_seconds', 'Response latency in seconds')
CPU_USAGE = Gauge('system_cpu_usage', 'Current CPU usage')
MEMORY_USAGE = Gauge('system_memory_usage', 'Current memory usage')

def setup_metrics():
    # 这里可以添加更多的指标设置
    pass

def record_request():
    REQUEST_COUNT.inc()

def record_response_time(latency):
    RESPONSE_TIME.observe(latency)

def update_system_metrics():
    CPU_USAGE.set(psutil.cpu_percent())
    MEMORY_USAGE.set(psutil.virtual_memory().percent)
