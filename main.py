import config.config as config
import importlib    

# 加载并运行模块
def load_and_run_modules(module_names='', base_path='modules'):
    module_names = config.get_module_config()['modules']
    base_path = config.get_module_config()['base_path']
    
    for module_name in module_names:
        try:
            # 构造模块的完整路径
            module_path = f"{base_path}.{module_name}.main"
            module = importlib.import_module(module_path)
            
            # 检查模块是否有 run 方法
            if hasattr(module, 'run') and callable(module.run):
                module.run()
            else:
                print(f"Module {module_name} does not have a 'run' method.")
        except ImportError as e:
            print(f"Error loading module {module_name}: {e}")
        except Exception as e:
            print(f"Error running module {module_name}: {e}")

# 在项目中通常默认是直接运行main.py文件的
if __name__ == "__main__":
    load_and_run_modules()
