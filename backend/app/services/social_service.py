import requests

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class SocialService:

    def __init__(self):

        self.analyzer = SentimentIntensityAnalyzer()


    def _score_sentiment(self, text: str):

        score = self.analyzer.polarity_scores(text)["compound"]

        if score >= 0.2:
            return "Bullish"

        if score <= -0.2:
            return "Bearish"

        return "Neutral"

    def get_reddit_posts(self, symbol="BTC"):

        posts = []

        subreddits = [
            "wallstreetbets",
            "stocks",
            "cryptocurrency",
            "Forex",
        ]

        headers = {
            "User-Agent": "QuantView"
        }

        try:

            for sub in subreddits:

                url = f"https://www.reddit.com/r/{sub}/search.json?q={symbol}&limit=5&sort=new"

                response = requests.get(url, headers=headers, timeout=10)

                if response.status_code != 200:
                    continue

                data = response.json()

                children = data.get("data", {}).get("children", [])

                for child in children:

                    post = child.get("data", {})

                    title = post.get("title", "")

                    sentiment = self._score_sentiment(title)

                    posts.append({
                        "platform": "Reddit",
                        "subreddit": sub,
                        "title": title,
                        "score": post.get("score", 0),
                        "url": f"https://reddit.com{post.get('permalink', '')}",
                        "sentiment": sentiment,
                    })

            return posts[:20]

        except Exception as e:
            print("Reddit fetch error:", e)
            return []

    def get_stocktwits_posts(self, symbol="BTC"):

        try:

            url = f"https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json"

            response = requests.get(url, timeout=10)

            if response.status_code != 200:
                return []

            data = response.json()

            posts = []

            for msg in data.get("messages", [])[:10]:

                body = msg.get("body", "")

                sentiment = self._score_sentiment(body)

                posts.append({
                    "platform": "StockTwits",
                    "user": msg.get("user", {}).get("username"),
                    "body": body,
                    "likes": msg.get("likes", {}).get("total", 0),
                    "sentiment": sentiment,
                })

            return posts

        except Exception as e:
            print("StockTwits fetch error:", e)
            return []

    def get_combined_sentiment(self, symbol="BTC"):

        reddit_posts = self.get_reddit_posts(symbol)

        stocktwits_posts = self.get_stocktwits_posts(symbol)

        combined = reddit_posts + stocktwits_posts

        bullish = sum(1 for p in combined if p["sentiment"] == "Bullish")

        bearish = sum(1 for p in combined if p["sentiment"] == "Bearish")

        neutral = sum(1 for p in combined if p["sentiment"] == "Neutral")

        overall = "Neutral"

        if bullish > bearish:
            overall = "Bullish"

        elif bearish > bullish:
            overall = "Bearish"

        trending_score = bullish + bearish + neutral

        return {
            "overall_sentiment": overall,
            "bullish": bullish,
            "bearish": bearish,
            "neutral": neutral,
            "trending_score": trending_score,
            "posts": combined[:20],
        }