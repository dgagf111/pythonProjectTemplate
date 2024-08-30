# 监控模块说明文档

## 概述

监控模块提供了一个基于Prometheus的监控系统，用于收集和导出应用程序的各种指标。该模块包括指标收集、HTTP服务器和报警功能。

## 主要组件

### 1. Prometheus导出器 (prometheus_exporter.py)

该组件定义了要收集的指标并提供了更新这些指标的方法。

主要指标包括：

* 请求计数 (`app_requests_total`)
* 响应时间 (`app_response_latency_seconds`)
* CPU使用率 (`system_cpu_usage`)
* 内存使用率 (`system_memory_usage`)

### 2. 报警系统 (alerting.py)

该组件负责检查系统指标并在超过阈值时发出警报。

主要功能：

* CPU使用率检查
* 内存使用率检查

### 3. 主运行模块 (main.py)

该模块负责启动Prometheus HTTP服务器、设置指标和初始化报警系统。

## 配置

监控模块的配置在 `config/dev.yaml` 文件中定义：

## 测试

监控模块的测试文件位于 `tests/framework/monitoring/test_monitoring.py`。测试覆盖了以下方面：

* Prometheus服务器的运行状态
* 指标的创建和更新
* 系统指标的更新
* 报警功能

## 注意事项

1. 确保在使用监控模块之前已安装所有必要的依赖，特别是 `prometheus_client` 和 `psutil`。
2. 监控服务器默认在9966端口运行，请确保该端口可用。
3. 在生产环境中使用时，建议根据实际需求调整报警阈值和检查频率。
4. 对于大规模部署，可能需要考虑使用外部Prometheus服务器来收集和存储指标数据。