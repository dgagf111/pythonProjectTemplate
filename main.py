import config.config as config

# 在项目中通常默认是直接运行main.py文件的
if __name__ == "__main__":
    # 加载模块
    for module_name, module in config.load_modules().items():
        print(f"Loaded module: {module_name}")
        # 你可以在这里调用模块中的函数或类
        # 例如: module.some_function()