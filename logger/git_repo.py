#!/usr/bin/python
# -*- coding: utf-8 -*-

from git import Repo

# Need to put SSH key in Github in order to avoid username/password connection
#
# Generate a SSH keys pair on raspberry pi:
# cd ~
# ssh-keygen -t rsa
#
# In Web GitHub repository, go to settings and click 'add SSH key'.
# Copy the contents of ~/.ssh/id_rsa.pub into the field labeled 'Key'.
#
# tell on raspberry to use SH connection:
# git remote set-url origin git@github.com:SebGeek/teleinfo.git

repo_dir = '~/partage/teleinfo'
repo = Repo(repo_dir)
file_list = ['log/log.csv.2017-09-06', ]
commit_message = 'Add log'
repo.index.add(file_list)
repo.index.commit(commit_message)
origin = repo.remote('origin')
origin.push()
