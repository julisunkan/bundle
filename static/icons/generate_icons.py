from PIL import Image, ImageDraw, ImageFont
import os

sizes = [72, 96, 128, 144, 152, 192, 384, 512]

def create_icon(size, maskable=False):
    img = Image.new('RGBA', (size, size), (99, 102, 241, 255))
    draw = ImageDraw.Draw(img)
    
    if maskable:
        padding = size // 5
        draw.rectangle([padding, padding, size-padding, size-padding], fill=(99, 102, 241, 255))
    
    center = size // 2
    card_w = int(size * 0.5)
    card_h = int(size * 0.35)
    card_x = center - card_w // 2
    card_y = center - card_h // 2
    draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=size//20, fill=(255, 255, 255, 255))
    
    line_y = card_y + card_h // 3
    line_margin = card_w // 6
    draw.line([(card_x + line_margin, line_y), (card_x + card_w - line_margin, line_y)], fill=(99, 102, 241, 255), width=max(2, size//50))
    draw.line([(card_x + line_margin, line_y + card_h//4), (card_x + card_w//2, line_y + card_h//4)], fill=(200, 200, 200, 255), width=max(2, size//50))
    
    return img

for size in sizes:
    icon = create_icon(size)
    icon.save(f'icon-{size}x{size}.png')
    print(f'Created icon-{size}x{size}.png')

for size in [192, 512]:
    icon = create_icon(size, maskable=True)
    icon.save(f'icon-{size}x{size}-maskable.png')
    print(f'Created icon-{size}x{size}-maskable.png')

print('All icons generated!')
