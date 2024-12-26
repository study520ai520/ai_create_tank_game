import os
import sys

def create_resource_dirs():
    # 获取当前脚本所在目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 创建资源目录
    resource_dirs = [
        os.path.join(base_dir, 'resources'),
        os.path.join(base_dir, 'resources', 'images'),
        os.path.join(base_dir, 'resources', 'sounds')
    ]
    
    for dir_path in resource_dirs:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"Created directory: {dir_path}")
        else:
            print(f"Directory already exists: {dir_path}")

if __name__ == "__main__":
    create_resource_dirs()
