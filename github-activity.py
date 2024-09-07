import os
import requests
import argparse
import logging

from functools import lru_cache
from logging.handlers import RotatingFileHandler

EVENT_TYPE_TO_TEXT_MAPPING = {
    "CommitCommentEvent": "Created a commit comment in",
    "CreateEvent": "Created a git branch or tag in",
    "DeleteEvent": "Deleted a git branch or tag from",
    "ForkEvent": "Forked repo",
    "GollumEvent": "Created or updated a wiki page in",
    "IssueCommentEvent": ""
}

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

def fetch_events(username: str, event_type: str):
    url = f"https://api.github.com/users/{username}/events"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

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
                print(event)
                # output += f"- {EVENT_TYPE_TO_TEXT_MAPPING[event['type']]} {event['repo']['name']} on {event['created_at']}\n"
            # print(output)

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
    parser.add_argument("username", type=str, help="GitHub username")
    parser.add_argument(
        "event_type",
        nargs="?",
        choices=[
            "all",
            "CommitCommentEvent",
            "CreateEvent",
            "DeleteEvent",
            "ForkEvent",
            "GollumEvent",
            "IssueCommentEvent",
            "IssuesEvent",
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
        help="Event type"
    )

    args = parser.parse_args()

    fetch_events(args.username, args.event_type)
