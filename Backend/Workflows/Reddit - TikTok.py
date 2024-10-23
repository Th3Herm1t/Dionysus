import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sys
import os
import json
import time
from datetime import datetime
import logging
from data_ingestion.reddit import RedditClient
from LLM.gemini import GeminiClient
from TTS.edge_tts import EdgeTTSClient  # Import Edge TTS
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
import asyncio  # Required for handling asynchronous TTS synthesis

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

def fetch_reddit_posts(subreddit_name, limit=100):
    reddit_client = RedditClient()
    posts = reddit_client.fetch_top_posts(subreddit_name, limit=limit, time_filter='day', include_comments=True)
    return posts

def filter_posts_via_llm(posts, prompt_path=r'Backend\LLM\prompts\reddit_post_selection_for_tiktok.txt', limit=24):
    gemini_client = GeminiClient()

    with open(prompt_path, 'r') as file:
        prompt_template = file.read().strip()

    reddit_posts_info = "\n\n".join(
        f"Post id: {post['id']}\n"
        f"Title: {post['title']}\n"
        f"Body: {post['body']}\n"
        f"Score: {post['score']}\n"
        f"Number of Comments: {post['num_comments']}\n"
        f"Over 18: {post['over_18']}\n"
        f"Upvote Ratio: {post['upvote_ratio']}\n"
        f"Stickied: {post['is_stickied']}\n"
        f"Media: {'None' if not post['media'] else 'Media present'}"
        for post in posts
        if not post['is_stickied'] and not post['media']
    )

    final_prompt = f"{prompt_template}\n\nHere are the Reddit posts:\n\n{reddit_posts_info}"
    
    response = gemini_client.generate_content(final_prompt)

    selected_post_ids = [
        line.strip() for line in response.split("\n")
        if line.strip() and (line.startswith("Post id") or len(line.strip()) == 7)
    ]

    selected_posts = [post for post in posts if post['id'] in selected_post_ids]
    
    return selected_posts[:limit]

def create_folder_structure_for_posts(posts):
    today_date = datetime.now().strftime('%Y-%m-%d')
    base_dir = os.path.join('Backend', 'Workflows', 'data', 'Reddit to TikTok', today_date)
    folder_paths = {}

    for post in posts:
        post_id = post['id']
        subreddit_name = post['subreddit']
        subreddit_folder = os.path.join(base_dir, subreddit_name)
        os.makedirs(subreddit_folder, exist_ok=True)

        post_folder = os.path.join(subreddit_folder, f'post_{post_id}')
        os.makedirs(post_folder, exist_ok=True)
        
        folder_paths[post_id] = post_folder

        json_file_path = os.path.join(post_folder, f'post_{post_id}.json')
        with open(json_file_path, 'w') as json_file:
            json.dump(post, json_file, indent=4)
        
        logger.info(f"Saved post data as JSON: {json_file_path}")

    return folder_paths

def prepare_reddit_for_tts_via_llm(post, folder_path, prompt_path='Backend/LLM/prompts/prepare_raw_reddit_for_tts.txt'):
    try:
        gemini_client = GeminiClient()
        with open(prompt_path, 'r') as prompt_file:
            prompt_template = prompt_file.read().strip()

        reddit_post_info = {
            "title": post['title'],
            "body": post['body'],
            "comments": [
                {
                    "author": comment['author'],
                    "body": comment['body'],
                    "score": comment['score']
                }
                for comment in post.get('comments', [])
            ]
        }

        llm_prompt = prompt_template.replace("[INPUT_JSON]", json.dumps(reddit_post_info, indent=4))
        llm_response = gemini_client.generate_content(llm_prompt)

        tts_file_path = os.path.join(folder_path, 'formatted_for_tts.txt')

        with open(tts_file_path, 'w', encoding='utf-8') as tts_file:
            tts_file.write(llm_response)

        logger.info(f"Formatted Reddit post for TTS saved at: {tts_file_path}")
    except Exception as e:
        logger.error(f"Failed to prepare Reddit post for TTS: {e}")

# Async function to generate TTS
async def generate_narration_for_post(post, folder_path):
    try:
        tts_client = EdgeTTSClient()
        tts_text_file = os.path.join(folder_path, 'formatted_for_tts.txt')

        with open(tts_text_file, 'r', encoding='utf-8') as f:
            post_text = f.read()

        audio_path, vtt_path = await tts_client.synthesize_post(post_text, folder_path)

        if audio_path and vtt_path:
            logger.info(f"Narration and captions saved for post {post['id']} at {folder_path}")
        else:
            logger.error(f"Failed to generate narration for post {post['id']}")
    
    except Exception as e:
        logger.error(f"Error while generating narration for post {post['id']}: {e}")

# Function to handle TTS generation for all posts
async def generate_narrations_for_posts(posts, folder_paths):
    tasks = []
    for post in posts:
        post_id = post['id']
        folder_path = folder_paths[post_id]
        task = generate_narration_for_post(post, folder_path)
        tasks.append(task)

    await asyncio.gather(*tasks)

def create_screenshots_for_selected_posts(posts, folder_paths):
    reddit_client = RedditClient()
    screenshot_paths = []

    for post in posts:
        post_id = post['id']
        subreddit_name = post['subreddit']
        post_folder = folder_paths.get(post_id)

        screenshot_path = reddit_client.screenshot_post_preview(subreddit_name, post_id, output_dir=post_folder)

        if screenshot_path:
            logger.info(f"Screenshot saved for post {post_id} at {screenshot_path}")
            screenshot_paths.append(screenshot_path)
        else:
            logger.error(f"Failed to save screenshot for post {post_id}")
    
    return screenshot_paths

if __name__ == "__main__":
    while True:
        logger.info("Starting Reddit to TikTok Workflow...")

        # Step 1: Fetch Reddit posts (max 100)
        posts = fetch_reddit_posts(subreddit_name='LifeProTips', limit=100)
        logger.info(f"Fetched {len(posts)} posts from subreddit: LifeProTips")

        # Step 2: Filter posts via LLM using the specified prompt template
        logger.info("Building Reddit post info for LLM prompt...")
        selected_posts = filter_posts_via_llm(posts)
        logger.info(f"Selected posts: {selected_posts}")

        # Step 3: Create folder structure for the selected posts
        folder_paths = create_folder_structure_for_posts(selected_posts)

        # Step 4: Prepare each post and its comments for TTS and save it in the corresponding folder
        logger.info("Preparing posts for TTS...")
        for post in selected_posts:
            post_id = post['id']
            folder_path = folder_paths[post_id]
            prepare_reddit_for_tts_via_llm(post, folder_path)
        
        # Step 5: Generate narrations for the selected posts using TTS
        logger.info("Generating narrations for selected posts...")
        asyncio.run(generate_narrations_for_posts(selected_posts, folder_paths))

        # Step 6: Create screenshots for the selected posts
        logger.info("Creating screenshots for selected posts...")
        screenshot_paths = create_screenshots_for_selected_posts(selected_posts, folder_paths)
        logger.info(f"Screenshots saved: {screenshot_paths}")

        # Step 7: Wait before the next run
        logger.info("Workflow completed. Waiting for next run.")
        time.sleep(86400)  # Wait 24 hours before the next run