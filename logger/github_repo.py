#!/usr/bin/python
# -*- coding: utf-8 -*-
from github import Github

g = Github("SebGeek", "MonTele12")

for repo in g.get_user().get_repos():
    if repo.name == "teleinfo":
        print repo

if __name__ == "__main__":
    pass
