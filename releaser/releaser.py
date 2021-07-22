#!python
import sys
import json

import collect
from github import Github
usage = "usage: python releaser.py list|pull [-m milestone] [-c config_file] [-L label1,label2,...]"
class PR:
    def __init__(self, repo, number, author, title, content, link):
        self.repo = repo
        self.number = number
        self.author = author
        self.title = title
        self.content = content 
        self.link = "github.com/" + repo + "/pull/" + number


def main():
    args = sys.argv[1:]
    if len(args) == 0:
        print(usage) # TODO help
        return 1

    milestone = None
    labels = None
    config_path = "../config.json"

    if not args[0] in ["list", "pull"]:
        print("Please specify the functionality:\n\n",
            "\tlist : Preview the the generated pr and print the log\n",
            "\tpull : Generate the release note and open a pr in pingcap/docs\n\n",
            usage)
        return 1

    i = 1
    while i < len(args):
        if args[i] == "-m":
            milestone = args[i + 1]
            i += 1
        elif args[i] == "-c":
            config_path = args[i + 1]
            i += 1
        elif args[i] == "-L":
            labels = args[i + 1].split(',')
            i += 1
        i += 1
    config = json.load(open(config_path))
    token = config["token"]
    if "-L" not in args:
        labels = config["labels"]
        if len(labels) == 0:
            labels = None

    if milestone == None or labels == None:
        print(usage)

    if args[0] == "list":
        collect.list_release_note(milestone, labels, config["repos"], token)
    elif args[0] == "pull":
        collect.create_pull_request(milestone, labels, config["repos"], token)

if __name__ == "__main__":
    main()