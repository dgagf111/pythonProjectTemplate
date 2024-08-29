import config.config as config
import importlib
from log.logHelper import get_logger

"""
全局日志实例使用说明：

1. 获取日志实例：
   已在文件顶部创建全局日志实例 `logger = get_logger()`，整个应用程序中都可以直接使用这个 `logger` 对象。

2. 日志级别：
   - logger.debug(): 用于详细的调试信息，通常只在诊断问题时使用
   - logger.info(): 用于确认一切按预期运行
   - logger.warning(): 用于表示可能出现的问题，但程序仍在正常工作
   - logger.error(): 用于记录更严重的问题，可能导致程序的某些功能无法正常工作
   - logger.critical(): 用于记录严重的错误，可能导致程序崩溃或无法继续运行

3. 使用示例：
   logger.info("应用程序启动")
   logger.debug(f"当前配置: {config}")
   logger.warning("配置文件未找到，使用默认配置")
   logger.error("数据库连接失败")
   logger.critical("严重错误：应用程序即将关闭")

4. 日志格式：
   默认格式为：'时间戳 - 日志名称 - 日志级别 - 日志消息'

5. 日志文件：
   日志会同时输出到控制台和文件。文件路径通常为：'../log/项目名/年份/年-月/年-月-日.log'

6. 注意事项：
   - 避免在日志消息中包含敏感信息（如密码、个人身份信息等）
   - 对于大量重复的日志，考虑使用更低的日志级别或减少日志频率
   - 在处理异常时，推荐使用 logger.exception()，它会自动包含堆栈跟踪信息
"""

# 获取全局日志实例
logger = get_logger()

# 加载并运行模块
def load_and_run_modules():
    logger.info("开始加载和运行模块")
    module_config = config.get_module_config()
    module_names = module_config.get('modules', [])
    base_path = module_config.get('base_path', 'modules')
    
    for module_name in module_names:
        try:
            # 构造模块的完整路径
            module_path = f"{base_path}.{module_name}.main"
            logger.debug(f"尝试导入模块: {module_path}")
            module = importlib.import_module(module_path)
            
            # 检查模块是否有 run 方法
            if hasattr(module, 'run') and callable(module.run):
                logger.info(f"运行模块: {module_name}")
                module.run()
            else:
                logger.warning(f"模块 {module_name} 没有 'run' 方法。")
        except ImportError as e:
            logger.error(f"导入模块 {module_name} 时出错: {e}")
        except Exception as e:
            logger.error(f"运行模块 {module_name} 时出错: {e}")

    logger.info("所有模块加载和运行完成")

# 主程序入口
if __name__ == "__main__":
    logger.info("主程序开始运行")
    try:
        load_and_run_modules()
    except Exception as e:
        logger.critical(f"主程序运行时发生严重错误: {e}", exc_info=True)
    logger.info("主程序运行结束")
