import sys
import os
import unittest
import pygame

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.game_manager import GameManager
from game.sprites.tank import PlayerTank, EnemyTank, Bullet
from game.sprites.terrain import BrickWall, SteelWall, Water, Bush, Base
from game.sprites.powerup import PowerUp, PowerUpManager
from config import Config

class TestGameFunctionality(unittest.TestCase):
    def setUp(self):
        """每个测试用例前的设置"""
        pygame.init()
        pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        self.game = GameManager()

    def tearDown(self):
        """每个测试用例后的清理"""
        pygame.quit()

    def test_player_movement(self):
        """测试玩家坦克移动"""
        initial_x = self.game.player.rect.x
        initial_y = self.game.player.rect.y

        # 创建一个模拟的按键字典
        keys = {}
        for key in [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d,
                   pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
            keys[key] = False
        
        # 测试向上移动
        keys[pygame.K_w] = True
        self.game.player.handle_input(keys, self.game.walls)
        self.assertEqual(self.game.player.direction, 0)
        self.assertTrue(self.game.player.rect.y < initial_y)

        # 重置位置
        self.game.player.rect.y = initial_y
        keys[pygame.K_w] = False

        # 测试向下移动
        keys[pygame.K_s] = True
        self.game.player.handle_input(keys, self.game.walls)
        self.assertEqual(self.game.player.direction, 2)
        self.assertTrue(self.game.player.rect.y > initial_y)

    def test_bullet_collision(self):
        """测试子弹碰撞"""
        # 创建一个砖墙
        wall = BrickWall(100, 100, self.game.resource_manager)
        self.game.walls.add(wall)

        # 创建一个子弹
        bullet = Bullet(100, 90, 2, self.game.resource_manager)  # 向下射击
        self.game.bullets.add(bullet)

        # 更新游戏状态
        bullet.update()
        self.game.handle_collisions()

        # 验证子弹和墙都被摧毁
        self.assertFalse(bullet.alive())
        self.assertFalse(wall.alive())

    def test_enemy_behavior(self):
        """测试敌人行为"""
        # 清除现有敌人
        self.game.enemies.empty()

        # 创建一个敌人
        enemy = EnemyTank(100, 100, self.game.resource_manager)
        self.game.enemies.add(enemy)

        # 记录初始位置
        initial_x = enemy.rect.x
        initial_y = enemy.rect.y

        # 强制改变方向并更新
        enemy.direction_change_time = 0  # 确保会改变方向
        current_time = pygame.time.get_ticks()
        enemy.update(current_time, self.game.walls, self.game.player)

        # 验证敌人有移动
        self.assertTrue(
            enemy.rect.x != initial_x or enemy.rect.y != initial_y,
            "Enemy tank should move from its initial position"
        )

    def test_powerup_effects(self):
        """测试道具效果"""
        # 测试护盾道具
        powerup = PowerUp(
            self.game.player.rect.x,
            self.game.player.rect.y,
            'shield',
            self.game.resource_manager
        )
        
        # 确保玩家初始状态没有护盾
        self.assertFalse(self.game.player.is_shielded)
        
        # 应用道具效果
        powerup.apply_effect(self.game.player, pygame.time.get_ticks())
        
        # 验证玩家获得护盾
        self.assertTrue(self.game.player.is_shielded)

    def test_game_over_conditions(self):
        """测试游戏结束条件"""
        # 测试基地被摧毁
        self.game.base.health = 1  # 确保基地有生命值
        self.game.base.destroy()
        self.game.handle_collisions()  # 更新游戏状态
        self.assertTrue(self.game.game_over, "Game should be over when base is destroyed")

        # 重置游戏
        self.game.reset_game()
        self.assertFalse(self.game.game_over, "Game should not be over after reset")

        # 测试玩家生命耗尽
        self.game.player.lives = 1
        self.game.player.take_damage()
        self.game.handle_collisions()  # 更新游戏状态
        self.assertTrue(self.game.game_over, "Game should be over when player has no lives")

    def test_wall_properties(self):
        """测试墙体属性"""
        # 测试砖墙可摧毁
        brick = BrickWall(0, 0, self.game.resource_manager)
        self.assertTrue(brick.destructible)

        # 测试钢墙不可摧毁
        steel = SteelWall(0, 0, self.game.resource_manager)
        self.assertFalse(steel.destructible)

        # 测试水域不可摧毁
        water = Water(0, 0, self.game.resource_manager)
        self.assertFalse(water.destructible)

        # 测试草丛不可摧毁但可穿过
        bush = Bush(0, 0, self.game.resource_manager)
        self.assertFalse(bush.destructible)
        self.assertTrue(bush.passable)

if __name__ == '__main__':
    unittest.main()
