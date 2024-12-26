#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Config:
    """游戏配置"""
    # 屏幕设置
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    WINDOW_WIDTH = SCREEN_WIDTH + 150  # 增加HUD显示区域
    WINDOW_HEIGHT = SCREEN_HEIGHT
    FPS = 60
    
    # 颜色设置
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (192, 192, 192)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    
    # 游戏设置
    TILE_SIZE = 40  # 地形块大小
    TANK_SIZE = 40  # 坦克大小（与地形块大小相同）
    BULLET_SIZE = 8  # 子弹大小
    POWERUP_SIZE = 20  # 道具大小
    INITIAL_SHIELD_DURATION = 3000  # 初始无敌时间（3秒）
    
    # 网格设置
    GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE
    GRID_HEIGHT = SCREEN_HEIGHT // TILE_SIZE
    
    # 网格位置转换
    @staticmethod
    def snap_to_grid(x, y):
        """将坐标对齐到网格"""
        grid_x = round(x / Config.TILE_SIZE) * Config.TILE_SIZE
        grid_y = round(y / Config.TILE_SIZE) * Config.TILE_SIZE
        return grid_x, grid_y
        
    @staticmethod
    def get_grid_pos(x, y):
        """获取网格坐标"""
        return x // Config.TILE_SIZE, y // Config.TILE_SIZE
    
    # 关卡设置
    MAX_LEVEL = 5
    ENEMIES_PER_LEVEL = 5  # 每关的敌人数量
    MAX_ENEMIES_ON_SCREEN = 4  # 屏幕上最大敌人数量
    ENEMY_SPAWN_DELAY = 3000  # 敌人生成延迟（毫秒）
    LEVEL_CONFIGS = {
        1: {
            "enemies": 5,
            "terrain_density": 0.1,
            "enemy_types": {"normal": 0.7, "fast": 0.3, "heavy": 0, "elite": 0}
        },
        2: {
            "enemies": 8,
            "terrain_density": 0.15,
            "enemy_types": {"normal": 0.5, "fast": 0.3, "heavy": 0.2, "elite": 0}
        },
        3: {
            "enemies": 10,
            "terrain_density": 0.2,
            "enemy_types": {"normal": 0.4, "fast": 0.3, "heavy": 0.2, "elite": 0.1}
        },
        4: {
            "enemies": 12,
            "terrain_density": 0.25,
            "enemy_types": {"normal": 0.3, "fast": 0.3, "heavy": 0.2, "elite": 0.2}
        },
        5: {
            "enemies": 15,
            "terrain_density": 0.3,
            "enemy_types": {"normal": 0.2, "fast": 0.3, "heavy": 0.2, "elite": 0.3}
        }
    }
    
    # 游戏规则
    POINTS_PER_ENEMY = 100  # 每消灭一个敌人获得的分数
    POINTS_FOR_LEVEL_UP = 500  # 每过一关奖励的分数
    POINTS_PER_POWERUP = 50  # 拾取道具获得的分数
    
    # 玩家设置
    PLAYER_SPEED = 4
    PLAYER_BULLET_SPEED = 8
    PLAYER_SHOOT_DELAY = 500  # 毫秒
    PLAYER_LIVES = 3
    PLAYER_HEALTH = 3
    PLAYER_SPAWN_X = 3  # 玩家出生点X坐标（格子数）
    PLAYER_SPAWN_Y = 13  # 玩家出生点Y坐标（从顶部数第13格，接近底部）
    
    # 敌人设置
    ENEMY_SPEED = 3
    ENEMY_BULLET_SPEED = 6
    ENEMY_SHOOT_DELAY = 1000  # 毫秒
    ENEMY_TYPES = {
        'normal': {
            'speed': 3,
            'bullet_speed': 8,
            'shoot_delay': 1000,
            'health': 1,
            'points': 100
        },
        'fast': {
            'speed': 6,
            'bullet_speed': 10,
            'shoot_delay': 1200,
            'health': 1,
            'points': 200
        },
        'heavy': {
            'speed': 2,
            'bullet_speed': 6,
            'shoot_delay': 1500,
            'health': 3,
            'points': 300
        },
        'elite': {
            'speed': 4,
            'bullet_speed': 12,
            'shoot_delay': 800,
            'health': 2,
            'points': 500
        }
    }
    
    # 地形设置
    TERRAIN_TYPES = {
        'brick': {
            'health': 1,
            'color': (210, 105, 30),  # 砖红色
            'destructible': True
        },
        'steel': {
            'health': 4,
            'color': (169, 169, 169),  # 钢铁色
            'destructible': False
        },
        'water': {
            'health': 999999,  # 不可摧毁
            'color': (0, 191, 255),  # 深天蓝
            'destructible': False
        },
        'grass': {
            'health': 999999,  # 不可摧毁
            'color': (34, 139, 34),  # 森林绿
            'destructible': False
        },
        'base': {
            'health': 1,
            'color': (255, 215, 0),  # 金色
            'destructible': True
        }
    }
    
    # 道具设置
    POWERUP_DROP_CHANCE = 0.3  # 道具掉落概率
    POWERUP_DURATION = 10000   # 道具持续时间（毫秒）
    POWERUP_SPAWN_CHANCE = 0.1  # 10%概率
    SHIELD_DURATION = 5000  # 毫秒
    SPEED_BOOST_DURATION = 10000  # 毫秒
    RAPID_FIRE_DURATION = 10000  # 毫秒
    BASE_SHIELD_DURATION = 15000  # 基地加固持续时间（毫秒）
    
    # 效果倍率
    SPEED_BOOST_MULTIPLIER = 1.5  # 速度提升倍数
    RAPID_FIRE_MULTIPLIER = 2.0  # 射速提升倍数
    
    # 碰撞设置
    TANK_SPACING = TANK_SIZE + 10  # 坦克之间的最小间距
    
    # 道具类型
    POWERUP_TYPES = {
        'shield': {
            'duration': SHIELD_DURATION,
            'color': (0, 191, 255),  # 深天蓝
            'symbol': 'P'
        },
        'speed': {
            'duration': SPEED_BOOST_DURATION,
            'color': (0, 255, 0),  # 绿色
            'symbol': 'S'
        },
        'rapid_fire': {
            'duration': RAPID_FIRE_DURATION,
            'color': (255, 255, 0),  # 黄色
            'symbol': 'R'
        },
        'base_shield': {
            'duration': BASE_SHIELD_DURATION,
            'color': (192, 192, 192),  # 银色
            'symbol': 'B'
        }
    }
