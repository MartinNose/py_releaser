from __future__ import print_function
from github import Github
import sys
import re
from datetime import date, datetime
import random

comment = "<!-- Please write a release note here to describe the change you made when it is released to the users of TiDB. If your PR doesn't involve any change to TiDB(like test enhancements, RFC proposals...), you can write No release note. -->"
alias = []
tools = []
class ReleaseNote:
    def __init__(self, text, pr, link, repo_name):
        self.text = text
        self.pr = pr
        self.repo_name = repo_name
        self.labels = list(map(lambda x: x.name, pr.get_labels()))
        self.link = link

def parse(raw):
    if raw[0] in "-*":
        raw = raw[1:]
        return raw.replace("`", "").strip()
    elif "```release-note" in raw.split("\n")[0]:
        raw = re.split("```release-note|```", raw)[1].strip()
        return raw
    else:
        raise(RuntimeError("Failed to Parse"))

def to_pr(issue):
    try:
        return issue.as_pull_request()
    except:
        return None

def get_release_note(milestone : str , labels : list, config : dict, token):
    repos = config["repos"]
    g = Github(token)
    rl_list = []
    label_release_note_dir = {}
    label_release_note_dir["__unsorted"] = []
    for repo_name in repos:
        print(repo_name)
        try:
            repo = g.get_repo(repo_name)
        except:
            print(repo_name)
            continue

        # pulls = filter(lambda x: x.milestone != None and x.milestone.title == milestone, repo.get_pulls(state="all"))
        # pulls = repo.get_pulls(state="all")
        try:
            milestone_obj = list(filter(lambda x: x != None and x.title == milestone, repo.get_milestones()))[0]
        except:
            print(f"No milestone: {milestone} in repo {repo_name}" )
            continue
        
        pulls = list(filter(None, map(to_pr, repo.get_issues(milestone=milestone_obj, state="all"))))

        cnt = 0
        for pr in pulls:
            print(f"{cnt}/{len(pulls)}")
            cnt += 1
            if not (pr.milestone != None and pr.milestone.title == milestone):
                continue
            print(pr.html_url)

            try:
                raw = re.split("### Release note( <!-- bugfixes or new feature need a release note -->)*", pr.body)[-1].strip()
            except IndexError:
                print(pr.body, file=sys.stderr)
                exit()

            raw = re.sub("<!--.*-->", "", raw).strip()
            try:
                text = parse(raw)
            except RuntimeError:
                text = "```unparsed\r\n" + raw + "\r\n```\r\n"
            
            
                
            if "no release note" in text.lower() or "none" == text.lower():
                continue

            rl = ReleaseNote(text, pr, pr.html_url, repo_name)

            match = False
            for label in rl.labels:
                if label in labels:
                    if not label in label_release_note_dir:
                        label_release_note_dir[label] = [rl]
                    else:
                        label_release_note_dir[label].append(rl)
                    match = True
                    break
            if not match:
                label_release_note_dir["__unsorted"].append(rl)
    return label_release_note_dir


def list_release_note(milestone : str , labels : list, config : dict, token):
    repos = config["repos"]
    label_release_note_dir = get_release_note(milestone, labels, config, token)
    for label in label_release_note_dir:
        print(label)
        for rl in label_release_note_dir[label]:
            print("    - " + rl.text)
        print()

def push(dict, key, item):
    if key in dict:
        dict[key].append(item)
    else:
        dict[key] = [item]
    
def rename(name):
    if name in alias:
        return alias[name]
    else:
        return name


def get_body(lable_release_note_dir, version):
    paras = []
    paras.append(f"---\r\ntitle: TiDB {version} Release Notes\r\ncategory: Releases\r\n---\r\n\r\n")
    paras.append(f"# TiDB {version} Release Notes")
    paras.append(f'Release Date: {date.today().strftime("%B %d, %Y")}')
    paras.append(f'TiDB version: {version}')

    for label in lable_release_note_dir:
        notes = lable_release_note_dir[label]
        paras.append(f"## {rename(label).split('/')[-1]}")
        repo_dir = {}
        tools_dir = {}
        for note in notes:
            if note.repo_name in tools:
                if note.repo_name in tools_dir:
                    tools_dir[note.repo_name].append(note)
                else:
                    tools_dir[note.repo_name] = [note]
            else:
                push(repo_dir, note.repo_name, note)

        for repo_name in repo_dir:
            notes = repo_dir[repo_name]
            paras.append(f"+ {rename(repo_name)}")
            para = ""
            for note in notes:
                if "```unparsed" in note.text:
                    para += "    - ```release-note " + f'[#{note.link.split("/")[-1]}]({note.link})' + "\r\n"
                else:    
                    para += "    - " + note.text + f' [#{note.link.split("/")[-1]}]({note.link})' + "\r\n"
            paras.append(para)
        
        if len(tools_dir) == 0:
            continue
        paras.append(f"+ Tools")

        for repo in tools_dir:
            paras.append(f"    + {rename(repo)}")
            para = ""
            for note in tools_dir[repo]:
                if "```unparsed" in note.text:
                    para += "        - ```release-note " + f'[#{note.link.split("/")[-1]}]({note.link})' + "\r\n"
                else:    
                    para += "        - " + note.text + f' [#{note.link.split("/")[-1]}]({note.link})' + "\r\n"            
            paras.append(para)
        
    body = ""
    for para in paras:
        body += para + "\r\n" * 2

    return body

def create_pull_request(milestone : str, labels : list, config : dict, token):
    repos = config["repos"]
    global alias, tools
    alias = config["alias"]
    tools = config["tools"]
    g = Github(token)
    dev_repo = g.get_repo("ti-srebot/docs")
    target_repo = g.get_repo("PingCAP/docs")

    version = milestone.replace("v", "")
    # rl = get_release_note(milestone, labels, config, token)
    # body = get_body(rl, version)

    version += datetime.now().strftime("-%H-%M-%S")
    # create release note md file and commit to ti-srebot/docs branch: update-[milestone]
    file_name = f"releases/release-{version}.md"

    commit_msg = f'releases: add TiDB {version} release notes\r\n\r\n' \
                + f'* releases: add TiDB {version} release notes\r\n' \
                + f'* Update {file_name}'


    sb = dev_repo.get_branch("master")
    # master fetch upstream
    try:
        base = dev_repo.get_branch("master")
        head = target_repo.get_branch("master")

        merge_to_master = dev_repo.merge("master",
                            head.commit.sha, "merge from upstream master")
    except Exception as ex:
        print(ex)

    dev_repo.create_git_ref(ref='refs/heads/update-' + version, sha=sb.commit.sha)
    dev_repo.create_file(file_name, commit_msg, body, branch=f"update-{version}")
    print(version)
    


    # create pull request to pingcap/docs

    upstream_pullrequest = target_repo.create_pull(f"releases: add tidb {version} release notes", f"update tidb {milestone} release notes", 'master', 
          '{}:{}'.format('ti-srebot', f"update-{version}"), True)


