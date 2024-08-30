import pytest
import requests
import time
from monitoring.main import monitoring_center
from monitoring.prometheus_exporter import REQUEST_COUNT, RESPONSE_TIME, CPU_USAGE, MEMORY_USAGE
from monitoring.alerting import check_cpu_usage, check_memory_usage
from unittest.mock import patch
from log.logHelper import get_logger

logger = get_logger()

@pytest.fixture(scope="module")
def monitoring_setup():
    # 启动监控模块，使用测试模式
    monitoring_center.start(test_mode=True)
    # 等待服务器启动
    time.sleep(2)
    yield
    # 这里可以添加清理代码，如果需要的话

def test_prometheus_server(monitoring_setup):
    # 测试 Prometheus 服务器是否正常运行
    response = requests.get("http://localhost:9966")
    assert response.status_code == 200

def test_metrics_creation():
    # 测试指标是否被正确创建
    print(f"REQUEST_COUNT._name: {REQUEST_COUNT._name}")
    assert REQUEST_COUNT._name == "app_requests", "REQUEST_COUNT 名称不正确"
    assert RESPONSE_TIME._name == "app_response_latency_seconds"
    assert CPU_USAGE._name == "system_cpu_usage"
    assert MEMORY_USAGE._name == "system_memory_usage"

def test_metrics_update():
    # 测试指标更新
    initial_count = REQUEST_COUNT._value.get()
    REQUEST_COUNT.inc()
    assert REQUEST_COUNT._value.get() == initial_count + 1

    RESPONSE_TIME.observe(0.1)
    assert RESPONSE_TIME._sum.get() > 0

@patch('psutil.cpu_percent')
@patch('psutil.virtual_memory')
def test_system_metrics_update(mock_memory, mock_cpu):
    # 模拟系统指标
    mock_cpu.return_value = 50.0
    mock_memory.return_value.percent = 60.0

    # 更新系统指标
    CPU_USAGE.set(mock_cpu.return_value)
    MEMORY_USAGE.set(mock_memory.return_value.percent)

    assert CPU_USAGE._value.get() == 50.0
    assert MEMORY_USAGE._value.get() == 60.0

@patch('monitoring.alerting.logger.warning')
def test_alerting(mock_logger):
    # 测试 CPU 使用率报警
    assert not check_cpu_usage(threshold=90)  # 不触发报警
    mock_logger.assert_not_called()

    assert check_cpu_usage(threshold=80)  # 应触发报警
    mock_logger.assert_called_with("CPU 使用率过高: 85%")

    # 重置 mock
    mock_logger.reset_mock()

    # 测试内存使用率报警
    check_memory_usage(threshold=80)
    mock_logger.assert_not_called()

    check_memory_usage(threshold=70)
    mock_logger.assert_called_with("内存使用率过高: 75%")
