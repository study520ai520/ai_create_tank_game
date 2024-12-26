#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
from pygame.sprite import Sprite
from ..config import Config
from .bullet import Bullet
import random

class Tank(Sprite):
    def __init__(self, x, y, resource_manager, tank_type, game_manager):
        super().__init__()
        self.resource_manager = resource_manager
        self.tank_type = tank_type
        self.game_manager = game_manager
        self.direction = 'up'
        
        # 加载图像
        self.images = {}
        for direction in ['up', 'down', 'left', 'right']:
            self.images[direction] = self.resource_manager.get_image('tank', f'{tank_type}_{direction}')
        self.image = self.images[self.direction]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # 设置属性
        if tank_type == 'player':
            self.speed = Config.PLAYER_SPEED
            self.bullet_speed = Config.PLAYER_BULLET_SPEED
            self.shoot_delay = Config.PLAYER_SHOOT_DELAY
        else:
            self.speed = Config.ENEMY_SPEED
            self.bullet_speed = Config.ENEMY_BULLET_SPEED
            self.shoot_delay = Config.ENEMY_SHOOT_DELAY
            
        # 射击相关
        self.last_shot = 0
        self.shield_end_time = 0
        self.rapid_fire_end_time = 0
        self.speed_boost_end_time = 0
        
        # 道具状态
        self.visible = True
        
    def update(self, current_time):
        """更新坦克状态"""
        if self.tank_type == 'player':
            self.update_player(current_time)
        else:
            self.update_enemy(current_time)
            
        # 更新道具状态
        self.update_powerups(current_time)
        
        # 更新无敌状态闪烁效果
        if self.shield_end_time > current_time:
            # 每100毫秒切换一次可见性
            self.visible = (current_time // 100) % 2 == 0
        else:
            self.visible = True
            
        # 检查与道具的碰撞（只对玩家坦克生效）
        if self.tank_type == 'player':
            powerup_hits = pygame.sprite.spritecollide(self, self.game_manager.powerup_group, True)
            for powerup in powerup_hits:
                powerup.apply(self, current_time)
                self.game_manager.score += Config.POINTS_PER_POWERUP  # 拾取道具加分
            
        # 检查碰撞
        for other_tank in self.game_manager.player_group.sprites() + self.game_manager.enemy_group.sprites():
            if other_tank != self and self.rect.colliderect(other_tank.rect):
                # 如果是玩家和敌人相撞
                if (self.tank_type == 'player' and other_tank.tank_type != 'player') or \
                   (self.tank_type != 'player' and other_tank.tank_type == 'player'):
                    # 两者都死亡
                    self.kill()
                    other_tank.kill()
                    if self.tank_type == 'player':
                        self.game_manager.handle_player_death()
                    else:
                        self.game_manager.handle_enemy_death(self)
                    if other_tank.tank_type == 'player':
                        self.game_manager.handle_player_death()
                    else:
                        self.game_manager.handle_enemy_death(other_tank)
                    break
                # 如果是敌人之间相撞
                elif self.tank_type != 'player' and other_tank.tank_type != 'player':
                    # 返回原位置并改变方向
                    self.rect.x = self.old_x
                    self.rect.y = self.old_y
                    self.direction = random.choice(['up', 'down', 'left', 'right'])
                    break
            
        # 根据可见性设置图像
        if self.visible:
            self.image = self.images[self.direction]
        else:
            # 创建一个透明的surface
            self.image = pygame.Surface((Config.TANK_SIZE, Config.TANK_SIZE), pygame.SRCALPHA)
            
    def draw(self, surface):
        """绘制坦克"""
        if self.visible:
            surface.blit(self.image, self.rect)
            
    def move(self, direction=None, speed=None):
        """移动坦克"""
        if direction is None:
            direction = self.direction
        if speed is None:
            speed = self.get_current_speed()
        
        # 记录原始位置
        self.old_x = self.rect.x
        self.old_y = self.rect.y
        
        # 根据方向移动
        if direction == 'up':
            self.rect.y -= speed
        elif direction == 'down':
            self.rect.y += speed
        elif direction == 'left':
            self.rect.x -= speed
        elif direction == 'right':
            self.rect.x += speed
            
        # 检查是否超出屏幕边界
        if (self.rect.left < 0 or 
            self.rect.right > Config.SCREEN_WIDTH or 
            self.rect.top < 0 or 
            self.rect.bottom > Config.SCREEN_HEIGHT):
            self.rect.x = self.old_x
            self.rect.y = self.old_y
            return False
            
        # 检查碰撞
        if self.game_manager.check_tank_collision(self, self.rect.x, self.rect.y):
            self.rect.x = self.old_x
            self.rect.y = self.old_y
            return False
            
        # 更新方向和图像
        self.direction = direction
        self.image = self.images[direction]
        return True
        
    def update_player(self, current_time):
        """更新玩家坦克"""
        # 获取按键状态
        keys = pygame.key.get_pressed()
        speed = self.get_current_speed()
        
        # 移动
        moved = False
        if keys[pygame.K_UP]:
            moved = self.move('up', speed)
        elif keys[pygame.K_DOWN]:
            moved = self.move('down', speed)
        elif keys[pygame.K_LEFT]:
            moved = self.move('left', speed)
        elif keys[pygame.K_RIGHT]:
            moved = self.move('right', speed)
            
        # 射击
        if keys[pygame.K_SPACE]:
            self.shoot(current_time)
            
    def update_enemy(self, current_time):
        """更新敌人坦克"""
        # 记录当前位置
        old_x = self.rect.x
        old_y = self.rect.y
        
        # 移动
        moved = self.move()
        
        # 如果移动失败（碰到障碍物），随机��择新方向
        if not moved:
            # 恢复原位置
            self.rect.x = old_x
            self.rect.y = old_y
            # 选择新方向，避免选择当前方向
            available_directions = ['up', 'down', 'left', 'right']
            available_directions.remove(self.direction)
            self.direction = random.choice(available_directions)
            # 尝试新方向移动
            self.move()
        
        # 随机改变方向（降低频率，从2%改为1%）
        if random.random() < 0.01:
            available_directions = ['up', 'down', 'left', 'right']
            available_directions.remove(self.direction)  # 避免选择当前方向
            self.direction = random.choice(available_directions)
        
        # 随机射击（保持5%概率）
        if random.random() < 0.05:
            self.shoot(current_time)
            
    def shoot(self, current_time):
        """发射子弹"""
        # 检查射击冷却
        if current_time - self.last_shot < self.get_shoot_delay():
            return False
            
        # 计算子弹生成位置
        if self.direction == 'up':
            bullet_x = self.rect.centerx
            bullet_y = self.rect.top
        elif self.direction == 'down':
            bullet_x = self.rect.centerx
            bullet_y = self.rect.bottom
        elif self.direction == 'left':
            bullet_x = self.rect.left
            bullet_y = self.rect.centery
        else:  # right
            bullet_x = self.rect.right
            bullet_y = self.rect.centery
            
        # 创建子弹
        bullet = Bullet(
            bullet_x,
            bullet_y,
            self.direction,
            self.resource_manager,
            'player' if self.tank_type == 'player' else 'enemy',
            self
        )
        
        # 将子弹添加到精灵组
        self.game_manager.bullet_group.add(bullet)
        self.game_manager.all_sprites.add(bullet)
        
        # 更新最后射击时间
        self.last_shot = current_time
        return True
        
    def take_damage(self):
        """受到伤害"""
        if pygame.time.get_ticks() < self.shield_end_time:
            return False  # 护盾有效，不受伤害
            
        self.health -= 1
        if self.health <= 0:
            self.kill()
            return True  # 坦克被摧毁
        return False  # 坦克存活
        
    def add_powerup(self, powerup_type, current_time):
        """添加道具效果"""
        if powerup_type == 'shield':
            self.shield_end_time = current_time + Config.SHIELD_DURATION
        elif powerup_type == 'speed':
            self.speed_boost_end_time = current_time + Config.SPEED_BOOST_DURATION
        elif powerup_type == 'rapid_fire':
            self.rapid_fire_end_time = current_time + Config.RAPID_FIRE_DURATION
            
    def update_powerups(self, current_time):
        """更新道具状态"""
        # 道具时间到期后自动失效
        if current_time >= self.shield_end_time:
            self.shield_end_time = 0
        if current_time >= self.speed_boost_end_time:
            self.speed_boost_end_time = 0
        if current_time >= self.rapid_fire_end_time:
            self.rapid_fire_end_time = 0
            
    def get_current_speed(self):
        """获取当前速度（考虑道具加成）"""
        if pygame.time.get_ticks() < self.speed_boost_end_time:
            return self.speed * Config.SPEED_BOOST_MULTIPLIER
        return self.speed
        
    def get_shoot_delay(self):
        """获取当前射击延迟（考虑道具加成）"""
        if pygame.time.get_ticks() < self.rapid_fire_end_time:
            return self.shoot_delay / Config.RAPID_FIRE_MULTIPLIER
        return self.shoot_delay

    def hit(self, current_time):
        """被击中"""
        if self.tank_type == 'player':
            if current_time < self.shield_end_time:
                return False  # 护盾有效，不受伤害
            self.game_manager.lives -= 1
            if self.game_manager.lives > 0:
                # 重生在基地左边3个单元格的位置
                self.rect.centerx = (Config.GRID_WIDTH // 2 - 3) * Config.TILE_SIZE
                self.rect.bottom = Config.SCREEN_HEIGHT - Config.TILE_SIZE
                self.direction = 'right'  # 朝向右边
                self.image = self.images[self.direction]
                self.shield_end_time = current_time + Config.SHIELD_DURATION
            else:
                self.kill()
        else:
            # 敌人被击中直接消失
            self.game_manager.handle_enemy_death(self)
            
        return True
