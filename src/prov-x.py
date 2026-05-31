import tweepy
from config import require_env

# Set up the Bearer Token
bearer_token = require_env("X_BEARER_TOKEN")

# Initialize the client
client = tweepy.Client(bearer_token=bearer_token)

def get_retweets(tweet_id):
    """
    Get the users who retweeted a specific tweet.

    Args:
        tweet_id (int): The ID of the tweet.

    Returns:
        list: A list of retweet URLs.
    """
    retweet_urls = []
    try:
        # Fetch retweets using the retweeted_by expansion
        response = client.get_retweeters(
            id=tweet_id, user_fields=["username"], max_results=30
        )

        # Extract retweeters and construct their retweet URLs
        if response.data:
            for user in response.data:
                retweet_url = f"https://twitter.com/{user.username}/status/{tweet_id}"
                retweet_urls.append(retweet_url)

    except tweepy.TweepyException as e:
        print(f"Error fetching retweets: {e}")

    return retweet_urls

# Example usage
if __name__ == "__main__":
    tweet_id = 1864061407672631504  # Replace with your tweet ID
    retweets = get_retweets(tweet_id)
    print("Retweet URLs:")
    for url in retweets:
        print(url)
