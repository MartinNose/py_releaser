from github import Github

def list(milestone : str , labels : list, repos : list, token):
    g = Github(token)

    for repo_name in repos:
        repo = g.get_repo(repo_name)
        pulls = repo.get_pulls()
        for pr in filter(lambda x: x.milestone != None and x.milestone.title == milestone, pulls):
            print("*"*100)
            print(pr.body.split("### Release note <!-- bugfixes or new feature need a release note -->")[1])



    pass


def pull(milestone : str, labels : list, repos : list, token):
    print(milestone, labels, repos)
    pass


