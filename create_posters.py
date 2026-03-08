import os
from PIL import Image, ImageDraw, ImageFont

BASE_IMAGE = r"C:\Users\USER\.gemini\antigravity\brain\b309efcd-a3f0-4804-87ea-8abb01ef3506\kuro_launch_poster_rooftop_base_1772968302018.png"

OUTPUTS = [
    ("assets/poster/colorverse_launch_poster_master.png", 2480, 3508),
    ("publish/poster/poster_twitter.png", 1920, 1080),
    ("publish/poster/poster_instagram.png", 1080, 1080),
    ("publish/poster/poster_og.png", 1200, 630)
]

def get_font(size):
    try:
        return ImageFont.truetype("arialbd.ttf", size)
    except:
        try:
            return ImageFont.truetype("segoeuib.ttf", size)
        except:
            return ImageFont.load_default()

def apply_typography(img, width, height):
    draw = ImageDraw.Draw(img)
    
    # Scale fonts based on height
    base_size = min(width, height)
    
    try:
        title_font = ImageFont.truetype("impact.ttf", int(base_size * 0.15))
    except:
        title_font = get_font(int(base_size * 0.15))
        
    subtitle_font = get_font(int(base_size * 0.04))
    series_font = get_font(int(base_size * 0.05))
    url_font = get_font(int(base_size * 0.03))
    
    def draw_neon_text(xy, text, font, fill="white", glow_color="#00ffff", glow_radius=4):
        x, y = xy
        for offset_x in range(-glow_radius, glow_radius+1):
            for offset_y in range(-glow_radius, glow_radius+1):
                if offset_x**2 + offset_y**2 <= glow_radius**2:
                    draw.text((x + offset_x, y + offset_y), text, font=font, fill=glow_color)
        draw.text((x, y), text, font=font, fill=fill)
        
    def draw_glitch_text(xy, text, font, fill="white", cyan_offset=(-3, 0), magenta_offset=(3, 0)):
        x, y = xy
        draw.text((x + cyan_offset[0], y + cyan_offset[1]), text, font=font, fill="#00ffff")
        draw.text((x + magenta_offset[0], y + magenta_offset[1]), text, font=font, fill="#ff00ff")
        draw.text((x, y), text, font=font, fill=fill)

    def get_text_size(text, font):
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            return bbox[2] - bbox[0], bbox[3] - bbox[1]
        except AttributeError:
            return draw.textsize(text, font=font)

    # Layout dimensions
    margin_y = height * 0.05
    
    # Title - Top
    title = "COLORVERSE"
    tw, th = get_text_size(title, title_font)
    glitch_offset = max(2, int(base_size * 0.005))
    draw_glitch_text(( (width - tw) // 2, margin_y), title, title_font, cyan_offset=(-glitch_offset, 0), magenta_offset=(glitch_offset, 0))
    
    # Subtitle - Below Title
    subtitle = "Where every color becomes a girl"
    sw, sh = get_text_size(subtitle, subtitle_font)
    draw_neon_text(( (width - sw) // 2, margin_y + th + base_size*0.02), subtitle, subtitle_font, fill="white", glow_color="#ff00aa", glow_radius=max(1, int(base_size*0.002)))
    
    # URL - Bottom
    url = "colorverse.art"
    uw, uh = get_text_size(url, url_font)
    draw_neon_text(( (width - uw) // 2, height - margin_y - uh), url, url_font, fill="white", glow_color="#00aaaa", glow_radius=max(1, int(base_size*0.002)))
    
    # Series - Above URL
    series = "Series 01 : KURO"
    sew, seh = get_text_size(series, series_font)
    draw_neon_text(( (width - sew) // 2, height - margin_y - uh - seh - base_size*0.04), series, series_font, fill="white", glow_color="#0055ff", glow_radius=max(2, int(base_size*0.003)))


def main():
    if not os.path.exists(BASE_IMAGE):
        print("Base image not found.")
        return
        
    os.makedirs("assets/poster", exist_ok=True)
    os.makedirs("publish/poster", exist_ok=True)
    
    with Image.open(BASE_IMAGE) as img:
        for out_path, target_w, target_h in OUTPUTS:
            # Crop to aspect ratio
            width, height = img.size
            img_ratio = width / height
            target_ratio = target_w / target_h
            
            cropped = img.copy()
            if img_ratio > target_ratio:
                # Image wider than target, crop sides
                new_w = int(height * target_ratio)
                left = (width - new_w) // 2
                cropped = cropped.crop((left, 0, left + new_w, height))
            else:
                # Image taller than target, crop top/bottom
                # Center crop slightly higher for portraits using 0.3 factor
                new_h = int(width / target_ratio)
                top = int((height - new_h) * 0.2)
                cropped = cropped.crop((0, top, width, top + new_h))
                
            resized = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
            
            apply_typography(resized, target_w, target_h)
            
            resized.save(out_path)
            print(f"Generated {out_path}")

if __name__ == '__main__':
    main()
