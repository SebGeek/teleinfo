#!/usr/bin/python
# -*- coding: utf-8 -*-
from github import Github

if __name__ == "__main__":
    g = Github("SebGeek", "MonTele12")

    repo = g.get_user().get_repo("teleinfo")
    fd = open("../log/log.csv.2016-11-21", "r")
    repo.create_file("/log/new_file2.txt", "add log", fd.read())
