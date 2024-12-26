import pygame
from .config import Config

class Button:
    def __init__(self, x, y, width, height, text, action, font=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.is_hovered = False
        self.font = font if font else pygame.font.Font(None, 36)
        
        # 按钮颜色
        self.normal_color = Config.GRAY
        self.hover_color = Config.LIGHT_GRAY
        self.text_color = Config.WHITE
        
    def update(self):
        """更新按钮状态"""
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)
                
    def draw(self, surface):
        """绘制按钮"""
        # 绘制按钮背景
        color = self.hover_color if self.is_hovered else self.normal_color
        pygame.draw.rect(surface, color, self.rect)
        
        # 绘制按钮边框
        pygame.draw.rect(surface, Config.WHITE, self.rect, 2)
        
        # 绘制文本
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
