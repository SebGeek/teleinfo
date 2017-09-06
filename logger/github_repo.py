#!/usr/bin/python
# -*- coding: utf-8 -*-
from github import Github

g = Github("SebGeek", "MonTele12")

for repo in g.get_user().get_repos():
    if repo.name == "teleinfo":
        print repo
        fd = open("../log/log.csv.2016-11-21", "r")
        repo.create_file("/log/new_file2.txt", "add log", fd.read())

if __name__ == "__main__":
    pass
