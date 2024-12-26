"""这个文件已经不再需要，可以删除"""

import pygame
import logging

logger = logging.getLogger(__name__)

class InputHandler:
    # 按键映射
    MOVE_UP = [pygame.K_w, pygame.K_UP]
    MOVE_DOWN = [pygame.K_s, pygame.K_DOWN]
    MOVE_LEFT = [pygame.K_a, pygame.K_LEFT]
    MOVE_RIGHT = [pygame.K_d, pygame.K_RIGHT]
    SHOOT = [pygame.K_SPACE]
    
    @staticmethod
    def is_pressed(keys, action_keys):
        """检查某个动作的按键是否被按下"""
        # 调试信息：记录按键状态
        pressed_keys = []
        for key in action_keys:
            if keys.get(key, False):
                pressed_keys.append(pygame.key.name(key))
        
        if pressed_keys:
            logger.debug(f"按键检测 - 动作键: {[pygame.key.name(k) for k in action_keys]}, "
                        f"按下的键: {pressed_keys}")
            
        return bool(pressed_keys)
        
    @staticmethod
    def create_key_state(up=False, down=False, left=False, right=False, shoot=False):
        """创建一个按键状态字典，用于测试"""
        keys = {}
        
        # 初始化所有可能的按键为False
        for key in (InputHandler.MOVE_UP + InputHandler.MOVE_DOWN +
                   InputHandler.MOVE_LEFT + InputHandler.MOVE_RIGHT +
                   InputHandler.SHOOT):
            keys[key] = False
            
        # 设置按下的键
        if up:
            for key in InputHandler.MOVE_UP:
                keys[key] = True
        if down:
            for key in InputHandler.MOVE_DOWN:
                keys[key] = True
        if left:
            for key in InputHandler.MOVE_LEFT:
                keys[key] = True
        if right:
            for key in InputHandler.MOVE_RIGHT:
                keys[key] = True
        if shoot:
            for key in InputHandler.SHOOT:
                keys[key] = True
                
        return keys
