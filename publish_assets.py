import os
from PIL import Image

# Directories
SOURCE_DIR = "assets/kuroh/night_collection"
TWITTER_DIR = "publish/twitter"
INSTA_DIR = "publish/instagram"
PIXIV_DIR = "publish/pixiv"

# Ensure directories exist
for d in [TWITTER_DIR, INSTA_DIR, PIXIV_DIR]:
    os.makedirs(d, exist_ok=True)

# Templates
UNIFIED_CAPTION = """COLORVERSE

Where every color becomes a girl.

Series 01 : KURO

colorverse.art

#COLORVERSE
#AIart
#animeart
#cyberpunk
#illustration
"""

POSTER_EN_TEMPLATE = """COLORVERSE
Where every color becomes a girl.

Series 01
KURO

Launch
March 22

#COLORVERSE #AIart #animeart #cyberpunk #illustration
"""

POSTER_JP_TEMPLATE = """COLORVERSE
すべての色が少女になる

Series 01
KURO

2026.03.22

#COLORVERSE #AIart #animeart #cyberpunk #illustration
"""

def generate_social_assets():
    if not os.path.exists(SOURCE_DIR):
        print(f"Source directory {SOURCE_DIR} not found.")
        return

    images = [f for f in os.listdir(SOURCE_DIR) if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    if not images:
        print("No images found in source.")
        return

    for img_name in images:
        source_path = os.path.join(SOURCE_DIR, img_name)
        base_name = os.path.splitext(img_name)[0]
        
        print(f"Processing {img_name}...")
        try:
            with Image.open(source_path) as img:
                # 1. PIXIV: Original resolution
                pixiv_img_path = os.path.join(PIXIV_DIR, img_name)
                img.save(pixiv_img_path)
                
                # 2. TWITTER: 1920x1080 crop
                with Image.open(source_path) as orig_img:
                    width, height = orig_img.size
                    target_w, target_h = 1920, 1080
                    img_ratio = width / height
                    target_ratio = target_w / target_h
                    
                    tw_img = orig_img.copy()
                    if img_ratio > target_ratio:
                        # Image is wider than target, resize to match height
                        tw_img.thumbnail((int(height * target_ratio), height), Image.Resampling.LANCZOS)
                        w, h = tw_img.size
                        left = (w - target_w) / 2
                        tw_img = tw_img.crop((left, 0, left + target_w, target_h))
                    else:
                        # Image is taller than target, resize to match width
                        tw_img.thumbnail((width, width / target_ratio), Image.Resampling.LANCZOS)
                        w, h = tw_img.size
                        top = (h - target_h) / 2
                        tw_img = tw_img.crop((0, top, target_w, top + target_h))
                    
                    # Safe resize in case image was smaller than 1920x1080 initially
                    tw_final = tw_img.resize((1920, 1080), Image.Resampling.LANCZOS)
                    twitter_img_path = os.path.join(TWITTER_DIR, img_name)
                    tw_final.save(twitter_img_path)
                
                # 3. INSTA: Square Crop (Center) 1080x1080
                with Image.open(source_path) as orig_img:
                    width, height = orig_img.size
                    new_size = min(width, height)
                    left = (width - new_size) / 2
                    top = (height - new_size) / 2
                    right = (width + new_size) / 2
                    bottom = (height + new_size) / 2
                    
                    insta_img = orig_img.crop((left, top, right, bottom))
                    insta_img.thumbnail((1080, 1080), Image.Resampling.LANCZOS)
                    insta_img_path = os.path.join(INSTA_DIR, img_name)
                    insta_img.save(insta_img_path)
                
        except Exception as e:
            print(f"Failed to process image {img_name}: {e}")

    # Write text templates
    with open(os.path.join(TWITTER_DIR, "caption_x.txt"), "w", encoding="utf-8") as f:
        f.write(UNIFIED_CAPTION)
    
    with open(os.path.join(INSTA_DIR, "caption.txt"), "w", encoding="utf-8") as f:
        f.write(UNIFIED_CAPTION)
        
    with open(os.path.join(PIXIV_DIR, "caption.txt"), "w", encoding="utf-8") as f:
        f.write(UNIFIED_CAPTION)

    print("Social media assets generated successfully.")

def generate_launch_poster_assets():
    POSTER_SOURCE = "assets/poster/colorverse_launch_poster_master.png"
    POSTER_OUTPUT = "publish/poster"
    
    if not os.path.exists(POSTER_SOURCE):
        print("Launch poster not found.")
        return

    os.makedirs(POSTER_OUTPUT, exist_ok=True)
    
    print("Generating launch poster variations...")
    try:
        with Image.open(POSTER_SOURCE) as img:
            # 1. Twitter / X (1920x1080)
            tw_img = img.copy()
            tw_img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
            tw_img.save(os.path.join(POSTER_OUTPUT, "poster_twitter.png"))
            
            # 2. Instagram (1080x1080) - crop center
            in_img = img.copy()
            width, height = in_img.size
            new_size = min(width, height)
            left = (width - new_size) / 2
            top = (height - new_size) / 2
            right = (width + new_size) / 2
            bottom = (height + new_size) / 2
            in_img = in_img.crop((left, top, right, bottom))
            in_img.thumbnail((1080, 1080), Image.Resampling.LANCZOS)
            in_img.save(os.path.join(POSTER_OUTPUT, "poster_instagram.png"))
            
            # 3. OpenGraph (1200x630)
            # Typically needs center crop preserving the wide aspect ratio
            og_img = img.copy()
            target_w, target_h = 1200, 630
            # Resize image to match width, then crop height, or vice versa
            img_ratio = width / height
            target_ratio = target_w / target_h
            if img_ratio > target_ratio:
                # Image is wider than target, resize to match height
                og_img.thumbnail((int(height * target_ratio), height), Image.Resampling.LANCZOS)
                w, h = og_img.size
                left = (w - target_w) / 2
                og_img = og_img.crop((left, 0, left + target_w, target_h))
            else:
                # Image is taller than target, resize to match width
                og_img.thumbnail((width, width / target_ratio), Image.Resampling.LANCZOS)
                w, h = og_img.size
                top = (h - target_h) / 2
                og_img = og_img.crop((0, top, target_w, top + target_h))
            # Just force resize if crop logic is complex, but thumbnail crop is safe
            og_img = img.copy()
            og_img.thumbnail((1200, 1200), Image.Resampling.LANCZOS) # Ensure it's downsized first
            w, h = og_img.size
            top = (h - 630) / 2
            bottom = (h + 630) / 2
            left = (w - 1200) / 2
            right = (w + 1200) / 2
            
            # Simplified safe crop/resize for OG
            og_final = img.resize((1200, 630), Image.Resampling.LANCZOS)
            og_final.save(os.path.join(POSTER_OUTPUT, "poster_og.png"))

            # 4. Print Poster (2480x3508)
            print_img = img.resize((2480, 3508), Image.Resampling.LANCZOS)
            print_img.save(os.path.join(POSTER_OUTPUT, "poster_print.png"))

            print("Poster variations generated successfully.")
            
        # Write text templates
        with open(os.path.join(POSTER_OUTPUT, "template_en.txt"), "w", encoding="utf-8") as f:
            f.write(POSTER_EN_TEMPLATE)
        with open(os.path.join(POSTER_OUTPUT, "template_jp.txt"), "w", encoding="utf-8") as f:
            f.write(POSTER_JP_TEMPLATE)
        print("Poster templates generated successfully.")
            
    except Exception as e:
        print(f"Failed to generate poster assets: {e}")

if __name__ == "__main__":
    generate_social_assets()
    generate_launch_poster_assets()
