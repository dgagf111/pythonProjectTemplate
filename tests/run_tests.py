import pytest
import os
import sys
import argparse

# 将项目根目录添加到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from log.logHelper import get_logger

logger = get_logger()

def run_framework_tests(module=None):
    """运行框架测试"""
    logger.info(f"开始运行框架测试{'（' + module + '）' if module else ''}...")
    framework_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'framework')
    
    if module:
        test_path = os.path.join(framework_dir, module)
        if not os.path.exists(test_path):
            logger.error(f"指定的模块 '{module}' 不存在")
            return
    else:
        test_path = framework_dir

    pytest.main(['-v', '--tb=short', '-s', test_path])

    logger.info("框架测试运行完成")

def run_business_tests(module=None):
    """运行业务测试"""
    logger.info(f"开始运行业务测试{'（' + module + '）' if module else ''}...")
    business_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'business')
    
    if module:
        test_path = os.path.join(business_dir, module)
        if not os.path.exists(test_path):
            logger.error(f"指定的模块 '{module}' 不存在")
            return
    else:
        test_path = business_dir

    pytest.main(['-v', '--tb=short', '-s', test_path])

    logger.info("业务测试运行完成")

def run_all_tests():
    """运行所有测试"""
    logger.info("开始运行所有测试...")
    run_framework_tests()
    run_business_tests()
    logger.info("所有测试运行完成")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="运行测试脚本")
    parser.add_argument("test_type", choices=["all", "framework", "business"], help="指定要运行的测试类型")
    parser.add_argument("--module", help="指定要测试的模块（适用于 framework 和 business 测试类型）")
    args = parser.parse_args()

    if args.test_type == "all":
        run_all_tests()
    elif args.test_type == "framework":
        run_framework_tests(args.module)
    elif args.test_type == "business":
        run_business_tests(args.module)
