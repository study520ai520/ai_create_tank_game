import os
import sys

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from tank_battle.game.game_manager import GameManager
from tank_battle.game.resources.resource_manager import ResourceManager
import pygame

def main():
    # 初始化 Pygame
    pygame.init()
    
    # 创建游戏窗口
    screen = pygame.display.set_mode((950, 600))  # 800x600 游戏区域 + 150 HUD区域
    pygame.display.set_caption("坦克大战")
    
    # 创建资源管理器
    resource_manager = ResourceManager()
    
    # 创建游戏管理器
    game_manager = GameManager(screen, resource_manager)
    
    # 运行游戏
    game_manager.run()

if __name__ == "__main__":
    main()