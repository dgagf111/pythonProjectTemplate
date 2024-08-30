import pytest
import os
import sys
import argparse

# 将项目根目录添加到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from log.logHelper import get_logger

logger = get_logger()

def run_framework_tests():
    """运行框架测试"""
    logger.info("开始运行框架测试...")
    framework_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'framework')
    pytest.main(['-v', '--tb=short', '-s', framework_dir])
    logger.info("框架测试运行完成")

def run_business_tests():
    """运行业务测试"""
    logger.info("开始运行业务测试...")
    business_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'business')
    pytest.main(['-v', '--tb=short', '-s', business_dir])
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
    args = parser.parse_args()

    if args.test_type == "all":
        run_all_tests()
    elif args.test_type == "framework":
        run_framework_tests()
    elif args.test_type == "business":
        run_business_tests()
