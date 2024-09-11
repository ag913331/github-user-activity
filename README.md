# GitHub User Activity CLI

This CLI fetches and displays both public and private activity from GitHub for a specific user. It supports fetching a variety of event types including comments on commits and issues, as well as repository membership details.

[Project URL](https://roadmap.sh/projects/github-user-activity)

## Features
- Fetch **public** GitHub events like commits, pushes, and more.
- Fetch **private** events like issue comments or commits for repositories where a [fine-grained token](https://docs.github.com/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token) is required.
- Check a user's repository membership and their permission level.
- Support for various GitHub event types:
  - `CommitCommentEvent` (Requires a `GITHUB_FINE_GRAINED_TOKEN` and account `OWNER` environment variables)
  - `CreateEvent`
  - `DeleteEvent`
  - `ForkEvent`
  - `GollumEvent`
  - `IssueCommentEvent` (Requires a `GITHUB_FINE_GRAINED_TOKEN` and account `OWNER` environment variables)
  - `IssuesEvent` (Requires a `GITHUB_FINE_GRAINED_TOKEN` and account `OWNER` environment variables)
  - `MemberEvent` (Requires a `GITHUB_FINE_GRAINED_TOKEN` and account `OWNER` environment variables)
  - `PushEvent`

  As of today `09/11/2024`, the CLI does not yet support following events filtering: `PullRequestEvent`, `PullRequestReviewCommentEvent`, `PullRequestReviewThreadEvent`, `ReleaseEvent`, `SponsorshipEvent`, `WatchEvent`. However, some of them might still appear as part of the public events.

## Setup & Installation

1. Clone the Repository
```bash
git@github.com:ag913331/github-user-activity.git
cd github-user-activity
```

2. Run `setup.sh`
```
chmod +x setup.sh
./setup.sh
```
This will create a vitual environment called `venv` and install packages `requests` and `python-dotenv` necessary for API requests and reading environment variables.

Alternatively, you could perform these actions manually.
```bash
#!/bin/bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Activate `venv` virtual environment
```bash
source venv/bin/activate
```

4. Setup environment variables
You need to provide the following environment variables in a `.env` file in the root of the project:
```bash
GITHUB_FINE_GRAINED_TOKEN=<your-github-fine-grained-token>
OWNER=<your-github-account-owner>
```

The `GITHUB_FINE_GRAINED_TOKEN` is required for accessing private events in repositories. The `OWNER` variable should be set to the GitHub account or organization that owns the repositories.

## Usage

### Command-line Arguments
- `-u, --user`: (Required) The GitHub username whose activity you want to retrieve.
- `-e, --event_type`: (Optional) The type of event to fetch. Defaults to `all` (all public events). Supported values:
  - `all`
  - `CommitCommentEvent` (requires repo)
  - `CreateEvent`
  - `DeleteEvent`
  - `ForkEvent`
  - `GollumEvent`
  - `IssueCommentEvent` (requires repo)
  - `IssuesEvent` (requires repo)
  - `MemberEvent` (requires repo)
  - `PushEvent`
- `-r, --repo`: (Optional) The repository to fetch events for (required for specific event types like `CommitCommentEvent` and `IssuesEvent`).

### Examples

**Fetch Public Events**
```bash
python github_activity.py -u <username>
```

**Fetch Events for a specific event type**
```bash
python github_activity.py -u <username> -e IssueCommentEvent -r <repository>
```

### Logs
Logs are stored in the `logs/` directory, rotating after 10MB in size with up to 10 backup files. Logs are also printed to the console.

## Error Handling
- If the GitHub token or owner is missing, you will receive a log error.
- If you exceed the GitHub API rate limit, an appropriate error message is logged.
- 404 or 403 errors are handled and logged with the relevant message.

## License
This project is licensed under the MIT License.