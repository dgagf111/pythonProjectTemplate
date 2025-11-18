# 修复方案：代码质量审查问题

本文档记录在代码质量审查中识别出的关键问题及对应修复方案，供开发与评审参考。

## 1. 数据库会话管理失效
- **位置**：`src/pythonprojecttemplate/core/utils.py:140`
- **问题**：`DatabaseUtils.get_db_session` 以同步生成器形式返回 `MySQL_Database.get_session`（其本身是异步生成器，见 `src/pythonprojecttemplate/db/mysql/mysql.py:20`），并在 `except/finally` 中直接调用 `session.rollback()/close()`。由于缺少 `await`，依赖该工具的调用方会得到一个未执行的协程对象，异常路径还会抛出 `'async_generator' object has no attribute rollback/close'`，导致连接池资源无法释放。
- **修复建议**：
  1. 将 `get_db_session` 改写为 `async def`，内部 `async with AsyncSessionLocal() as session:`。
  2. 捕获异常后 `await session.rollback()`，`finally` 中 `await session.close()`。
  3. 更新依赖点（如 FastAPI Depends）以匹配异步依赖。
- **验证**：运行 `python tests/run_tests.py modules api` 并执行至少一次需要数据库依赖的 API 单元测试，确认无 runtime warning/未释放连接。

## 2. CacheFactory 无法加载 Redis 配置
- **位置**：`src/pythonprojecttemplate/cache/factory.py:32-63`
- **问题**：工厂从 `cache_config.get('host')` 等顶层键读取 Redis 参数，但 `AppSettings.cache` 的结构为 `{"redis": {...}}`（参考 `src/pythonprojecttemplate/config/dev.yaml:64-76`）。即便 YAML 或环境中配置了 Redis 主机/端口，工厂依旧退回默认值 `localhost:6379`，生产环境会连接错误实例。
- **修复建议**：
  1. 统一通过 `redis_cfg = cache_config.get("redis", {})` 取得 `host/port/db`。
  2. `create_redis_cache`、`create_cache_manager` 等处复用同一配置解析逻辑。
  3. 为 `redis_cfg` 缺失字段提供合理默认值，并在日志中输出选用的配置来源。
- **验证**：设置自定义环境变量（例如 `PPT_CACHE__REDIS__HOST`），运行 `python tests/run_tests.py modules cache`，并在日志中确认真正使用了自定义主机。

## 3. 永久令牌缺少 provider 隔离
- **位置**：`src/pythonprojecttemplate/api/api_router.py:210-217`、`src/pythonprojecttemplate/api/auth/token_service.py:120-149`、`src/pythonprojecttemplate/api/models/auth_models.py:35-78`
- **问题**：接口要求调用方传入 `provider`，但 `generate_permanent_token` 完全忽略该字段，`tokens` 表也没有 provider 列，校验方法仅根据 token 字符串定位记录。结果同一个永久 token 可以跨不同外部应用共享，难以实现按集成方吊销或审计。
- **修复建议**：
  1. 使用已有的 `ThirdPartyToken` 模型存储永久令牌，或在 `Token` 模型中新增 `provider` 字段。
  2. `generate_permanent_token` 写入 provider，并在 `verify_permanent_token` 校验时附加 `provider` 条件。
  3. 若迁移到 `ThirdPartyToken`，同步更新 Alembic/数据访问逻辑，并补充回滚策略。
- **验证**：编写针对 `provider` 的集成测试（或扩展 `tests/api`），确保不同 provider 的 token 互不影响。

## 4. 刷新令牌接口错误码不当
- **位置**：`src/pythonprojecttemplate/api/api_router.py:85-120`
- **问题**：`/refresh` 接口仅有一个 `except Exception` 分支，任何异常（包括 `InvalidTokenException`、`TokenRevokedException` 等客户端错误）都被映射为 500。客户端无法区分凭据问题与服务器故障，监控也会出现大量误报。
- **修复建议**：
  1. 显式捕获认证相关异常并返回 `HTTPStatus.UNAUTHORIZED` 或 `HTTPStatus.FORBIDDEN`。
  2. 在未知异常时保留 500，但增加 `exc_info=True` 以便排查。
  3. 根据需要调整 `ResultVO.error` 的 message，使客户端可据此触发重新登录。
- **验证**：为刷新接口添加单元测试，构造无效 token、被吊销 token 和正常 token 三种路径，确保响应码与日志符合预期。

---

完成以上修复后，建议运行以下命令验证整体稳定性：
```bash
python tests/run_tests.py modules api config
pytest tests -v --strict-markers
```
