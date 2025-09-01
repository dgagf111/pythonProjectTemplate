#!/usr/bin/env python3
"""
主程序入口

新的标准化项目结构主程序入口，支持：
- 标准的Python包结构
- 统一的配置和日志管理
- 模块化启动
"""

import sys
import os
import signal
import asyncio
import threading
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from pythonprojecttemplate.core import config, get_logger
    from pythonprojecttemplate.api import create_app
    # 导入其他核心模块
    from scheduler.scheduler_center import scheduler_center
    from monitoring.main import monitoring_center
    import importlib
except ImportError as e:
    print(f"导入错误: {e}")
    print(f"当前 sys.path: {sys.path}")
    sys.exit(1)

# 获取全局日志实例
logger = get_logger()

def load_and_run_modules():
    """加载并运行模块"""
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
    """优雅关闭"""
    logger.info("开始优雅关闭...")
    try:
        scheduler_center.shutdown()
        monitoring_center.shutdown()
        logger.info("应用程序已关闭")
    except Exception as e:
        logger.error(f"关闭过程中出现错误: {e}")
    finally:
        os._exit(0)  # 使用 os._exit() 强制退出

def signal_handler(signum, frame):
    """信号处理器"""
    logger.info(f"接收到信号: {signal.Signals(signum).name}")
    threading.Thread(target=lambda: asyncio.run(graceful_shutdown())).start()

def run_web_server():
    """运行Web服务器"""
    import uvicorn
    
    # 创建FastAPI应用
    app = create_app()
    
    # 获取API配置
    api_config = config.get_api_config()
    host = api_config.get('host', '0.0.0.0')
    port = api_config.get('port', 8000)
    
    logger.info(f"启动Web服务器，地址: {host}:{port}")
    
    # 运行服务器
    uvicorn.run(app, host=host, port=port, log_config=None)

def run_scheduler_and_monitoring():
    """运行调度器和监控"""
    try:
        logger.info("应用程序启动")
        
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

def main():
    """主函数"""
    import argparse
    
    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Python Project Template')
    parser.add_argument('--mode', choices=['web', 'scheduler', 'all'], default='all',
                       help='运行模式：web(仅Web服务)、scheduler(仅调度器)、all(全部)')
    parser.add_argument('--test', action='store_true', help='运行测试')
    
    args = parser.parse_args()
    
    if args.test:
        # 运行测试
        import subprocess
        subprocess.run(["python", "tests/run_tests.py", "all"])
        return
    
    if args.mode == 'web':
        run_web_server()
    elif args.mode == 'scheduler':
        run_scheduler_and_monitoring()
    else:  # all
        # 在单独的线程中运行调度器和监控
        scheduler_thread = threading.Thread(target=run_scheduler_and_monitoring)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        # 在主线程中运行Web服务器
        run_web_server()

if __name__ == "__main__":
    main()