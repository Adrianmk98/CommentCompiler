import configparser
from datetime import datetime, timedelta
import praw



def fetch_recent_posts(reddit,days):
    """Fetches recent posts from 'cmhoc' subreddit within the past number of days.
    Gets the number of days from the """
    subreddit = reddit.subreddit('cmhoc')
    recent_posts = []
    time_limit = datetime.utcnow() - timedelta(days=days)

    for submission in subreddit.new(limit=100):  # Fetch recent 100 posts
        submission_time = datetime.utcfromtimestamp(submission.created_utc)
        if submission_time >= time_limit:
            recent_posts.append((submission.title, submission.created_utc, submission.url))

    return recent_posts



