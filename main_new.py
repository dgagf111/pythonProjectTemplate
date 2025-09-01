#!/usr/bin/env python3
"""
兼容性入口文件

为了保持向后兼容性，这个文件提供了从根目录启动应用的入口。
实际功能由 src/pythonprojecttemplate/main.py 实现。
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# 导入并运行新的主程序
try:
    from pythonprojecttemplate.main import main
    
    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"无法导入新的主程序: {e}")
    print("正在尝试使用旧的启动方式...")
    
    # 兼容旧的启动方式
    try:
        from config.config import config
        import importlib
        from log.logHelper import get_logger
        from scheduler.scheduler_center import scheduler_center
        import signal
        from monitoring.main import monitoring_center
        import asyncio
        import threading
        from fastapi import FastAPI, Request
        from api.api_router import api_router
        from api.exception.custom_exceptions import APIException
        from fastapi.responses import JSONResponse
        from api.http_status import HTTPStatus
        from api.models.result_vo import ResultVO
        import uvicorn

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

        async def graceful_shutdown():
            logger.info("开始优雅关闭...")
            scheduler_center.shutdown()
            monitoring_center.shutdown()
            logger.info("应用程序已关闭")
            os._exit(0)  # 使用 os._exit() 强制退出

        def signal_handler(signum, frame):
            logger.info(f"接收到信号: {signal.Signals(signum).name}")
            threading.Thread(target=lambda: asyncio.run(graceful_shutdown())).start()

        def main_legacy():
            try:
                logger.info("应用程序启动（兼容模式）")
                
                # 启动调度中心
                scheduler_center.start()
                logger.info("调度中心已启动")

                # 启动监控中心
                monitoring_center.start()
                logger.info("监控中心已启动")

                # 加载并运行模块
                load_and_run_modules()

                # 使用 signal.pause() 等待信号
                logger.info("主程序进入等待状态，按 Ctrl+C 或发送 SIGTERM 信号来停止服务")
                signal.pause()
            except Exception as e:
                logger.error(f"启动过程中发生错误: {e}")
            finally:
                asyncio.run(graceful_shutdown())

        app = FastAPI()

        # 全局异常处理
        @app.exception_handler(Exception)
        async def global_exception_handler(request: Request, e: Exception):
            logger.error(f"捕获到全局异常: {e}", exc_info=True)
            return ResultVO.error(
                code=HTTPStatus.INTERNAL_SERVER_ERROR.code,
                message=str(e)
            )

        # 包含 API 路由器
        app.include_router(api_router)

        # 其他应用设置...
        if len(sys.argv) > 1 and sys.argv[1] == "test":
            # 如果传入 "test" 参数，只运行测试
            import subprocess
            subprocess.run(["python", "tests/run_tests.py", "all"])
        else:
            # 否则，正常启动应用
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            uvicorn.run(app, host="0.0.0.0", port=8000)
            main_legacy()
            
    except ImportError as e2:
        print(f"兼容性启动也失败了: {e2}")
        print("请检查项目依赖是否正确安装")
        sys.exit(1)