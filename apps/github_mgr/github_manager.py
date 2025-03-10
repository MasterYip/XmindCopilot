'''
Author: Raymon Yip 2205929492@qq.com
Date: 2025-03-09 11:57:27
Description: file content
FilePath: /XmindCopilot/apps/github_mgr/github_manager.py
LastEditTime: 2025-03-10 11:26:57
LastEditors: Raymon Yip
'''
import subprocess
import requests
import json
import os
import XmindCopilot
from XmindCopilot.search import topic_search_by_title, topic_search_by_hyperlink
from XmindCopilot.topic_cluster import topic_cluster
from user_cfg import user_name, token

# Directory Management
try:
    # Run in Terminal
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
except:
    # Run in ipykernel & interactive
    ROOT_DIR = os.getcwd()


def get_github_stars(username, token=None):
    """
    Retrieve a list of starred repositories for a GitHub user

    Parameters:
    username (str): GitHub username to query
    token (str, optional): GitHub personal access token for authentication

    Returns:
    list: Repository full names in format 'owner/repo'

    Example:
    >>> get_github_stars('octocat')
    ['torvalds/linux', 'github/docs']
    """
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if token:
        headers['Authorization'] = f'token {token}'

    url = f"https://api.github.com/users/{username}/starred"

    star_list = []
    page_cnt = 0
    while url:
        try:
            print(f"Requesting page {page_cnt} of starred repositories...")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            star_list.extend(data)
            page_cnt += 1

            # Handle pagination
            if 'next' in response.links:
                url = response.links['next']['url']
            else:
                url = None

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"API request failed: {str(e)}") from e

    return star_list


# JSON fields
#   assignableUsers, codeOfConduct, contactLinks, createdAt, defaultBranchRef,
#   deleteBranchOnMerge, description, diskUsage, forkCount, fundingLinks,
#   hasDiscussionsEnabled, hasIssuesEnabled, hasProjectsEnabled, hasWikiEnabled,
#   homepageUrl, id, isArchived, isBlankIssuesEnabled, isEmpty, isFork,
#   isInOrganization, isMirror, isPrivate, isSecurityPolicyEnabled, isTemplate,
#   isUserConfigurationRepository, issueTemplates, issues, labels, languages,
#   latestRelease, licenseInfo, mentionableUsers, mergeCommitAllowed, milestones,
#   mirrorUrl, name, nameWithOwner, openGraphImageUrl, owner, parent,
#   primaryLanguage, projects, projectsV2, pullRequestTemplates, pullRequests,
#   pushedAt, rebaseMergeAllowed, repositoryTopics, securityPolicyUrl,
#   squashMergeAllowed, sshUrl, stargazerCount, templateRepository, updatedAt, url,
#   usesCustomOpenGraphImage, viewerCanAdminister, viewerDefaultCommitEmail,
#   viewerDefaultMergeMethod, viewerHasStarred, viewerPermission,
#   viewerPossibleCommitEmails, viewerSubscription, visibility, watchers

DEFAULT_FIELDS = [
    'name', 'owner', 'description',
    'isPrivate', 'isFork', 'isTemplate', 'isArchived',
    'stargazerCount', 'forkCount', 'watchers',
    'url', 'homepageUrl', 'sshUrl',
    # 'visibility', 'viewerHasStarred',
    # 'createdAt', 'updatedAt',
]


def get_repo_str():
    limit = 1000
    cmd = f'gh repo list -L {limit} --json ' + ','.join(DEFAULT_FIELDS)
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')


def get_repo_list():
    repo_list = get_repo_str()
    return json.loads(repo_list)


class RepoManager(object):
    def __init__(self, xmind_dir, user_name, token=None):
        self.user_name = user_name
        self.token = token
        self.load_xmind(xmind_dir)
        
    def load_xmind(self, xmind_dir):
        self.workbook = XmindCopilot.load(xmind_dir)
        self.repo_node = topic_search_by_title(self.workbook.getSheets()[2].getRootTopic(), "Repos", 1)
        self.star_node = topic_search_by_title(self.workbook.getSheets()[2].getRootTopic(), "Stars", 1)

    def save_repo_list(self, filename='repo_list.json'):
        with open(os.path.join(ROOT_DIR, filename), 'w') as f:
            f.write(json.dumps(self.repo_list, indent=4))

    def save_star_list(self, filename='star_list.json'):
        with open(os.path.join(ROOT_DIR, filename), 'w') as f:
            f.write(json.dumps(self.star_list, indent=4))

    def update_repo_node(self):
        self.repo_list = get_repo_list()
        if not topic_search_by_title(self.repo_node, "New", 1):
            self.repo_node.addSubTopicbyTitle("New")
        new_node = topic_search_by_title(self.repo_node, "New", 1)
        for repo in self.repo_list:
            # ●: Public Repo, ○: Private Repo, 
            # ■: Archived Public Repo, □: Archived Private Repo, ▲: Forked Repo
            prefix = ""
            if not repo['isPrivate'] and not repo['isArchived']:
                prefix = "●"
            elif repo['isPrivate'] and not repo['isArchived']:
                prefix = "○"
            elif not repo['isPrivate'] and repo['isArchived']:
                prefix = "■"
            elif repo['isPrivate'] and repo['isArchived']:
                prefix = "□"
            if repo['isFork']:
                prefix = "▲"

            title = prefix + " " + repo['name'] + "\n" + \
                "★" + str(repo['stargazerCount']) + "|" + \
                "F" + str(repo['forkCount']) + "|" + \
                "W" + str(repo['watchers']['totalCount'])
            url = repo['url']
            repo_node = topic_search_by_hyperlink(self.repo_node, url, -1)
            if not repo_node:
                repo_node = new_node.addSubTopicbyTitle(title)
                repo_node.setHyperlink(url)
            elif repo_node.getTitle() != title:
                repo_node.setTitle(title)
        if len(new_node.getSubTopics()) == 0:
            new_node.removeTopic()
    
    def update_star_node(self, arrange_by_owner=True, cluster=True):
        self.star_list = get_github_stars(self.user_name, self.token)
        if not topic_search_by_title(self.star_node, "New", 1):
            self.star_node.addSubTopicbyTitle("New")
        new_node = topic_search_by_title(self.star_node, "New", 1)
        for star in self.star_list:
            title = star['full_name']
            url = star['html_url']
            owner_name = star['owner']['login']
            if not topic_search_by_hyperlink(self.star_node, url, -1):
                if arrange_by_owner:
                    owner_node = topic_search_by_title(new_node, owner_name, 1)
                    if not owner_node:
                        owner_node = new_node.addSubTopicbyTitle(owner_name)
                        owner_node.setFolded()
                    star_node = owner_node.addSubTopicbyTitle(title)
                    star_node.setHyperlink(url)
                else:
                    star_node = new_node.addSubTopicbyTitle(title)
                    star_node.setHyperlink(url)
        if cluster:
            topic_cluster(new_node, recursive=False)
        
    def save_xmind(self):
        XmindCopilot.save(self.workbook)

if __name__ == '__main__':
    xmind_dir = "apps/temp.xmind8"
    repo_manager = RepoManager(xmind_dir, user_name, token)
    # repo_manager.update_repo_node()
    repo_manager.update_star_node(arrange_by_owner=False)
    # repo_manager.save_repo_list()
    repo_manager.save_xmind()
