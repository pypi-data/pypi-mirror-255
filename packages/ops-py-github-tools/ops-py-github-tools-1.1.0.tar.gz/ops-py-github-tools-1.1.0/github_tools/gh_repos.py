#!/usr/bin/env python

import requests


########################################################################################################################


class GithubRepos(object):
    """
    A selection of GitHub repo api calls.

    ...

    Attributes
    ----------
    repo : str
        The name of the repo, including the owner. E.g.: equinor/ops-py
    api_url : str
        The GitHub repos api url. Defaults to: "https://api.github.com/repos"
    headers : dict
        The header part of the GitHub API payload
    repo_url : str
        The full url to the repo. Starts with the 'api_url' followed by the 'repo'.
        E.g.: "https://api.github.com/repos/equinor/ops-py"

    Methods
    -------
    set_repo_url(repo="")
        Set the 'repo_url'
        Will consist of the value from 'api_url' and the value of the provided 'repo' argument
        If 'repo' argument is not provided, then the init value of 'repo' will be used.
    get_headers()
        Returns the 'headers'.
    get_repo_url()
        Returns the 'repo_url'.
    do_request(url)
        Performs the request to the provided url with the init 'headers'.
    get_pulls(repo="")
        Calls the set_repo_url method to update the 'repo_url' if 'repo' argument is provided.
        Set the 'url' and calls the do_request method with the 'url' provided as argument.
        Returns the result.
    get_pulls(repo="")
        Calls the set_repo_url method to update the 'repo_url' if 'repo' argument is provided.
        Set the 'url' and calls the do_request method with the 'url' provided as argument.

        Will request the GitHub API for all the open Pull Requests in the repo.
        Returns the list of open Pull Requests.
    get_pull_request(pull_number, repo="", state_only=False)
        Calls the set_repo_url method to update the 'repo_url' if 'repo' argument is provided.
        Set the 'url' and calls the do_request method with the 'url' provided as argument.

        Will request the GitHub API for the provided 'pull_number'
        Returns the Pull Requests.

        If 'state_only' argument is set to True, only the state of Pull Request will be returned.
        'open', 'closed'...
    get_milestones(repo="")
        Calls the set_repo_url method to update the 'repo_url' if 'repo' argument is provided.
        Set the 'url' and calls the do_request method with the 'url' provided as argument.

        Will request the GitHub API for all the milestones in the repo.
        Returns the list of milestones.
    """
    def __init__(self, token, repo=""):
        """
        Parameters
        ----------
        token : str
            The GitHub Personal Access Token
            https://github.com/settings/tokens
            https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
        repo : str
            The name of the repo, including the owner. E.g.: equinor/ops-py
        """
        self.repo = repo
        self.api_url = "https://api.github.com/repos"
        self.headers = {
             'Accept': 'application/vnd.github+json',
             'Authorization': f'Bearer {token}',
             'X-GitHub-Api-Version': '2022-11-28'
             }
        self.repo_url = ""
        self.set_repo_url()

    def set_repo_url(self, repo=""):
        """set the 'repo_url' with the value from 'api_url' and the value of the 'repo' argument."""
        if repo:
            self.repo = repo
        self.repo_url = f"{self.api_url}/{self.repo}"

    def get_headers(self):
        """returns the request headers"""
        return self.headers

    def get_repo_url(self):
        """returns the repo_url"""
        return self.repo_url

    def do_request(self, url):
        """performs the request to the provided url"""
        result = None
        r = requests.get(url, headers=self.headers)
        if r:
            try:
                result = r.json()
            except:
                pass
        return result

    def get_pulls(self, repo=""):
        """request the GitHub API for a list of all the open Pull Requests in the repo"""
        if repo:
            self.set_repo_url(repo)

        url = f"{self.repo_url}/pulls"
        res = self.do_request(url)
        return res

    def get_pull_request(self, pull_number, repo="", state_only=False):
        """request the GitHub API for a specific Pull Request number"""
        if repo:
            self.set_repo_url(repo)

        url = f"{self.repo_url}/pulls/{pull_number}"
        res = self.do_request(url)
        if res and state_only:
            return res.get("state")
        if res:
            return res

    def get_milestones(self, repo=""):
        """request the GitHub API for a list of all the defined milestones"""
        if repo:
            self.set_repo_url(repo)

        url = f"{self.repo_url}/milestones"
        res = self.do_request(url)
        return res
