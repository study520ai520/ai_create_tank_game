import pygame
from pygame.sprite import Sprite
from ..config import Config

class Terrain(Sprite):
    """地形精灵类"""
    def __init__(self, x, y, terrain_type, resource_manager):
        super().__init__()
        self.type = terrain_type
        self.resource_manager = resource_manager
        
        # 从资源管理器获取图像
        self.image = self.resource_manager.get_image('terrain', terrain_type)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # 从配置获取属性
        terrain_config = Config.TERRAIN_TYPES[terrain_type]
        self.health = terrain_config['health']
        self.destructible = terrain_config['destructible']
        
    def update(self, current_time):
        """更新地形状态"""
        pass  # 地形是静态的，不需要更新

    def take_damage(self):
        """受到伤害"""
        if not self.destructible:
            return False
            
        self.health -= 1
        if self.health <= 0:
            self.kill()
            return True
        return False
