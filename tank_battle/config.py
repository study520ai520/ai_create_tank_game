class Config:
    # 游戏窗口设置
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    TILE_SIZE = 32
    FPS = 60
    
    # 游戏设置
    PLAYER_SPEED = 4
    ENEMY_SPEED = 2
    BULLET_SPEED = 8
    MAX_ENEMIES = 4
    ENEMY_SPAWN_DELAY = 3000  # 毫秒
    ENEMY_SHOOT_CHANCE = 0.02  # 每帧2%的概率射击
    
    # 得分设置
    SCORE_ENEMY_DESTROY = 100
    SCORE_POWERUP_COLLECT = 50
    
    # 道具设置
    POWERUP_SPAWN_DELAY = 10000  # 毫秒
    POWERUP_DURATION = 10000  # 毫秒
    SHIELD_DURATION = 10000    # 毫秒
