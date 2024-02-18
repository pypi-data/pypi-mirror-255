import os
import sys  # don't remove required for error handling

from importlib import util  # library management
import csv
import requests

from datetime import date, datetime


class GitHubIssue:
    @staticmethod
    def write_issues(r, csvout):
        "output a list of issues to csv"
        if not r.status_code == 200:
            raise Exception(r.status_code)
        for issue in r.json():
            Tag = []
            labels = issue["labels"]
            for label in labels:
                Tag.append(label["name"])

            csvout.writerow(
                [
                    issue["number"],
                    issue["title"].encode("utf-8"),
                    Tag,
                    issue["state"],
                    issue["created_at"],
                    issue["closed_at"],
                ]
            )

    @classmethod
    def import_issues_to_csv_from_github(cls, config: dict) -> str:
        """Uses basic authentication (Github username + password) to retrieve Issues
        from a repository that username has access to and writes the issues to a csv file.
        Supports Github API v3.

        Args:
            config (dict): Environment configuration dictionary

        Returns:
            str: Import status message
        """

        GITHUB_USER = "USER NAME"
        GITHUB_PASSWORD = "PASSWORD"
        REPO = "REPO NAME"  # format is username/repo
        ISSUES_FOR_REPO_URL = "https://api.github.com/repos/%s/issues" % REPO
        AUTH = (GITHUB_USER, GITHUB_PASSWORD)
        arg = "?state=all"

        response = requests.get(ISSUES_FOR_REPO_URL + arg)
        file_csv = "%s-issues.csv" % (REPO.replace("/", "-"))
        file_csv_o = open(file_csv, "wb")
        out_csv = csv.writer(file_csv_o)
        out_csv.writerow(("id", "Title", "Tag", "State", "Open Date", "Close Date"))

        cls.write_issues(r, out_csv)

        # more pages? examine the 'link' header returned
        if "link" in response.headers:
            pages = dict(
                [
                    (rel[6:-1], url[url.index("<") + 1 : -1])
                    for url, rel in [
                        link.split(";") for link in response.headers["link"].split(",")
                    ]
                ]
            )

            while "last" in pages and "next" in pages:
                response = requests.get(pages["next"], auth=AUTH)
                cls.write_issues(response, out_csv)
                if pages["next"] == pages["last"]:
                    break
                pages = dict(
                    [
                        (rel[6:-1], url[url.index("<") + 1 : -1])
                        for url, rel in [
                            link.split(";")
                            for link in response.headers["link"].split(",")
                        ]
                    ]
                )

        file_csv_o.close()

        return "Success"
