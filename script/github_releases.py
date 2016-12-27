#!/usr/bin/env python

from sys import exit, stderr
from os import getenv, path
from re import match, MULTILINE
from requests import get, patch


LOG_DELIMITER = "## streamlink "
LOG_RE_HEADER = r"^(\d+\.\d+\.\d+)\s\(.+\)(?:\n|\r\n?)+([\s\S]+)$"


def checkEnvVar(v):
    if not getenv(v):
        raise AssertionError("Missing env var {0}\n".format(v))

def getChangelog(s):
    m = match(LOG_RE_HEADER, s, MULTILINE)
    if not m:
        raise AssertionError("Changelog format error")
    return (m.group(1), m.group(2))


def githubAPI(method, url, **kwargs):
    url = "https://api.github.com/repos/{0}/releases/{1}".format(getenv("TRAVIS_REPO_SLUG"), url)
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": getenv("TRAVIS_REPO_SLUG"),
        "Authorization": "token {0}".format(getenv("RELEASES_API_KEY"))
    }
    return (get if method != "PATCH" else patch)(url, headers=headers, **kwargs)


try:
    # Make sure that all required env vars are set
    [checkEnvVar(v) for v in ["TRAVIS_REPO_SLUG", "TRAVIS_TAG", "RELEASES_API_KEY"]]

    # Parse changelog file
    file = path.abspath("{0}/{1}".format(path.dirname(__file__), "../CHANGELOG.md"))
    contents = open(file).read()
    if not contents:
        raise AssertionError("Missing changelog file")
    changelogs = dict([getChangelog(x) for x in contents.split(LOG_DELIMITER)[1:]])
    if not getenv("TRAVIS_TAG") in changelogs:
        raise AssertionError("Missing changelog for current release")

    # Get release ID
    res = githubAPI("GET", "tags/{0}".format(getenv("TRAVIS_TAG")))
    data = res.json()
    if not "id" in data:
        raise AssertionError("Missing id from Github API response")

    # Update release name and body
    payload = {
        "name": "Streamlink {0}".format(getenv("TRAVIS_TAG")),
        "body": changelogs[getenv("TRAVIS_TAG")]
    }
    githubAPI("PATCH", data["id"], json=payload)


    print("Github release {0} has been successfully updated".format(getenv("TRAVIS_TAG")))
    exit(0)

except Exception as e:
    stderr.write("{0}\n".format(str(e)))
    exit(1)
