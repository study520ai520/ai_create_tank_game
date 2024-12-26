import pygame
from pygame.sprite import Sprite
from ..config import Config
import random
import math
import os
import sys

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.append(project_root)

class PowerUp(Sprite):
    def __init__(self, x, y, powerup_type, resource_manager):
        super().__init__()
        self.type = powerup_type
        self.resource_manager = resource_manager
        
        # 从资源管理器获取图像
        self.image = self.resource_manager.get_image('powerup', powerup_type)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # 从配置获取属性
        powerup_config = Config.POWERUP_TYPES[powerup_type]
        self.duration = powerup_config['duration']
        self.color = powerup_config['color']
        self.symbol = powerup_config['symbol']
        
        # 动画效果
        self.original_y = y
        self.float_offset = 0
        self.spawn_time = pygame.time.get_ticks()
        
        # ���出现音效
        self.resource_manager.play_sound('powerup_appear')

    def update(self, current_time):
        """更新道具状态"""
        # 浮动动画
        self.float_offset += 0.1
        self.rect.centery = self.original_y + int(math.sin(self.float_offset) * 5)
        
        # 检查道具是否应该消失
        if current_time - self.spawn_time >= Config.POWERUP_DURATION:
            self.kill()

    def apply(self, tank, current_time):
        """应用道具效果"""
        if self.type == 'base_shield':
            # 基地加固道具直接作用于游戏管理器
            tank.game_manager.apply_base_shield(current_time)
        else:
            # 其他道具作用于坦克
            tank.add_powerup(self.type, current_time)
        self.kill()  # 使用后消失

class PowerUpManager:
    def __init__(self, resource_manager):
        self.resource_manager = resource_manager
        self.powerups = pygame.sprite.Group()
        self.last_spawn_time = 0
        self.spawn_delay = 20000  # 20秒
        
    def spawn_powerup(self, current_time, walls):
        """生成新的道具"""
        if current_time - self.last_spawn_time < self.spawn_delay:
            return
            
        if random.random() < Config.POWERUP_SPAWN_CHANCE:
            # 随机选择道具类型
            powerup_types = ['shield', 'speed', 'rapid_fire', 'base_shield']
            powerup_type = random.choice(powerup_types)
            
            # 随机选择位置（确保不与墙体重叠）
            while True:
                x = random.randint(0, Config.SCREEN_WIDTH - 32)
                y = random.randint(0, Config.SCREEN_HEIGHT - 32)
                temp_rect = pygame.Rect(x, y, 32, 32)
                
                collision = False
                for wall in walls:
                    if temp_rect.colliderect(wall.rect):
                        collision = True
                        break
                
                if not collision:
                    break
            
            # 创建新道具
            powerup = PowerUp(x, y, powerup_type, self.resource_manager)
            self.powerups.add(powerup)
            self.last_spawn_time = current_time
            
    def update(self, current_time):
        """更新所有道具"""
        self.powerups.update(current_time)
        
    def check_collision(self, tank, current_time):
        """检查与玩家的碰撞"""
        collided = pygame.sprite.spritecollide(tank, self.powerups, True)
        for powerup in collided:
            powerup.apply(tank, current_time)
