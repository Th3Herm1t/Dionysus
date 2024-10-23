import praw
from .config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
from prawcore.exceptions import NotFound, RequestException
import time
import undetected_chromedriver as uc
import os
from selenium.webdriver.common.by import By
from PIL import Image
from datetime import datetime

class RedditClient:
    def __init__(self):
        try:
            self.reddit = praw.Reddit(
                client_id=REDDIT_CLIENT_ID,
                client_secret=REDDIT_CLIENT_SECRET,
                user_agent=REDDIT_USER_AGENT
            )
        except Exception as e:
            print(f"Error initializing Reddit client: {e}")
            raise

    def convert_timestamp(self, ts):
        """Convert UNIX timestamp to a human-readable format."""
        return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    def fetch_top_posts(self, subreddit_name, limit=5, time_filter='day', include_comments=False, comments_limit=100):
        """
        Fetch top posts and optionally comments from a specific subreddit.
        
        :param subreddit_name: Name of the subreddit (e.g., 'funny')
        :param limit: Number of posts to fetch (default is 5)
        :param time_filter: Time filter for top posts ('day', 'week', 'month', 'year', 'all')
        :param include_comments: Boolean, whether to fetch comments for each post
        :param comments_limit: Number of top comments to fetch (if include_comments is True)
        :return: List of dictionaries containing post details (and optionally comments)
        """
        valid_time_filters = ['day', 'week', 'month', 'year', 'all']
        if time_filter not in valid_time_filters:
            raise ValueError(f"Invalid time_filter value. Allowed values: {valid_time_filters}")

        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            top_posts = subreddit.top(time_filter=time_filter, limit=limit)
        except NotFound:
            print(f"Subreddit '{subreddit_name}' not found.")
            return []
        except RequestException as e:
            print(f"Network error occurred: {e}")
            return []
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return []

        posts_data = []
        for post in top_posts:
            post_data = {
                'title': post.title,
                'author': post.author.name if post.author else '[deleted]',
                'score': post.score,
                'id': post.id,
                'url': post.url,
                'num_comments': post.num_comments,
                'created': self.convert_timestamp(post.created_utc),
                'body': post.selftext if post.selftext else 'N/A',
                'is_stickied': post.stickied,
                'gilded': post.gilded,
                'over_18': post.over_18,
                'subreddit': post.subreddit.display_name,
                'upvote_ratio': post.upvote_ratio,
                'flair': post.link_flair_text if post.link_flair_text else 'N/A',
                'media': post.media['o'] if post.media and 'o' in post.media else None
            }

            # Fetch top comments if include_comments is True
            if include_comments:
                post.comments.replace_more(limit=0)  # Load all comments
                comments = post.comments.list()[:comments_limit]
                post_data['comments'] = []

                for comment in comments:
                    if comment.author and comment.author.name != 'AutoModerator':  # Skip AutoModerator comments
                        post_data['comments'].append({
                            'author': comment.author.name,
                            'body': comment.body,
                            'score': comment.score,
                            'created': self.convert_timestamp(comment.created_utc),
                            'gilded': comment.gilded,
                            'is_submitter': comment.is_submitter,
                            'parent_id': comment.parent_id,
                            'link_id': comment.link_id,
                            'comment_id': comment.id
                        })

            posts_data.append(post_data)
        
        return posts_data

    def screenshot_post_preview(self, subreddit_name, post_id, output_dir=r'Backend\data\reddit_screenshots', chrome_profile_path=None):
        """
        Takes a screenshot of a specific Reddit post element from the post's page.

        :param subreddit_name: Name of the subreddit (e.g., 'funny')
        :param post_id: ID of the post (e.g., '1g78sgf')
        :param output_dir: Directory to save the screenshots (default is 'screenshots')
        :param chrome_profile_path: Path to the Chrome user profile to maintain the login session
        :return: Path to the saved screenshot of the post element
        """
        # Ensure the output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Initialize undetected ChromeDriver
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        # Use a user profile if provided
        if chrome_profile_path:
            options.add_argument(f"user-data-dir={chrome_profile_path}")  # Path to Chrome user profile

        # Initialize undetected ChromeDriver with options
        driver = uc.Chrome(options=options)

        try:
            # Navigate to the specific post page
            reddit_post_url = f"https://www.reddit.com/r/{subreddit_name}/comments/{post_id}/"
            driver.get(reddit_post_url)
            time.sleep(3)  # Give the page some time to load

            # Select the post element using the post_id
            post_element_selector = f"#t3_{post_id}"
            post_element = driver.find_element(By.CSS_SELECTOR, post_element_selector)

            # Take the screenshot of the post element
            screenshot_path = os.path.join(output_dir, f"post_{post_id}.png")
            post_element.screenshot(screenshot_path)

            # Verify if screenshot file was actually saved
            if os.path.exists(screenshot_path):
                print(f"Screenshot saved to: {screenshot_path}")
            else:
                print(f"Screenshot was not saved to {screenshot_path}. Check file permissions and path.")
                screenshot_path = None

        except Exception as e:
            print(f"Error taking screenshot for post {post_id}: {e}")
            screenshot_path = None
        finally:
            try:
                driver.quit()  # Close the ChromeDriver session
            except OSError as os_error:
                print(f"OSError while quitting driver: {os_error}")
            except Exception as e:
                print(f"Exception while quitting driver: {e}")

        return screenshot_path



