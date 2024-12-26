import os
import pygame
from ..config import Config
import random
import math

class ResourceManager:
    def __init__(self):
        """初始化资源管理器"""
        # 初始化资源字典
        self.images = {}
        self.sounds = {}
        self.fonts = {}
        
        # 获取项目根目录
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.resources_dir = os.path.join(self.base_dir, 'resources')
        self.images_dir = os.path.join(self.resources_dir, 'images')
        self.sounds_dir = os.path.join(self.resources_dir, 'sounds')
        self.fonts_dir = os.path.join(self.resources_dir, 'fonts')
        
        # 确保资源目录存在
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.sounds_dir, exist_ok=True)
        os.makedirs(self.fonts_dir, exist_ok=True)
        
        print(f"Resource Manager initialized with resources directory: {self.resources_dir}")
        
        # 加载图像资源
        self._load_images()
        self._load_sounds()
        self._load_fonts()
        
    def _load_images(self):
        """加载所有图像"""
        # 加载坦克和子弹图像
        self._load_tank_images()
        self._load_bullet_images()
        
        # 加载地形图像
        self._load_terrain_images()
        
        # 加载道具图像
        self._load_powerup_images()
        
    def _load_tank_images(self):
        """加载坦克图像"""
        tank_size = Config.TILE_SIZE
        
        # 为每种类型的坦克创建图像
        tank_types = {
            'player': {
                'body': (34, 177, 76),  # 深绿色
                'turret': (28, 145, 62),  # 更深的绿色
                'track': (20, 100, 45)  # 履带颜色
            },
            'normal': {
                'body': (200, 40, 40),  # 红色
                'turret': (170, 30, 30),
                'track': (150, 25, 25)
            },
            'fast': {
                'body': (255, 165, 0),  # 橙色
                'turret': (230, 140, 0),
                'track': (200, 120, 0)
            },
            'heavy': {
                'body': (128, 128, 128),  # 灰色
                'turret': (100, 100, 100),
                'track': (80, 80, 80)
            },
            'elite': {
                'body': (148, 0, 211),  # 紫色
                'turret': (128, 0, 181),
                'track': (108, 0, 151)
            }
        }
        
        # 为每种类型的坦克创建四个方向的图像
        directions = ['up', 'right', 'down', 'left']
        angles = [0, 270, 180, 90]
        
        for tank_type, colors in tank_types.items():
            for direction, angle in zip(directions, angles):
                # 创建透明背景的surface
                image = pygame.Surface((tank_size, tank_size), pygame.SRCALPHA)
                
                # 绘制履带
                track_width = 6
                pygame.draw.rect(image, colors['track'], (0, 0, track_width, tank_size))  # 左履带
                pygame.draw.rect(image, colors['track'], (tank_size-track_width, 0, track_width, tank_size))  # 右履带
                
                # 绘制坦克主体
                body_rect = pygame.Rect(track_width, 4, tank_size-2*track_width, tank_size-8)
                pygame.draw.rect(image, colors['body'], body_rect)
                
                # 绘制炮塔
                turret_size = 16
                turret_rect = pygame.Rect((tank_size-turret_size)//2, (tank_size-turret_size)//2,
                                        turret_size, turret_size)
                pygame.draw.rect(image, colors['turret'], turret_rect)
                
                # 绘制炮管
                barrel_width = 4
                barrel_length = 20
                barrel_rect = pygame.Rect((tank_size-barrel_width)//2, 0,
                                        barrel_width, barrel_length)
                pygame.draw.rect(image, colors['turret'], barrel_rect)
                
                # 旋转图像
                if angle != 0:
                    image = pygame.transform.rotate(image, angle)
                
                # 保存图像
                key = f'tank_{tank_type}_{direction}'
                self.images[key] = image
                
                # 保存到文件（可选）
                image_path = os.path.join(self.images_dir, f'{tank_type}_{direction}.png')
                pygame.image.save(image, image_path)
                print(f"Created tank image: {key}")
                
    def _load_bullet_images(self):
        """创建子弹图像"""
        bullet_size = (8, 8)
        
        # 玩家子弹 - 黄色
        player_color = (255, 255, 0)  # 黄色
        for direction in ['up', 'down', 'left', 'right']:
            surface = pygame.Surface(bullet_size, pygame.SRCALPHA)
            pygame.draw.circle(surface, player_color, (4, 4), 4)
            self.images[f'bullet_player_{direction}'] = surface
            
        # 敌人子弹 - 白色
        enemy_color = (255, 255, 255)  # 白色
        for direction in ['up', 'down', 'left', 'right']:
            surface = pygame.Surface(bullet_size, pygame.SRCALPHA)
            pygame.draw.circle(surface, enemy_color, (4, 4), 4)
            self.images[f'bullet_enemy_{direction}'] = surface
            
        print("Created bullet images")
        
    def _create_terrain_image(self, terrain_type):
        """创建地形图像"""
        image = pygame.Surface((Config.TILE_SIZE, Config.TILE_SIZE), pygame.SRCALPHA)
        tile_size = Config.TILE_SIZE
        
        if terrain_type == 'brick':
            # 砖墙 - 更精细的砖块纹理
            brick_color = (180, 80, 50)  # 砖红色
            dark_brick = (160, 70, 45)   # 深色砖
            mortar_color = (140, 140, 140)  # 浅灰色砂浆
            
            brick_width = 8
            brick_height = 4
            gap = 1  # 砂浆间隙
            
            for row in range(0, tile_size, brick_height):
                offset = (row // brick_height % 2) * (brick_width // 2)
                for col in range(-offset, tile_size, brick_width):
                    if 0 <= col < tile_size:
                        # 砖块主体
                        brick_rect = pygame.Rect(col, row, brick_width-gap, brick_height-gap)
                        pygame.draw.rect(image, brick_color, brick_rect)
                        
                        # 砖块阴影效果
                        pygame.draw.line(image, dark_brick, 
                                      (col, row+brick_height-gap-1),
                                      (col+brick_width-gap, row+brick_height-gap-1))
                        pygame.draw.line(image, dark_brick,
                                      (col+brick_width-gap-1, row),
                                      (col+brick_width-gap-1, row+brick_height-gap))
                        
                        # 砂浆
                        if col > 0:
                            pygame.draw.line(image, mortar_color,
                                          (col-1, row),
                                          (col-1, row+brick_height-gap))
                        pygame.draw.line(image, mortar_color,
                                      (col, row+brick_height-gap),
                                      (col+brick_width-gap, row+brick_height-gap))
            
        elif terrain_type == 'steel':
            # 钢铁墙 - 金属板效果
            base_color = (160, 160, 160)    # 基础灰色
            light_color = (200, 200, 200)   # 高光色
            dark_color = (120, 120, 120)    # 阴影色
            bolt_color = (80, 80, 80)       # 螺���色
            
            # 主体金属板
            pygame.draw.rect(image, base_color, (0, 0, tile_size, tile_size))
            
            # 边缘高光和阴影
            pygame.draw.rect(image, light_color, (0, 0, tile_size, 2))  # 上边缘高光
            pygame.draw.rect(image, light_color, (0, 0, 2, tile_size))  # 左边缘高光
            pygame.draw.rect(image, dark_color, (0, tile_size-2, tile_size, 2))  # 下边缘阴影
            pygame.draw.rect(image, dark_color, (tile_size-2, 0, 2, tile_size))  # 右边缘阴影
            
            # 中央凸起
            center_rect = pygame.Rect(8, 8, tile_size-16, tile_size-16)
            pygame.draw.rect(image, light_color, center_rect)
            pygame.draw.rect(image, base_color, center_rect.inflate(-2, -2))
            
            # 螺栓
            bolt_positions = [(6, 6), (tile_size-6, 6), 
                            (6, tile_size-6), (tile_size-6, tile_size-6)]
            for x, y in bolt_positions:
                pygame.draw.circle(image, bolt_color, (x, y), 3)  # 螺栓外圈
                pygame.draw.circle(image, light_color, (x-1, y-1), 1)  # 螺栓高光
            
        elif terrain_type == 'water':
            # 水 - 动态波纹效果
            colors = [
                (0, 120, 255, 180),  # 浅蓝色（半透明��
                (0, 100, 220, 180),  # 中蓝色（半透明）
                (0, 80, 200, 180)    # 深蓝色（半透明）
            ]
            
            # 基础水面
            pygame.draw.rect(image, colors[0], (0, 0, tile_size, tile_size))
            
            # 波纹效果
            wave_height = 4
            for i in range(4):
                y_offset = i * 8
                for x in range(0, tile_size, 4):
                    y = int(math.sin(x * 0.2) * wave_height) + y_offset
                    if 0 <= y < tile_size-wave_height:
                        wave_rect = pygame.Rect(x, y, 4, wave_height)
                        pygame.draw.rect(image, colors[1], wave_rect)
                        pygame.draw.rect(image, colors[2], wave_rect.inflate(-1, -1))
            
        elif terrain_type == 'grass':
            # 草地 - 自然草丛效果
            dark_green = (34, 139, 34)    # 深绿色
            forest_green = (40, 160, 40)  # 森林绿
            lime_green = (50, 205, 50)    # 浅绿色
            
            # 基础草地
            pygame.draw.rect(image, forest_green, (0, 0, tile_size, tile_size))
            
            # 随机草丛
            for _ in range(60):
                x = random.randint(0, tile_size-1)
                y = random.randint(0, tile_size-1)
                color = random.choice([dark_green, lime_green])
                length = random.randint(3, 7)
                width = random.randint(1, 2)
                angle = random.uniform(-0.5, 0.5)
                end_x = x + math.sin(angle) * length
                end_y = y - math.cos(angle) * length
                pygame.draw.line(image, color, (x, y), (end_x, end_y), width)
            
        elif terrain_type == 'base':
            # 基地 - 精致的鹰形标志
            gold = (218, 165, 32)      # 金色
            dark_gold = (184, 134, 11) # 深金色
            highlight = (255, 215, 0)  # 高光金色
            
            # 基础形状 - 盾牌
            center = tile_size // 2
            shield_points = [
                (center, 4),
                (28, 12),
                (28, 28),
                (4, 28),
                (4, 12)
            ]
            
            # 盾牌主体
            pygame.draw.polygon(image, gold, shield_points)
            pygame.draw.polygon(image, dark_gold, shield_points, 2)
            
            # 鹰的翅膀 - 更细致的设计
            left_wing = [
                (center-2, 14),
                (8, 18),
                (10, 22),
                (center-1, 20)
            ]
            right_wing = [
                (center+2, 14),
                (24, 18),
                (22, 22),
                (center+1, 20)
            ]
            
            # 绘制翅膀
            pygame.draw.polygon(image, dark_gold, left_wing)
            pygame.draw.polygon(image, dark_gold, right_wing)
            pygame.draw.polygon(image, highlight, left_wing, 1)
            pygame.draw.polygon(image, highlight, right_wing, 1)
            
            # 鹰的头部和装饰
            pygame.draw.circle(image, dark_gold, (center, 12), 3)  # 头部
            pygame.draw.circle(image, highlight, (center-1, 11), 1)  # 眼睛高光
            
            # 装饰性边框
            for i in range(2):
                smaller_shield = [(x + (1 if x < center else -1) * i,
                                 y + (1 if y > center else -1) * i)
                                for x, y in shield_points]
                pygame.draw.polygon(image, highlight, smaller_shield, 1)
            
        return image
        
    def _load_terrain_images(self):
        """加载地形图像"""
        for terrain_type in Config.TERRAIN_TYPES.keys():
            # 创建地形图像
            image = self._create_terrain_image(terrain_type)
            
            # 保存到内存
            self.images[f'terrain_{terrain_type}'] = image
            
            # 保存到文件（可选）
            image_path = os.path.join(self.images_dir, f'terrain_{terrain_type}.png')
            pygame.image.save(image, image_path)
            print(f"Created terrain image: {terrain_type}")
        
    def _create_default_powerup_images(self):
        """创建默认的道具图像"""
        powerup_size = Config.POWERUP_SIZE
        
        # 道具类型及其颜色
        powerup_colors = {
            'shield': (0, 255, 255),    # 青色
            'speed': (255, 255, 0),     # 黄色
            'rapid_fire': (255, 0, 0),  # 红色
            'base_shield': (192, 192, 192),  # 银色
        }
        
        for powerup_type, color in powerup_colors.items():
            # 创建基础surface
            surface = pygame.Surface((powerup_size, powerup_size), pygame.SRCALPHA)
            
            # 绘制道具外框（圆形）
            pygame.draw.circle(surface, color, (powerup_size//2, powerup_size//2), powerup_size//2)
            
            # 根据道具类型绘制不同的图标
            if powerup_type == 'shield':
                # 盾牌图标
                shield_points = [
                    (powerup_size//2, 4),  # 顶点
                    (powerup_size-4, powerup_size//2),  # 右点
                    (powerup_size//2, powerup_size-4),  # 底点
                    (4, powerup_size//2),  # 左点
                ]
                pygame.draw.polygon(surface, (255, 255, 255), shield_points)
                
            elif powerup_type == 'speed':
                # 闪电图标
                lightning_points = [
                    (powerup_size//2, 4),  # 顶点
                    (powerup_size-6, powerup_size//2),  # 右上
                    (powerup_size//2, powerup_size//2),  # 中点
                    (6, powerup_size-4),  # 左上
                ]
                pygame.draw.polygon(surface, (255, 255, 255), lightning_points)
                
            elif powerup_type == 'rapid_fire':
                # 子弹图标
                bullet_radius = 3
                for i in range(3):
                    x = powerup_size//2
                    y = 6 + i * 6
                    pygame.draw.circle(surface, (255, 255, 255), (x, y), bullet_radius)
                    
            elif powerup_type == 'base_shield':
                # 基地加固图标 - 小城堡形状
                castle_color = (255, 255, 255)  # 白色
                # 主体
                pygame.draw.rect(surface, castle_color, 
                               (powerup_size//4, powerup_size//2, 
                                powerup_size//2, powerup_size//3))
                # 塔楼
                pygame.draw.rect(surface, castle_color,
                               (powerup_size//3, powerup_size//4,
                                powerup_size//3, powerup_size//2))
                # 塔尖
                castle_top = [
                    (powerup_size//3, powerup_size//4),  # 左
                    (powerup_size//2, powerup_size//6),  # 顶
                    (2*powerup_size//3, powerup_size//4)  # 右
                ]
                pygame.draw.polygon(surface, castle_color, castle_top)
            
            # 保存图像
            self.images[f'powerup_{powerup_type}'] = surface
            
        print("Created powerup images")
        
    def _load_powerup_images(self):
        """加载道具图像"""
        self._create_default_powerup_images()
        
    def _load_sounds(self):
        """加载音效"""
        # 暂时禁用音效加载
        pass
        
    def _load_fonts(self):
        """加载字体"""
        try:
            # 尝试使用系统自带的中文字体
            font_path = "C:/Windows/Fonts/simhei.ttf"  # 黑体
            if not os.path.exists(font_path):
                font_path = "C:/Windows/Fonts/msyh.ttc"  # 微软雅黑
            
            self.fonts = {
                'small': pygame.font.Font(font_path, 16),
                'medium': pygame.font.Font(font_path, 24),
                'large': pygame.font.Font(font_path, 32)
            }
            print("Loaded custom fonts")
        except Exception as e:
            print(f"Error loading custom fonts: {e}")
            # 如果加载失败，使用系统默认字体
            self.fonts = {
                'small': pygame.font.SysFont(None, 16),
                'medium': pygame.font.SysFont(None, 24),
                'large': pygame.font.SysFont(None, 32)
            }
            print("Using system default fonts")
        
    def get_image(self, image_type, name):
        """获取图像"""
        if image_type == 'tank':
            key = f'tank_{name}'
        elif image_type == 'bullet':
            key = f'bullet_{name}'
        elif image_type == 'terrain':
            key = f'terrain_{name}'
        elif image_type == 'powerup':
            key = f'powerup_{name}'
        else:
            key = name
            
        if key not in self.images:
            print(f"Warning: Image {key} not found!")
            # 返回一个默认的紫色方块作为缺失图像的标记
            surface = pygame.Surface((32, 32))
            surface.fill((255, 0, 255))
            return surface
            
        return self.images[key]
            
    def get_font(self, size):
        """获取指定大小的字体"""
        return self.fonts[size]
        
    def play_sound(self, sound_name):
        """播放音效"""
        # 暂时禁用音效播放
        pass
