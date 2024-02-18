#!/usr/bin/env python

import os
from gh_repos import GithubRepos
from gh_create_milestone import CreateMilestone


########################################################################################################################


def main():
    gh = GithubRepos(GITHUB_TOKEN, repo=REPO)

    # Get all open Pull requests
    pulls = gh.get_pulls(REPO)
    print(pulls)

    # Get state for a specific Pull request
    pr = gh.get_pull_request(226)
    print(pr)

    # Get a specific Pull request
    pr = gh.get_pull_request(226, state_only=True)
    print(pr)

    # Create a milestone
    milestone = "2024-02-01"
    gh = GithubRepos(GITHUB_TOKEN, repo=REPO)
    headers = gh.get_headers()
    repo_url = gh.get_repo_url()
    ms = CreateMilestone(headers, repo_url, milestone)
    ms.create_milestone()


########################################################################################################################


if __name__ == '__main__':
    REPO = "equinor/ops-py"
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # https://github.com/settings/tokens
    main()
