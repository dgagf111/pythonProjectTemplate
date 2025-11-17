import pytest
import requests
import time
from pythonprojecttemplate.monitoring.main import monitoring_center
from pythonprojecttemplate.monitoring.prometheus_exporter import REQUEST_COUNT, RESPONSE_TIME, CPU_USAGE, MEMORY_USAGE
from pythonprojecttemplate.monitoring.alerting import check_cpu_usage, check_memory_usage
from unittest.mock import patch
from pythonprojecttemplate.log.logHelper import get_logger

logger = get_logger()

@pytest.fixture(scope="module")
def monitoring_setup():
    monitoring_center.start(test_mode=True)
    time.sleep(1)
    if not monitoring_center.running:
        pytest.skip("监控模块无法在当前环境中启动网络服务")
    yield monitoring_center
    monitoring_center.shutdown()

def test_prometheus_server(monitoring_setup):
    response = requests.get(f"http://localhost:{monitoring_setup.metrics_port}")
    assert response.status_code == 200

def test_metrics_creation():
    assert REQUEST_COUNT._name == "app_requests"
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

@patch('pythonprojecttemplate.monitoring.alerting.logger.warning')
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
