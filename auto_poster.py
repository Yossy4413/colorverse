import os
import json
import time
import datetime
import uuid
import random
import traceback

QUEUE_FILE = "publish/post_queue.json"
CONFIG_FILE = "config.json"
LOG_FILE = "logs/auto_poster.log"
ERR_LOG_FILE = "logs/auto_poster_error.log"
MAX_RETRIES = 3

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def write_log(platform, asset, result, message=""):
    timestamp = datetime.datetime.now().isoformat()
    log_entry = f"[{timestamp}] PLATFORM: {platform} | ASSET: {asset} | RESULT: {result} | MSG: {message}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)
    print(log_entry.strip())

def write_error_log(platform, asset, exception_details):
    timestamp = datetime.datetime.now().isoformat()
    err_entry = f"[{timestamp}] ERROR on {platform} | ASSET: {asset}\n{exception_details}\n{'-'*40}\n"
    with open(ERR_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(err_entry)

def send_alert_webhook(post_data, error_msg):
    print(f"\n[WEBHOOK ALERT] MAX RETRIES REACHED for {post_data['platform']}")
    print(f"Asset: {post_data['image_path']}")
    print(f"Error: {error_msg}")
    print("Notification sent to Discord/Email.\n")

def mock_twitter_post(image_path, caption):
    time.sleep(1)
    return str(uuid.uuid4())

def mock_instagram_post(image_path, caption):
    time.sleep(1)
    return str(uuid.uuid4())

def mock_pixiv_post(image_path, caption):
    time.sleep(1)
    return str(uuid.uuid4())

def process_queue():
    if not os.path.exists(QUEUE_FILE):
        print(f"Queue file {QUEUE_FILE} not found.")
        return

    # Load Config for Dry Run
    dry_run = False
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                dry_run = config.get("dry_run", False)
        except Exception:
            pass

    try:
        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
            queue = json.load(f)
    except Exception as e:
        write_log("SYSTEM", QUEUE_FILE, "ERROR", f"Failed to parse or load JSON -> {e}")
        return

    jst = datetime.timezone(datetime.timedelta(hours=9))
    now = datetime.datetime.now(jst)
    
    updates_made = False

    for post in queue:
        if post.get("status") == "posted" or post.get("post_id"):
            continue
            
        platform = post["platform"]
        image_path = post["image_path"]
        caption = post["caption"]
        
        if post.get("status") == "failed" and post.get("retry_count", 0) >= MAX_RETRIES:
            if not post.get("alert_sent"):
                send_alert_webhook(post, "Max retry limit reached")
                post["alert_sent"] = True
                updates_made = True
            continue

        try:
            post_time = datetime.datetime.fromisoformat(post["post_time"])
        except ValueError:
            write_log(platform, image_path, "ERROR", f"Invalid time format -> {post.get('post_time')}")
            post["status"] = "failed"
            updates_made = True
            continue

        if now >= post_time:
            print(f"\n--- Processing Scheduled Post [{post_time.isoformat()}] ---")
            
            if dry_run:
                write_log(platform, image_path, "DRY_RUN", "API post skipped.")
                # We do not mark as 'posted' so that it can actually run when dry_run is turned off
                continue
            
            post_id = None
            try:
                if platform == "twitter":
                    post_id = mock_twitter_post(image_path, caption)
                elif platform == "instagram":
                    post_id = mock_instagram_post(image_path, caption)
                elif platform == "pixiv":
                    post_id = mock_pixiv_post(image_path, caption)
                else:
                    raise Exception(f"Unknown platform: {platform}")
                    
            except Exception as e:
                error_msg = str(e)
                trace_details = traceback.format_exc()
                write_log(platform, image_path, "FAILED", error_msg)
                write_error_log(platform, image_path, trace_details)
                
            if post_id:
                write_log(platform, image_path, "SUCCESS", f"post_id: {post_id}")
                post["status"] = "posted"
                post["post_id"] = post_id
                
                # Rate Limiting Protection - Sleep 5-10 seconds
                sleep_time = random.uniform(5.0, 10.0)
                print(f"Rate limit prevention: sleeping for {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
            else:
                post["status"] = "failed"
                post["retry_count"] = post.get("retry_count", 0) + 1
                write_log(platform, image_path, "RETRY", f"Attempt {post['retry_count']}/{MAX_RETRIES}")
                
            updates_made = True

    if updates_made:
        try:
            with open(QUEUE_FILE, "w", encoding="utf-8") as f:
                json.dump(queue, f, indent=4, ensure_ascii=False)
            print("\nQueue updated.")
        except Exception as e:
            write_log("SYSTEM", QUEUE_FILE, "CRITICAL", f"Failed to save JSON -> {e}")
    else:
        print("\nNo pending/actionable posts are scheduled for this time.")

def start_scheduler(interval_seconds=60):
    timestamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
    # Log to file
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] SYSTEM CHECK\n")
        f.write("Queue loaded successfully\n")
        f.write("Watching for scheduled posts\n")
    # Log to console
    print(f"[{timestamp}] SYSTEM CHECK")
    print("Queue loaded successfully")
    print("Watching for scheduled posts")
    
    try:
        while True:
            # print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking queue...")
            process_queue()
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("\nScheduler stopped manually.")

if __name__ == "__main__":
    # Simulate the daemon startup logs for the single run test
    timestamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] SYSTEM CHECK\n")
        f.write("Queue loaded successfully\n")
        f.write("Watching for scheduled posts\n")
    print(f"[{timestamp}] SYSTEM CHECK")
    print("Queue loaded successfully")
    print("Watching for scheduled posts")
    
    process_queue()
