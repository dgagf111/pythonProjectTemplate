# 配置文件管理

## 配置文件结构

本项目使用 YAML 文件来管理配置。主要的配置文件包括：

1. 项目根目录下的 `env.yaml`
2. `config` 文件夹内的环境特定 YAML 文件（如 `dev.yaml`、`test.yaml`、`prod.yaml`）

## 配置文件关系

1. `env.yaml` 中的 `env` 属性决定了要加载哪个环境特定的 YAML 文件。
2. 环境特定的 YAML 文件（如 `dev.yaml`）包含了该环境下的详细配置。

## 使用 Config 类管理配置

项目使用 `Config` 类来统一管理配置文件的读取。以下是如何使用 `Config` 类的说明：

1. 导入 Config 类：

‍`python from config.config import config ‍`

2. 获取配置：

* 获取环境配置：
  ‍`python env_config = config.get_env_config() ‍`
* 获取主配置：
  ‍`python main_config = config.get_config() ‍`
* 获取特定配置：
  ‍`python mysql_config = config.get_mysql_config() log_config = config.get_log_config() module_config = config.get_module_config() scheduler_config = config.get_scheduler_config() tasks_config = config.get_tasks_config() ‍`

3. 使用配置：

```python
# 示例：获取 MySQL 配置

mysql_config = config.get_mysql_config()
username = mysql_config['username']
password = mysql_config['password']
host = mysql_config['host']
port = mysql_config['port']
database = mysql_config['database']

# 示例：获取日志配置

log_config = config.get_log_config()
log_level = log_config.get('log_level', 'INFO')
```

通过使用 `Config` 类，您可以在整个项目中统一管理和访问配置，无需直接读取 YAML 文件。这种方法提供了更好的封装和灵活性，使配置管理更加简单和可维护。

## 添加新配置

当需要添加新的配置项时，请遵循以下步骤：

1. 在相应的 YAML 文件中添加新的配置项。
2. 在 `config.py` 文件中的 `Config` 类中添加相应的获取方法。

例如，如果要添加一个新的 Redis 配置：

1. 在 `dev.yaml`（或其他环境配置文件）中添加：

‍`yaml redis:   host: localhost   port: 6379   db: 0 ‍`

2. 在 `config.py` 中的 `Config` 类中添加新方法：

‍`python def get_redis_config(self) -> Dict[str, Any]:     """获取 Redis 配置"""     return self._config.get('redis', {}) ‍`

3. 现在可以在项目中使用新的配置：

‍`python redis_config = config.get_redis_config() redis_host = redis_config['host'] ‍`

## 最佳实践

* 保持配置文件的结构清晰和有组织。
* 使用注释来解释复杂或不明显的配置项。
* 对敏感信息（如密码）使用环境变量，而不是直接在配置文件中硬编码。
* 定期审查和更新配置文件，移除未使用的配置项。
* 使用版本控制来跟踪配置文件的变化，但注意不要将包含敏感信息的文件提交到公共仓库。

通过遵循这些指南，您可以有效地管理项目的配置，提高代码的可维护性和安全性。