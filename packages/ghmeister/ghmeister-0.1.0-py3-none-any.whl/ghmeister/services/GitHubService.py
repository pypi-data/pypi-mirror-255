from github import Auth, Github

from ghmeister.auth import get_github_token

github = None


def get_github():
    global github
    if not github:
        token = get_github_token()
        auth = Auth.Token(token['access_token'])
        github = Github(auth=auth)
    return github
