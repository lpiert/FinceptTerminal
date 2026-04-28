#!/usr/bin/env python3
"""
reddit_sentiment.py - Reddit Sentiment Analysis for Stock Symbols

[STUB] This script requires user to configure Reddit API credentials.
Free alternative to Fincept's proprietary sentiment analysis.

Usage:
    python reddit_sentiment.py AAPL --limit 50
    python reddit_sentiment.py TSLA,BTC --subreddit wallstreetbets
    
Requirements:
    pip install praw textblob pandas

Configuration:
    Set environment variables or edit the CONFIG section below:
    - REDDIT_CLIENT_ID
    - REDDIT_CLIENT_SECRET
    - REDDIT_USER_AGENT
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# [STUB] User must configure these credentials
# Get them from: https://www.reddit.com/prefs/apps
CONFIG = {
    "client_id": os.getenv("REDDIT_CLIENT_ID", "YOUR_CLIENT_ID"),
    "client_secret": os.getenv("REDDIT_CLIENT_SECRET", "YOUR_CLIENT_SECRET"),
    "user_agent": os.getenv("REDDIT_USER_AGENT", "FinceptTerminal/1.0 by /u/YOUR_USERNAME"),
}

try:
    import praw
    from textblob import TextBlob
    import pandas as pd
except ImportError:
    print("Error: Required packages not installed.")
    print("Run: pip install praw textblob pandas")
    sys.exit(1)


class RedditSentimentAnalyzer:
    """Analyze Reddit sentiment for stock/crypto symbols"""
    
    def __init__(self):
        if CONFIG["client_id"] == "YOUR_CLIENT_ID":
            raise ValueError(
                "❌ Reddit API credentials not configured!\n"
                "Please set environment variables:\n"
                "  export REDDIT_CLIENT_ID=your_client_id\n"
                "  export REDDIT_CLIENT_SECRET=your_secret\n"
                "  export REDDIT_USER_AGENT='FinceptTerminal/1.0 by /u/username'\n"
                "\nOr edit the CONFIG section in this file."
            )
        
        self.reddit = praw.Reddit(
            client_id=CONFIG["client_id"],
            client_secret=CONFIG["client_secret"],
            user_agent=CONFIG["user_agent"],
        )
        
    def analyze_symbol(self, symbol: str, limit: int = 50, 
                      subreddits: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze sentiment for a given symbol
        
        Args:
            symbol: Stock/crypto symbol (e.g., AAPL, BTC)
            limit: Max posts/comments to analyze
            subreddits: List of subreddits to search (default: popular finance subs)
            
        Returns:
            Dictionary with sentiment analysis results
        """
        if subreddits is None:
            subreddits = [
                "wallstreetbets",
                "stocks",
                "investing",
                "SecurityAnalysis",
                "StockMarket",
                "pennystocks",
                "options",
                "cryptocurrency",
            ]
        
        print(f"🔍 Analyzing sentiment for {symbol}...")
        print(f"   Searching {len(subreddits)} subreddits, limit={limit}")
        
        all_posts = []
        total_analyzed = 0
        
        for subreddit_name in subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Search for symbol mentions
                search_query = f"{symbol} OR ${symbol}" if len(symbol) <= 5 else symbol
                
                for submission in subreddit.search(search_query, limit=limit // len(subreddits), sort="hot"):
                    # Skip if too old (>7 days)
                    if datetime.fromtimestamp(submission.created_utc) < datetime.now() - timedelta(days=7):
                        continue
                    
                    # Analyze title and selftext
                    text_to_analyze = submission.title
                    if submission.selftext:
                        text_to_analyze += " " + submission.selftext[:500]  # Limit length
                    
                    blob = TextBlob(text_to_analyze)
                    polarity = blob.sentiment.polarity  # -1 (negative) to 1 (positive)
                    subjectivity = blob.sentiment.subjectivity  # 0 (objective) to 1 (subjective)
                    
                    post_data = {
                        "id": submission.id,
                        "title": submission.title[:100],
                        "url": submission.shortlink,
                        "score": submission.score,
                        "num_comments": submission.num_comments,
                        "created_utc": submission.created_utc,
                        "subreddit": subreddit_name,
                        "sentiment_polarity": polarity,
                        "sentiment_subjectivity": subjectivity,
                        "sentiment_label": self._classify_sentiment(polarity),
                    }
                    
                    all_posts.append(post_data)
                    total_analyzed += 1
                    
            except Exception as e:
                print(f"⚠️  Error searching r/{subreddit_name}: {str(e)}")
                continue
        
        if not all_posts:
            return {
                "success": False,
                "error": f"No posts found for {symbol}",
                "symbol": symbol,
            }
        
        # Calculate aggregate statistics
        df = pd.DataFrame(all_posts)
        
        results = {
            "success": True,
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "total_posts_analyzed": total_analyzed,
            "time_range_days": 7,
            "subreddits_searched": subreddits,
            
            "aggregate_sentiment": {
                "mean_polarity": float(df["sentiment_polarity"].mean()),
                "median_polarity": float(df["sentiment_polarity"].median()),
                "std_polarity": float(df["sentiment_polarity"].std()),
                "mean_subjectivity": float(df["sentiment_subjectivity"].mean()),
            },
            
            "sentiment_distribution": {
                "positive": int((df["sentiment_polarity"] > 0.1).sum()),
                "neutral": int(((df["sentiment_polarity"] >= -0.1) & (df["sentiment_polarity"] <= 0.1)).sum()),
                "negative": int((df["sentiment_polarity"] < -0.1).sum()),
            },
            
            "engagement_metrics": {
                "total_score": int(df["score"].sum()),
                "mean_score": float(df["score"].mean()),
                "total_comments": int(df["num_comments"].sum()),
                "mean_comments": float(df["num_comments"].mean()),
            },
            
            "top_positive_posts": self._get_top_posts(df, "positive", top_n=5),
            "top_negative_posts": self._get_top_posts(df, "negative", top_n=5),
            "most_discussed": self._get_top_posts(df, "comments", top_n=5),
        }
        
        print(f"✅ Analysis complete!")
        print(f"   Posts analyzed: {total_analyzed}")
        print(f"   Mean sentiment: {results['aggregate_sentiment']['mean_polarity']:.3f}")
        print(f"   Positive: {results['sentiment_distribution']['positive']}")
        print(f"   Neutral: {results['sentiment_distribution']['neutral']}")
        print(f"   Negative: {results['sentiment_distribution']['negative']}")
        
        return results
    
    def _classify_sentiment(self, polarity: float) -> str:
        """Classify sentiment based on polarity score"""
        if polarity > 0.1:
            return "positive"
        elif polarity < -0.1:
            return "negative"
        else:
            return "neutral"
    
    def _get_top_posts(self, df: pd.DataFrame, sort_by: str, top_n: int = 5) -> List[Dict]:
        """Get top N posts by various criteria"""
        if sort_by == "positive":
            sorted_df = df.nlargest(top_n, "sentiment_polarity")
        elif sort_by == "negative":
            sorted_df = df.nsmallest(top_n, "sentiment_polarity")
        elif sort_by == "comments":
            sorted_df = df.nlargest(top_n, "num_comments")
        else:
            sorted_df = df.head(top_n)
        
        return sorted_df[["title", "url", "score", "num_comments", "sentiment_polarity"]].to_dict("records")


def main():
    parser = argparse.ArgumentParser(description="Reddit Sentiment Analysis for Stocks/Crypto")
    parser.add_argument("symbols", help="Comma-separated symbols (e.g., AAPL,TSLA,BTC)")
    parser.add_argument("--limit", type=int, default=50, help="Max posts per symbol (default: 50)")
    parser.add_argument("--subreddit", help="Specific subreddit to search (optional)")
    parser.add_argument("--output", help="Output JSON file (optional)")
    
    args = parser.parse_args()
    
    symbols = [s.strip().upper() for s in args.symbols.split(",")]
    subreddits = [args.subreddit] if args.subreddit else None
    
    analyzer = RedditSentimentAnalyzer()
    
    all_results = {}
    
    for symbol in symbols:
        try:
            result = analyzer.analyze_symbol(symbol, limit=args.limit, subreddits=subreddits)
            all_results[symbol] = result
            
            # Small delay between symbols to avoid rate limiting
            if len(symbols) > 1:
                import time
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {str(e)}")
            all_results[symbol] = {"success": False, "error": str(e)}
    
    # Output results
    output_json = json.dumps(all_results, indent=2)
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_json)
        print(f"\n💾 Results saved to: {args.output}")
    else:
        print("\n" + "="*60)
        print(output_json)


if __name__ == "__main__":
    main()
