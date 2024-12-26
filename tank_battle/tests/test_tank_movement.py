import os
import sys
import logging
import pygame

# 设置日志级别
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from game.sprites.tank import PlayerTank
from game.config import Config
from game.input_handler import InputHandler
from game.resources.resource_manager import ResourceManager

def main():
    """测试玩家坦克移动"""
    # 初始化 Pygame
    pygame.init()
    pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
    resource_manager = ResourceManager()
    
    # 创建玩家坦克
    player = PlayerTank(100, 100, resource_manager)
    terrain_group = pygame.sprite.Group()
    
    # 测试向右移动
    initial_x = player.rect.x
    keys = InputHandler.create_key_state(right=True)
    logger.info(f"测试向右移动 - 初始位置: ({player.rect.x}, {player.rect.y})")
    
    # 第一次调用应该会转向
    player.handle_input(keys, terrain_group)
    logger.info(f"转向后方向: {player.direction}")
    
    # 第二次调用应该会移动
    player.handle_input(keys, terrain_group)
    logger.info(f"移动后位置: ({player.rect.x}, {player.rect.y})")
    
    # 验证结果
    success = player.rect.x > initial_x
    print(f"测试结果: {'成功' if success else '失败'}")
    print(f"初始位置: {initial_x}, 当前位置: {player.rect.x}")
    
    # 清理
    pygame.quit()
    
    return success

if __name__ == '__main__':
    main()
