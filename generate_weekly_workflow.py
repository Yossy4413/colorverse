import os
import shutil
import json
import datetime
from PIL import Image

# Directories
TWITTER_DIR = "publish/twitter"
INSTA_DIR = "publish/instagram"
PIXIV_DIR = "publish/pixiv"

def get_next_weekday(start_date, target_weekday):
    """0 = Monday, 1 = Tuesday, ..., 6 = Sunday"""
    days_ahead = target_weekday - start_date.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return start_date + datetime.timedelta(days_ahead)

now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))

tuesday = get_next_weekday(now, 1).replace(hour=21, minute=0, second=0, microsecond=0)
thursday = get_next_weekday(now, 3).replace(hour=21, minute=0, second=0, microsecond=0)
sunday = get_next_weekday(now, 6).replace(hour=21, minute=0, second=0, microsecond=0)

# Weekly Campaign Details
POSTS = [
    {
        "type": "artwork",
        "source": "assets/kuro/night_collection/night_street.png",
        "name": "post1_artwork",
        "caption": "A silent observer in the neon rain.\nネオンの雨の中、静かな観察者。\n\n#COLORVERSE #AIart #cyberpunk",
        "time": tuesday.isoformat()
    },
    {
        "type": "character",
        "source": "assets/kuro/profile/kuro_profile_card.png",
        "name": "post2_character",
        "caption": "KURO\nThe girl who watches the city.\n街を見つめる少女。\n\n#COLORVERSE #AIart #cyberpunk",
        "time": thursday.isoformat()
    },
    {
        "type": "world",
        "source": "assets/environment/colorverse_city_kv.png",
        "name": "post3_world",
        "caption": "COLORVERSE CITY\nNeon lights and digital dreams.\nネオンの光とデジタルの夢。\n\n#COLORVERSE #AIart #cyberpunk",
        "time": sunday.isoformat()
    }
]

def generate_weekly_workflow():
    for d in [TWITTER_DIR, INSTA_DIR, PIXIV_DIR]:
        os.makedirs(d, exist_ok=True)

    queue = []
    print("Generating weekly social media workflow...")
    for post in POSTS:
        source = post["source"]
        name = post["name"]
        caption = post["caption"]
        post_time = post["time"]
        
        if not os.path.exists(source):
            print(f"File not found: {source}")
            continue
            
        print(f"Processing {name} ({post['type']})...")
        
        # Write specific captions for this post
        for d in [TWITTER_DIR, INSTA_DIR, PIXIV_DIR]:
            with open(os.path.join(d, f"{name}_caption.txt"), "w", encoding="utf-8") as f:
                f.write(caption)
                
            queue.append({
                "platform": d.split("/")[-1],
                "image_path": f"{d}/{name}.png",
                "caption": caption,
                "post_time": post_time,
                "status": "pending",
                "retry_count": 0
            })
                
        with Image.open(source) as img:
            # 1. PIXIV: Original
            img.save(os.path.join(PIXIV_DIR, f"{name}.png"))
            
            # 2. TWITTER: 1920x1080 crop
            tw_img = img.copy()
            w, h = tw_img.size
            target_w, target_h = 1920, 1080
            img_ratio = w / h
            target_ratio = target_w / target_h
            if img_ratio > target_ratio:
                tw_img.thumbnail((int(h * target_ratio), h), Image.Resampling.LANCZOS)
                nw, nh = tw_img.size
                left = (nw - target_w) / 2
                tw_img = tw_img.crop((left, 0, left + target_w, target_h))
            else:
                tw_img.thumbnail((w, w / target_ratio), Image.Resampling.LANCZOS)
                nw, nh = tw_img.size
                top = (nh - target_h) / 2
                tw_img = tw_img.crop((0, top, target_w, top + target_h))
                
            tw_final = tw_img.resize((1920, 1080), Image.Resampling.LANCZOS)
            tw_final.save(os.path.join(TWITTER_DIR, f"{name}.png"))
            
            # 3. INSTA: 1080x1080 crop
            in_img = img.copy()
            w, h = in_img.size
            new_size = min(w, h)
            left = (w - new_size) / 2
            top = (h - new_size) / 2
            right = (w + new_size) / 2
            bottom = (h + new_size) / 2
            
            insta_crop = in_img.crop((left, top, right, bottom))
            insta_crop.thumbnail((1080, 1080), Image.Resampling.LANCZOS)
            insta_crop.save(os.path.join(INSTA_DIR, f"{name}.png"))
            
    # Write the schedule JSON queue
    schedule_path = "publish/post_queue.json"
    with open(schedule_path, "w", encoding="utf-8") as json_file:
        json.dump(queue, json_file, indent=4, ensure_ascii=False)
    print(f"Schedule queue written to {schedule_path}")

if __name__ == "__main__":
    generate_weekly_workflow()
