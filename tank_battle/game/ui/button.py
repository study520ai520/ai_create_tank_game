import pygame

class Button:
    def __init__(self, x, y, width, height, text, action, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.font = font
        self.color = (128, 128, 128)  # 默认颜色
        self.hover_color = (200, 200, 200)  # 鼠标悬停时的颜色
        self.text_color = (255, 255, 255)  # 文字颜色
        self.is_hovered = False
        
    def update(self):
        # 更新按钮状态
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:  # 左键点击
                self.action()
                
    def draw(self, surface):
        """绘制按钮"""
        # 根据悬停状态选择颜色
        color = self.hover_color if self.is_hovered else self.color
        
        # 绘制按钮背景
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)  # 白色边框
        
        # 绘制文本
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
