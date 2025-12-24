from datetime import datetime
from src.monitor import load_processed_ids, save_processed_ids
from src.youtube import get_new_videos
from src.telegram_sender import send_analysis

def run_check():
    now = datetime.now()
    print(f"🔍 [{now.strftime('%Y-%m-%d %H:%M:%S')}] Starting local check...")
    
    try:
        # Load processed IDs (memory of what we've already seen)
        processed_ids = load_processed_ids()
        
        # Check for new videos
        new_videos = get_new_videos(processed_ids)
        
        if not new_videos:
            print("✅ No new videos found.")
            return

        print(f"🎥 Found {len(new_videos)} new videos.")
        
        # Process each new video
        for video in new_videos:
            try:
                print(f"📹 Processing: {video['title']}")
                success = send_analysis(video)
                if success:
                    processed_ids.add(video['id'])
                    print(f"✅ Sent successfully")
            except Exception as e:
                print(f"❌ Error processing video: {e}")
                continue
        
        # Save the updated list of seen videos
        save_processed_ids(processed_ids)
        print("💾 Progress saved.")

    except Exception as e:
        print(f"❌ Critical Error: {e}")

if __name__ == "__main__":
    run_check()