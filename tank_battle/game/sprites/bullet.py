import pygame
from pygame.sprite import Sprite
from ..config import Config

class Bullet(Sprite):
    """子弹类"""
    def __init__(self, x, y, direction, resource_manager, tank_type, owner):
        super().__init__()
        self.resource_manager = resource_manager
        self.tank_type = tank_type  # player 或 enemy
        self.owner = owner
        self.direction = direction
        
        # 加载图像
        image_key = f"{tank_type}_{direction}"
        self.image = self.resource_manager.get_image('bullet', image_key)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # 设置速度
        if tank_type == 'player':
            self.speed = Config.PLAYER_BULLET_SPEED
        else:
            self.speed = Config.ENEMY_BULLET_SPEED
            
    def update(self, current_time):
        """更新子弹位置"""
        # 移动子弹
        if self.direction == 'up':
            self.rect.y -= self.speed
        elif self.direction == 'down':
            self.rect.y += self.speed
        elif self.direction == 'left':
            self.rect.x -= self.speed
        elif self.direction == 'right':
            self.rect.x += self.speed
            
        # 检查是否超出屏幕
        if (self.rect.bottom < 0 or self.rect.top > Config.SCREEN_HEIGHT or
            self.rect.right < 0 or self.rect.left > Config.SCREEN_WIDTH):
            self.kill()
            return
            
        # 获取游戏管理器
        game_manager = self.owner.game_manager
        
        # 检查碰撞
        # 检查与地形的碰撞
        terrain_hits = pygame.sprite.spritecollide(self, game_manager.terrain_group, False)
        for terrain in terrain_hits:
            # 对于地形，除了钢铁和水外都可以被摧毁
            if terrain.type != 'steel' and terrain.type != 'water' and terrain.type != 'grass':
                terrain.kill()
                # 如果是基地被摧毁，触发游戏结束
                if terrain.type == 'base':
                    game_manager.game_over = True
                    game_manager.game_over_reason = 'base_destroyed'
            # 除了草地外，子弹都会消失
            if terrain.type != 'grass':
                self.kill()
                return
            
        # 检查与坦克的碰撞
        if self.tank_type == 'player':
            # 玩家子弹检查与敌人的碰撞
            enemy_hits = pygame.sprite.spritecollide(self, game_manager.enemy_group, False)
            for enemy in enemy_hits:
                if enemy.hit(current_time):
                    self.kill()
                return
        else:
            # 敌人子弹检查与玩家的碰撞
            player_hits = pygame.sprite.spritecollide(self, game_manager.player_group, False)
            for player in player_hits:
                if player.hit(current_time):
                    self.kill()
                return
