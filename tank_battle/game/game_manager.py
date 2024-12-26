from .sprites.tank import Tank
from .sprites.terrain import Terrain
from .ui.button import Button
from .config import Config
from .resources.resource_manager import ResourceManager
from .sprites.powerup import PowerUp
import pygame
import random

class GameManager:
    def __init__(self, screen, resource_manager):
        """初始化游戏管理器"""
        self.screen = screen
        self.resource_manager = resource_manager
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = 'MENU'  # MENU, PLAYING, GAME_OVER
        
        # 游戏数据
        self.score = 0
        self.current_level = 1
        self.lives = Config.PLAYER_LIVES
        self.enemies_remaining = Config.ENEMIES_PER_LEVEL
        self.last_enemy_spawn = 0
        
        # 创建精灵组
        self.all_sprites = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.bullet_group = pygame.sprite.Group()
        self.terrain_group = pygame.sprite.Group()
        self.powerup_group = pygame.sprite.Group()
        
        # ���建按钮
        button_width = 200
        button_height = 50
        button_x = (Config.WINDOW_WIDTH - button_width) // 2
        start_y = Config.WINDOW_HEIGHT // 2 - button_height
        quit_y = Config.WINDOW_HEIGHT // 2 + button_height
        
        self.start_button = Button(
            button_x, start_y, button_width, button_height,
            "开始游戏", self.start_game,
            self.resource_manager.fonts['medium']
        )
        self.quit_button = Button(
            button_x, quit_y, button_width, button_height,
            "退出游戏", self.quit_game,
            self.resource_manager.fonts['medium']
        )
        
        # 尝试加载中文字体，如果失败则使用默认字体
        try:
            self.font_path = "C:/Windows/Fonts/msyh.ttc"  # 微软雅黑
            # 测试字体是否可用
            test_font = pygame.font.Font(self.font_path, 12)
        except:
            self.font_path = pygame.font.get_default_font()
            
        # 初始化字体
        self.font = pygame.font.Font(self.font_path, 36)
        self.title_font = pygame.font.Font(self.font_path, 74)
        button_font = pygame.font.Font(self.font_path, 32)
        
        # 创建游戏结束界面的按钮
        self.restart_button = Button(
            button_x,
            Config.SCREEN_HEIGHT * 2 // 3,
            button_width,
            button_height,
            '重新开始',
            lambda: self.restart_game(),  # 使用lambda避免立即调用
            button_font
        )
        
        self.menu_button = Button(
            button_x,
            Config.SCREEN_HEIGHT * 2 // 3 + button_height + 20,
            button_width,
            button_height,
            '返回菜单',
            lambda: self.return_to_menu(),  # 使用lambda避免立即调用
            button_font
        )
        
        self.game_over = False
        self.game_over_reason = None
        self.base_shield_end_time = 0  # 添加基地加固结束时间
        self.base_walls = []  # 存储基地周围的墙
        
    def restart_game(self):
        """重新开始游戏"""
        self.game_over = False
        self.game_over_reason = None
        self.start_game()
        
    def return_to_menu(self):
        """返回主菜单"""
        self.game_over = False
        self.game_over_reason = None
        self.game_state = 'MENU'
        self.clear_all_sprites()
        
    def start_game(self):
        """开始新游戏"""
        self.clear_all_sprites()
        self.game_state = 'PLAYING'
        self.score = 0
        self.current_level = 1
        self.lives = Config.PLAYER_LIVES
        self.enemies_remaining = Config.ENEMIES_PER_LEVEL
        self.init_level()

    def init_level(self):
        """初始化关卡"""
        # 清空所有精灵组
        self.clear_all_sprites()
        
        # 设置关卡参数
        level_config = Config.LEVEL_CONFIGS[self.current_level]
        self.enemies_remaining = level_config["enemies"]
        
        # 创建玩家
        self.create_player()
        
        # 创建地形
        self.create_terrain(level_config["terrain_density"])
        
        # 创建基地
        self.create_base()
        
        # 创建初始敌人
        self.create_initial_enemies(level_config)
        
        # 开始定期生成敌人
        self.last_enemy_spawn = pygame.time.get_ticks()
        
    def create_player(self, respawn=False):
        """创建玩家坦克"""
        # 玩家初始位置（从底部数第二格）
        player_x = Config.PLAYER_SPAWN_X * Config.TILE_SIZE
        player_y = Config.SCREEN_HEIGHT - 2 * Config.TILE_SIZE
        
        # 创建玩家坦克
        player = Tank(
            player_x, 
            player_y, 
            self.resource_manager,
            'player',
            self
        )
        
        # 如果是复活，给予短暂的无敌时间
        if respawn:
            player.shield_end_time = pygame.time.get_ticks() + Config.INITIAL_SHIELD_DURATION
            
        self.player_group.add(player)
        self.all_sprites.add(player)
        
    def check_tank_collision(self, tank, x, y):
        """检查坦克碰撞"""
        # 创建临时矩形用于碰撞检测
        temp_rect = pygame.Rect(x, y, Config.TANK_SIZE, Config.TANK_SIZE)
        
        # 检查是否超出地图边界
        if (temp_rect.left < 0 or temp_rect.right > Config.SCREEN_WIDTH or
            temp_rect.top < 0 or temp_rect.bottom > Config.SCREEN_HEIGHT):
            return True
            
        # 检查与其他坦克的碰撞
        for other_tank in self.player_group.sprites() + self.enemy_group.sprites():
            if other_tank != tank and other_tank.rect.colliderect(temp_rect):
                return True
                
        # 检查与地形的碰撞（除了草地）
        for terrain in self.terrain_group:
            if terrain.type != 'grass' and terrain.rect.colliderect(temp_rect):
                return True
                
        return False
        
    def create_initial_enemies(self, level_config):
        """创建初始敌人"""
        # 在屏幕顶部随机位置生成敌人
        enemies_to_create = min(3, self.enemies_remaining)  # 最多同时生成3个敌人
        enemies_created = 0
        max_attempts_per_enemy = 10  # 每个敌人的最大尝试次数
        
        while enemies_created < enemies_to_create:
            # 随机选择敌人类型
            enemy_type = self.choose_enemy_type(level_config["enemy_types"])
            
            # 尝试找到合适的生成位置
            for _ in range(max_attempts_per_enemy):
                # 随机选择生成位置
                x = random.randint(0, Config.GRID_WIDTH - 1) * Config.TILE_SIZE
                y = 0
                
                # 创建临时矩形用于碰撞检测
                temp_rect = pygame.Rect(x, y, Config.TANK_SIZE, Config.TANK_SIZE)
                
                # 检查是否与地形碰撞（除了草地）
                collision = False
                for terrain in self.terrain_group:
                    if terrain.type != 'grass' and terrain.rect.colliderect(temp_rect):
                        collision = True
                        break
                        
                # 检查是否与其他坦克碰撞
                if not collision:
                    for tank in self.player_group.sprites() + self.enemy_group.sprites():
                        if tank.rect.colliderect(temp_rect):
                            collision = True
                            break
                
                # 如果没有碰撞，创建敌人
                if not collision:
                    enemy = Tank(x, y, self.resource_manager, enemy_type, self)
                    self.enemy_group.add(enemy)
                    self.all_sprites.add(enemy)
                    enemies_created += 1
                    break
                
    def choose_enemy_type(self, type_weights):
        """根据权重选择敌人类型"""
        types = list(type_weights.keys())
        weights = list(type_weights.values())
        return random.choices(types, weights=weights)[0]
        
    def create_enemy(self, x, y, enemy_type):
        """���建敌人坦克"""
        enemy = Tank(
            x,
            y,
            self.resource_manager,
            enemy_type,  # 使用具体的敌人类型（normal, fast, heavy, elite）
            self
        )
        self.enemy_group.add(enemy)
        self.all_sprites.add(enemy)
        
    def create_base(self):
        """创建基地"""
        # 基地位置：屏幕底部中央
        x = (Config.GRID_WIDTH // 2) * Config.TILE_SIZE
        y = (Config.GRID_HEIGHT - 1) * Config.TILE_SIZE
        
        # 创建基地
        self.base = Terrain(x, y, 'base', self.resource_manager)
        self.terrain_group.add(self.base)
        self.all_sprites.add(self.base)
        
        # 创建基地周围的砖墙保护
        wall_positions = [
            (x - Config.TILE_SIZE, y),  # 左
            (x + Config.TILE_SIZE, y),  # 右
            (x, y - Config.TILE_SIZE),  # 上
            (x - Config.TILE_SIZE, y - Config.TILE_SIZE),  # 左上
            (x + Config.TILE_SIZE, y - Config.TILE_SIZE),  # 右上
        ]
        
        self.base_walls = []  # 清空原有的墙列表
        for wall_x, wall_y in wall_positions:
            wall = Terrain(wall_x, wall_y, 'brick', self.resource_manager)
            self.terrain_group.add(wall)
            self.all_sprites.add(wall)
            self.base_walls.append(wall)  # 记录基地周围的墙
            
    def apply_base_shield(self, current_time):
        """应用基地加固效果"""
        # 设置基地加固结束时间
        self.base_shield_end_time = current_time + Config.BASE_SHIELD_DURATION
        
        # 将基地周围的墙转换为钢铁
        for wall in self.base_walls:
            if wall.alive():  # 如果墙还存在
                # 记录原位置
                x, y = wall.rect.x, wall.rect.y
                # 移除原有的墙
                wall.kill()
                # 创建新的钢铁墙
                steel_wall = Terrain(x, y, 'steel', self.resource_manager)
                self.terrain_group.add(steel_wall)
                self.all_sprites.add(steel_wall)
                # 更新墙的引用
                self.base_walls[self.base_walls.index(wall)] = steel_wall
                
    def update_base_shield(self, current_time):
        """更新基地加固状态"""
        if current_time >= self.base_shield_end_time and self.base_shield_end_time > 0:
            # 加固效果结束，恢复为砖墙
            for wall in self.base_walls:
                if wall.alive() and wall.type == 'steel':
                    # 记录原位置
                    x, y = wall.rect.x, wall.rect.y
                    # 移除钢铁墙
                    wall.kill()
                    # 创建新的砖墙
                    brick_wall = Terrain(x, y, 'brick', self.resource_manager)
                    self.terrain_group.add(brick_wall)
                    self.all_sprites.add(brick_wall)
                    # 更新墙的引用
                    self.base_walls[self.base_walls.index(wall)] = brick_wall
            # 重置结束时间
            self.base_shield_end_time = 0
            
    def create_terrain(self, density):
        """创建地形"""
        # 创建基地周围的保护墙
        base_x = (Config.GRID_WIDTH // 2) * Config.TILE_SIZE
        base_y = (Config.GRID_HEIGHT - 1) * Config.TILE_SIZE
        
        # 保护区域的网格坐标
        protected_positions = [
            (base_x // Config.TILE_SIZE - 1, base_y // Config.TILE_SIZE),     # 左
            (base_x // Config.TILE_SIZE + 1, base_y // Config.TILE_SIZE),     # 右
            (base_x // Config.TILE_SIZE, base_y // Config.TILE_SIZE - 1),     # 上
            (base_x // Config.TILE_SIZE - 1, base_y // Config.TILE_SIZE - 1), # 左上
            (base_x // Config.TILE_SIZE + 1, base_y // Config.TILE_SIZE - 1), # 右上
        ]
        
        # 创建基地
        base = Terrain(
            base_x,
            base_y,
            'base',
            self.resource_manager
        )
        self.terrain_group.add(base)
        self.all_sprites.add(base)
        
        # 创建基地保护墙
        for grid_x, grid_y in protected_positions:
            wall = Terrain(
                grid_x * Config.TILE_SIZE,
                grid_y * Config.TILE_SIZE,
                'brick',
                self.resource_manager
            )
            self.terrain_group.add(wall)
            self.all_sprites.add(wall)
        
        # 创建随机地形
        for y in range(Config.GRID_HEIGHT - 2):  # 减2是为了留出基地区域
            for x in range(Config.GRID_WIDTH):
                # 跳过玩家出生点周围
                if y < 2 and (x < 2 or x > Config.GRID_WIDTH - 3):
                    continue
                    
                # 跳过基地保护区域
                if (x, y) in protected_positions:
                    continue
                    
                # 根据密度随机生成地形
                if random.random() < density:
                    terrain_type = random.choice(['brick', 'steel', 'water', 'grass'])
                    terrain = Terrain(
                        x * Config.TILE_SIZE,
                        y * Config.TILE_SIZE,
                        terrain_type,
                        self.resource_manager
                    )
                    self.terrain_group.add(terrain)
                    self.all_sprites.add(terrain)
                    
    def update(self, current_time):
        """更新游戏状态"""
        if self.game_over:
            # 游戏结束状态下更新按钮
            self.restart_button.update()
            self.menu_button.update()
            return
            
        if self.game_state == 'MENU':
            self.start_button.update()
            self.quit_button.update()
        elif self.game_state == 'PLAYING':
            # 更新基地加固状态
            self.update_base_shield(current_time)
            
            # 更新所有精灵
            self.all_sprites.update(current_time)
            
            # 检查是否需要生成新敌人
            if (len(self.enemy_group) < Config.MAX_ENEMIES_ON_SCREEN and 
                self.enemies_remaining > 0 and 
                current_time - self.last_enemy_spawn >= Config.ENEMY_SPAWN_DELAY):
                self.spawn_enemy()
                self.last_enemy_spawn = current_time
            
            # 检查是否完成关卡
            if self.enemies_remaining <= 0 and len(self.enemy_group) == 0:
                self.level_complete()
                
            # 检查玩家是否失败
            if len(self.player_group) == 0:
                self.handle_player_death()
                
        elif self.game_state == 'GAME_OVER':
            self.restart_button.update()
            self.menu_button.update()
            
    def spawn_enemy(self):
        """生成敌人"""
        # 获取当前关卡配置
        level_config = Config.LEVEL_CONFIGS[self.current_level]
        # 根据权重选择敌人类型
        enemy_type = self.choose_enemy_type(level_config["enemy_types"])
        
        # 尝试找到合适的生成位置
        max_attempts = 10  # 最大尝试次数
        for _ in range(max_attempts):
            # 在屏幕��部随机位置生成敌人
            x = random.randint(0, Config.GRID_WIDTH - 1) * Config.TILE_SIZE
            y = 0
            
            # 创建临时矩形用于碰撞检测
            temp_rect = pygame.Rect(x, y, Config.TANK_SIZE, Config.TANK_SIZE)
            
            # 检查是否与地形碰撞（除了草地）
            collision = False
            for terrain in self.terrain_group:
                if terrain.type != 'grass' and terrain.rect.colliderect(temp_rect):
                    collision = True
                    break
                    
            # 检查是否与其他坦克碰撞
            if not collision:
                for tank in self.player_group.sprites() + self.enemy_group.sprites():
                    if tank.rect.colliderect(temp_rect):
                        collision = True
                        break
            
            # 如果没有碰撞，创建敌人
            if not collision:
                enemy = Tank(x, y, self.resource_manager, enemy_type, self)
                self.enemy_group.add(enemy)
                self.all_sprites.add(enemy)
                self.enemies_remaining -= 1
                return True
                
        # 如果所有尝试都失败，跳过这次生成
        return False
        
    def level_complete(self):
        """完成关卡"""
        self.score += Config.POINTS_FOR_LEVEL_UP
        self.current_level += 1
        if self.current_level > Config.MAX_LEVEL:
            self.game_over(victory=True)
        else:
            self.enemies_remaining = Config.ENEMIES_PER_LEVEL
            self.init_level()
            
    def draw(self):
        """绘制游戏画面"""
        self.screen.fill(Config.BLACK)
        
        if self.game_state == 'MENU':
            # 绘制菜单
            self.show_menu()
        elif self.game_state == 'PLAYING' or self.game_over:
            # 绘制游戏元素
            self.all_sprites.draw(self.screen)
            # 绘制HUD
            self.draw_hud(self.screen)
            
            # 如果游戏结束，显示结束画面
            if self.game_over:
                self.draw_game_over(self.screen)
                
        elif self.game_state == 'GAME_OVER':
            # 绘制游戏结束画面
            self.show_game_over()
            
        pygame.display.flip()
        
    def draw_game_over(self, screen):
        """绘制游戏结束画面"""
        # 创建半透明遮罩
        overlay = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        # 获取字体
        font = self.resource_manager.get_font('large')
        
        # 显示游戏结束原因
        if self.game_over_reason == 'base_destroyed':
            text = font.render('基地被摧毁，游戏结束！', True, Config.WHITE)
        elif self.game_over_reason == 'player_dead':
            text = font.render('玩家生命耗尽，游戏结束！', True, Config.WHITE)
        else:
            text = font.render('游戏结束！', True, Config.WHITE)
            
        # 显示得分
        score_text = font.render(f'最终得分：{self.score}', True, Config.WHITE)
        
        # 计算文本位置
        text_rect = text.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2 - 30))
        score_rect = score_text.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2 + 30))
        
        # 绘制文本
        screen.blit(text, text_rect)
        screen.blit(score_text, score_rect)
        
        # 绘制按钮
        self.restart_button.draw(screen)
        self.menu_button.draw(screen)
        
    def show_menu(self):
        """显示主菜单"""
        # 绘制背景
        self.screen.fill(Config.BLACK)
        
        # 绘制标题
        title_text = self.title_font.render('坦克大战', True, Config.WHITE)
        title_rect = title_text.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 4))
        self.screen.blit(title_text, title_rect)
        
        # 绘制按钮
        self.start_button.draw(self.screen)
        self.quit_button.draw(self.screen)
        
    def draw_hud(self, surface):
        """绘制HUD（生命值、分数等）"""
        # 获取字体
        font = self.resource_manager.fonts['small']
        
        # 设置文本颜色
        text_color = Config.WHITE
        
        # 绘制生命数
        lives_text = font.render(f"生命: {self.lives}", True, text_color)
        surface.blit(lives_text, (Config.SCREEN_WIDTH + 10, 10))
        
        # 绘制分数
        score_text = font.render(f"分数: {self.score}", True, text_color)
        surface.blit(score_text, (Config.SCREEN_WIDTH + 10, 40))
        
        # 绘制关卡
        level_text = font.render(f"关卡: {self.current_level}", True, text_color)
        surface.blit(level_text, (Config.SCREEN_WIDTH + 10, 70))
        
        # 绘制剩余敌人数量
        enemies_text = font.render(f"敌人: {len(self.enemy_group)}", True, text_color)
        surface.blit(enemies_text, (Config.SCREEN_WIDTH + 10, 100))
        
        # 绘制道具状态标题
        powerup_title = font.render("道具状态:", True, text_color)
        surface.blit(powerup_title, (Config.SCREEN_WIDTH + 10, 130))
        
        # 获取玩家坦克
        player = next(iter(self.player_group.sprites()), None)
        current_time = pygame.time.get_ticks()
        
        # 定义所有道具类型及其显示名称
        powerup_types = {
            'shield': '护盾',
            'speed': '加速',
            'rapid_fire': '快射',
            'base_shield': '基地加固'
        }
        
        # 显示每种道具的状态
        y_offset = 160  # 起始Y坐标
        for powerup_type, display_name in powerup_types.items():
            # 检查道具是否激活
            is_active = False
            remaining_time = 0
            
            if player:
                if powerup_type == 'shield' and current_time < player.shield_end_time:
                    is_active = True
                    remaining_time = (player.shield_end_time - current_time) // 1000
                elif powerup_type == 'speed' and current_time < player.speed_boost_end_time:
                    is_active = True
                    remaining_time = (player.speed_boost_end_time - current_time) // 1000
                elif powerup_type == 'rapid_fire' and current_time < player.rapid_fire_end_time:
                    is_active = True
                    remaining_time = (player.rapid_fire_end_time - current_time) // 1000
                elif powerup_type == 'base_shield' and current_time < self.base_shield_end_time:
                    is_active = True
                    remaining_time = (self.base_shield_end_time - current_time) // 1000
            
            # 显示道具状态
            status = f"{display_name}: {'激活 (%d秒)' % remaining_time if is_active else '未激活'}"
            status_text = font.render(status, True, Config.GREEN if is_active else Config.GRAY)
            surface.blit(status_text, (Config.SCREEN_WIDTH + 10, y_offset))
            y_offset += 25  # 每个道具状态之间的间距
        
    def show_game_over(self, victory=False):
        """显示游戏结束画面"""
        # 绘制背景
        self.screen.fill(Config.BLACK)
        
        # 绘制主要文本
        if victory:
            main_text = self.title_font.render('胜利！', True, Config.WHITE)
        else:
            main_text = self.title_font.render('游戏结束', True, Config.WHITE)
            
        main_rect = main_text.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 3))
        self.screen.blit(main_text, main_rect)
        
        # 绘制得分
        score_text = self.font.render(f'得分: {self.score}', True, Config.WHITE)
        score_rect = score_text.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)
        
        # 绘制按钮
        self.restart_button.draw(self.screen)
        self.menu_button.draw(self.screen)
        
    def quit_game(self):
        """退出游戏"""
        pygame.quit()
        
    def clear_all_sprites(self):
        """清空所有精灵组"""
        self.all_sprites.empty()
        self.player_group.empty()
        self.enemy_group.empty()
        self.bullet_group.empty()
        self.terrain_group.empty()
        self.powerup_group.empty()
        
    def show_victory_screen(self):
        """显示胜利画面"""
        self.show_game_over(victory=True)
        
    def show_defeat_screen(self):
        """显示失败画面"""
        self.show_game_over(victory=False)
        
    def handle_player_death(self):
        """处理玩家死亡"""
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True
            self.game_over_reason = 'player_dead'
        
    def handle_enemy_death(self, enemy):
        """处理敌人死亡"""
        # 增加分数
        self.score += Config.POINTS_PER_ENEMY
        
        # 移除敌人
        enemy.kill()
        
        # 随机掉落道具
        if random.random() < Config.POWERUP_DROP_CHANCE:
            powerup_type = random.choice(['shield', 'speed', 'rapid_fire', 'base_shield'])
            powerup = PowerUp(enemy.rect.centerx, enemy.rect.centery,
                            powerup_type, self.resource_manager)
            self.powerup_group.add(powerup)
            self.all_sprites.add(powerup)
            
    def run(self):
        """运行游戏主循环"""
        self.running = True
        while self.running:
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.game_state == 'PLAYING':
                            self.game_state = 'MENU'
                        elif self.game_state == 'MENU':
                            self.running = False
                            
                # 处理按钮事件
                if self.game_state == 'MENU':
                    self.start_button.handle_event(event)
                    self.quit_button.handle_event(event)
                elif self.game_state == 'GAME_OVER' or self.game_over:
                    self.restart_button.handle_event(event)
                    self.menu_button.handle_event(event)
            
            # 更新游戏状态
            current_time = pygame.time.get_ticks()
            self.update(current_time)
            
            # 绘制游戏画面
            self.draw()
            
            # 控制帧率
            self.clock.tick(Config.FPS)
            
        pygame.quit()
