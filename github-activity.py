import os
import sys
import requests
import argparse
import logging

from dotenv import load_dotenv
from functools import lru_cache
from logging.handlers import RotatingFileHandler

load_dotenv()

GITHUB_FINE_GRAINED_TOKEN = os.getenv("GITHUB_FINE_GRAINED_TOKEN")
OWNER = os.getenv("OWNER")

@lru_cache(maxsize=None)
def get_logger(log_name):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(
        logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
    )

    os.makedirs(f"logs", exist_ok=True)
    fh = RotatingFileHandler(
        f"logs/{log_name}.log", 
        maxBytes=1024 * 1024 * 10, 
        backupCount=10
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(
        logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
    )

    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger

LOGGER = get_logger("github-user-activity")

def fetch_repo_events(username: str, repo: str, event_type: str):
    if not GITHUB_FINE_GRAINED_TOKEN:
        LOGGER.error("Error: GitHub access token is missing. Please set GITHUB_FINE_GRAINED_TOKEN in your environment.")
        return
    
    if not OWNER:
        LOGGER.error("Error: GitHub account owner is missing. Please set OWNER in your environment.")
        return
        
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"Bearer {GITHUB_FINE_GRAINED_TOKEN}"
    }

    url = f"https://api.github.com/repos/{OWNER}/{repo}/comments"

    if event_type == "IssueCommentEvent":
        url = f"https://api.github.com/repos/{OWNER}/{repo}/issues"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        events = response.json()

        if not events:
            LOGGER.error(f"No events found for user: {username}")
            return

        if event_type == "CommitCommentEvent":
            output = f"CommitCommentEvent Activity:\n{username} has {len(events)} CommitCommentEvent activities\n-------------------------------------\n"
            for useract in events:
                output += f"  URL: {useract['url']}\n  Commit Body: {useract['body']}\n  Created: {useract['created_at']}\n-------------------------------------\n"
            print(output)
        elif event_type == "IssueCommentEvent":
            filtered_events = [event for event in events if event['assignee']['login'] == username]
            output = f"IssueCommentEvent Activity:\n{username} has {len(filtered_events)} IssueCommentEvent activities\n-------------------------------------\n"
            for event in filtered_events:
                output += f"  - Added {event['comments']} comments on issue: {event['title']}\n-------------------------------------\n"
            print(output)

    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            LOGGER.error(f"User '{username}' not found. Please check the username and try again.")
        elif response.status_code == 403 and 'X-RateLimit-Remaining' in response.headers and response.headers['X-RateLimit-Remaining'] == '0':
            LOGGER.error("Error: Rate limit exceeded. Please try again later.")
        else:
            LOGGER.error(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        LOGGER.error(f"Network error occurred: {req_err}")
    except Exception as e:
        LOGGER.error(f"An unexpected error occurred: {e}")

def fetch_public_events(username: str, event_type: str):
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        # "Authorization": f"Bearer {GITHUB_FINE_GRAINED_TOKEN}"
    }
    url = f"https://api.github.com/users/{username}/events"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        events = response.json()

        if not events:
            LOGGER.error(f"No events found for user: {username}")
            return

        if event_type == "all":
            filtered_events = events
        else:
            filtered_events = [event for event in events if event["type"] == event_type]

        if not filtered_events:
            LOGGER.error(f"No '{event_type}' events found for user: {username}")
        else:
            output = "Output: \n"
            for event in filtered_events:
                if event["type"] == "CreateEvent":
                    output += f"  - Created a {event['payload']['ref_type']} in {event['repo']['name']} at {event['created_at']}\n"
                elif event["type"] == "DeleteEvent":
                    output += f"  - Deleted {event['payload']['ref_type']} [{event['payload']['ref']}] at {event['created_at']}\n"
                elif event["type"] == "ForkEvent":
                    output += f"  - Forked {event['repo']['name']} into {event['payload']['forkee']['name']} at {event['created_at']}\n"
                elif event["type"] == "GollumEvent":
                    output += f"  - Created {len(event['payload']['pages'])} wiki pages in {event['repo']['name']}"
                else:
                    print(event)
            print(output)

    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            LOGGER.error(f"User '{username}' not found. Please check the username and try again.")
        elif response.status_code == 403 and 'X-RateLimit-Remaining' in response.headers and response.headers['X-RateLimit-Remaining'] == '0':
            LOGGER.error("Error: Rate limit exceeded. Please try again later.")
        else:
            LOGGER.error(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        LOGGER.error(f"Network error occurred: {req_err}")
    except Exception as e:
        LOGGER.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GitHub User Activity CLI")
    parser.add_argument("-u", "--user", type=str, help="GitHub username")
    parser.add_argument(
        "-e",
        "--event_type",
        choices=[
            "all",
            "CommitCommentEvent", #token #owner
            "CreateEvent",
            "DeleteEvent",
            "ForkEvent",
            "GollumEvent",
            "IssueCommentEvent", #token #owner
            # "IssuesEvent",
            "MemberEvent",
            "PublicEvent",
            "PullRequestReviewEvent",
            "PullRequestReviewCommentEvent",
            "PullRequestReviewThreadEvent",
            "PushEvent",
            "ReleaseEvent",
            "SponsorshipEvent",
            "WatchEvent"
        ],
        type=str,
        default="all",
        required=False,
        help="Event type"
    )
    parser.add_argument("-r", "--repo", type=str, required=False, help="Repository username")

    args = parser.parse_args()
    if args.event_type in ["CommitCommentEvent", "IssueCommentEvent"]:
        if not args.repo:
            LOGGER.warning("CommitCommentEvent endpoints require a repository name. Try `python github-activity.py -u <username> -e <event_type> -r <repository_name>`")
            sys.exit(1)
        fetch_repo_events(args.user, args.repo, args.event_type)
    else:
        fetch_public_events(args.user, args.event_type)
