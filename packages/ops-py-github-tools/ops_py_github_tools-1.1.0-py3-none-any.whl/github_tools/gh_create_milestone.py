#!/usr/bin/env python

import json
import calendar
import requests
from datetime import datetime


########################################################################################################################


def get_duedate(title):
    """calculates the due date for a two weeks period of the provided 'title' argument

    Expect the provided milestone 'title' to be in the format of "{year}-{month}-{period}".
    The period may be either '01' or '02'.

    Example "2023-12-01":

    If the period is '01' we know the due date will be by midnight in two week from the first of the month.
    Returns "2023-12-14T23:59:59Z"

    Example "2023-12-02":
    If the period is '02' it will be by midnight of the last day of the month. Might be 28, 29, 30 or 31.
    Uses the monthrange function of the calendar module to calculate this.
    Return "2023-12-31T23:59:59Z"
    """

    try:
        year, month, period = title.split("-")
    except:
        return

    if int(period) == 1:
        return f"{year}-{month}-14T23:59:59Z"

    dt = datetime(int(year), int(month), int(period))
    res = calendar.monthrange(dt.year, dt.month)
    day = res[1]
    return f"{year}-{month}-{day}T23:59:59Z"


class CreateMilestone(object):
    """
    Create a GitHub milestone in repo with due date.

    ...

    Attributes
    ----------
    headers : dict
        The header part of the GitHub API payload.

    url : str
        The GitHub api milestones url.

    title : str
        The milestone title in the format of "{year}-{month}-{period}".
        year = yyyy
        month = (01 -> 12)
        period = (01 -> 02)
        E.g.: "2023-12-01"

    payload : dict
        The payload posted to the GitHub api milestones url


    Methods
    -------
    do_post()
        Performs the post of payload to the GitHub api milestones url.
        Returns the result if success

    create_milestone()
        Calls the get_duedate function with milestone 'title' as argument.
        Add the returned due_date result to the payload and calls the do_post method.
    """

    def __init__(self, headers, repo_url, title):
        """
        Parameters
        ----------
        headers : str
            The GitHub API header
        repo_url : str
            The complete url to the GitHub API including owner/repo
            E.g.: "https://api.github.com/repos/equinor/ops-py"
        title : str
            The milestone title in the format of "{year}-{month}-{period}".
            year = yyyy, month = (01 -> 12), period = (01 -> 02). E.g.: "2023-12-01"
        """

        self.headers = headers
        self.url = f"{repo_url}/milestones"
        self.title = title
        self.payload = {"title": self.title, "state": "open", "due_on": ""}

    def do_post(self):
        """post payload to the GitHub api milestones url"""

        result = None
        r = requests.post(self.url,
                          headers=self.headers,
                          data=json.dumps(self.payload))
        if not r:
            # Creating milestone for repo failed (probably exists).
            return

        try:
            result = r.json()
        except:
            # Creating milestone for repo failed.
            pass

        return result

    def create_milestone(self):
        """set 'due_on' in payload to value of due_date and calls the do_post method"""

        due_date = get_duedate(self.title)
        if not due_date:
            return

        self.payload["due_on"] = due_date
        res = self.do_post()
        return res
