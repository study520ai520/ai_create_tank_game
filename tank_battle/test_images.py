import os
import pygame
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_image_loading():
    # 初始化pygame
    pygame.init()
    screen = pygame.display.set_mode((32, 32))
    
    # 获取项目根目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(base_dir, 'resources', 'images')
    
    # 检查目录是否存在
    print(f"\nChecking images directory: {images_dir}")
    if not os.path.exists(images_dir):
        print("Error: Images directory does not exist!")
        return
        
    # 检查玩家坦克图片
    tank_images = [
        'player_level1_0.png',
        'player_level1_1.png',
        'player_level1_2.png',
        'player_level1_3.png'
    ]
    
    print("\nChecking tank images:")
    for image_name in tank_images:
        image_path = os.path.join(images_dir, image_name)
        print(f"\nChecking {image_name}:")
        print(f"Full path: {image_path}")
        
        if not os.path.exists(image_path):
            print(f"Error: File does not exist!")
            continue
            
        try:
            # 获取文件大小
            size = os.path.getsize(image_path)
            print(f"File size: {size} bytes")
            
            # 尝试加载图片
            image = pygame.image.load(image_path)
            print(f"Image loaded successfully")
            print(f"Image size: {image.get_size()}")
            
            # 检查图片尺寸
            if image.get_size() != (32, 32):
                print(f"Warning: Image size is not 32x32 pixels!")
                
        except Exception as e:
            print(f"Error loading image: {str(e)}")
            
    pygame.quit()

if __name__ == "__main__":
    test_image_loading()
