import pytest
import os
import sys

# 将项目根目录添加到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from log.logHelper import get_logger

logger = get_logger()

# Set environment variable for testing
# os.environ['ENV'] = 'test'

def run_all_tests():
    """运行所有测试"""
    logger.info("开始运行所有测试...")
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 使用 pytest.main() 运行测试，包括所有子目录
    pytest.main(['-v', '--tb=short', '-s', test_dir])
    
    logger.info("所有测试运行完成")

if __name__ == "__main__":
    run_all_tests()
