import re
import subprocess
from urllib.parse import urlparse

repoMap = {}


def clone(repo_location, branch, folder, extra_token=None):
    """
    Clone a git repo to the folder
    When extra_token isn't None, add it to the command

    replacing
    https://apidrop.visualstudio.com/Content%20CI/_git/ReferenceAutomation?path=/Python/GetPackageCode.ps1&line=50&lineEnd=90&lineStartColumn=1&lineEndColumn=2&lineStyle=plain&_a=contents
    """

    print("<CI INFO>: Cloning repo: {}...".format(repo_location))

    global repoMap

    if not test_url(repo_location, extra_token):
        raise ValueError(
            "Git repo address {} is not a valid URL.".format(repo_location)
        )
    else:
        # Remove http(s):// from url to record. Further avoid dup-clone.
        pureURL = re.sub("^\s*https?://", "", repo_location)

        if pureURL not in repoMap:
            branch = convertBranch(repo_location, branch, extra_token)

            check_params = ["git", "ls-remote", "--heads", repo_location, branch]
            if extra_token:
                check_params[1:1] = [
                    "-c",
                    "http.extraHeader=Authorization: Basic {}".format(extra_token),
                ]

            check_br = subprocess.check_output(check_params)

            # if remote branch exists, clone it
            if check_br:
                clone_params = [
                    "git",
                    "clone",
                    repo_location,
                    folder,
                    "--shallow-submodules",
                    "--branch",
                    branch,
                ]
                if extra_token:
                    clone_params[1:1] = [
                        "-c",
                        "http.extraHeader=Authorization: Basic {}".format(
                            extra_token
                        ),
                    ]
                subprocess.run(clone_params, check=True)
                repoMap[pureURL] = folder
                print(
                    "<CI INFO>: Repo {} successfully cloned in {}...".format(
                        repo_location, repoMap[pureURL]
                    )
                )
            else:
                raise ValueError(
                    "Branch {} doesn't exist in repo {}.".format(branch, repo_location)
                )
        else:
            print("<CI INFO>: Repo already cloned in {}...".format(repoMap[pureURL]))

        return repoMap[pureURL]


def test_url(url, extraHeader):
    """
    Test if the url is a valid git repo url
    """
    params = ["git", "ls-remote", url]
    if extraHeader:
        print("Using extra header to test git repo url.")
        params[1:1] = [
            "-c",
            "http.extraHeader=Authorization: Basic {}".format(extraHeader),
        ]
    try:
        subprocess.check_output(params)
        return True
    except:
        return False


def convertBranch(repo_url, branch, extraHeader):
    result = branch
    if not branch:
        print(
            "Using empty branch of {}, going to use master branch instead.".format(
                repo_url
            )
        )
        result = "master"
    if result == "master":
        check_params = ["git", "ls-remote", "--heads", repo_url, "refs/heads/main"]
        if extraHeader:
            check_params[1:1] = [
                "-c",
                "http.extraHeader=Authorization: Basic {}".format(extraHeader),
            ]

        checkBr = subprocess.check_output(check_params)
        if checkBr:
            print(
                "Using master branch of {}, going to use main branch instead.".format(
                    repo_url
                )
            )
            result = "main"
    return result


def checkout(folder, branch):
    """
    Checkout one folder to a given branch

    Replacing
    https://apidrop.visualstudio.com/Content%20CI/_git/ReferenceAutomation?path=/Python/PyCommon.ps1&line=707&lineEnd=763&lineStartColumn=1&lineEndColumn=2&lineStyle=plain&_a=contents
    """

    remote = "origin"

    if ":" in branch:
        remote, branch = branch.split(":")

    branches = (
        subprocess.check_output(["git", "-C", folder, "branch", "--list"])
        .decode()
        .strip()
    )

    if "* {}".format(branch) not in branches:
        # branch is not exactly current branch
        if branch not in branches:
            subprocess.run(
                [
                    "git",
                    "-C",
                    folder,
                    "fetch",
                    "--quiet",
                    remote,
                    "{}:{}".format(branch, branch),
                ]
            )

        subprocess.run(["git", "-C", folder, "checkout", "--quiet", branch])

        print("<CI INFO>: Switched to branch {}.".format(branch))


def commit_and_push(repo_location, folder, extra_token=None):
    """
    Commit in the folder and push changes to target repo, maybe phase 2

    Replacing
    https://apidrop.visualstudio.com/Content%20CI/_git/ReferenceAutomation?path=/common/CI.push.ps1

    """

    pass


def pull(repo_location, folder, extra_token=None):
    """
    Pull in the folder document repo, maybe phase 2

    Replacing
    https://apidrop.visualstudio.com/Content%20CI/_git/ReferenceAutomation?path=/common/CI.pull.ps1
    """

    pass


def status(folder):
    """
    Print git status of this folder, a helper method for our unit test
    """
    try:
        status = subprocess.check_output(['git', '-C', folder, 'status'], stderr=subprocess.DEVNULL).decode()
        return len(status) > 0
    except subprocess.CalledProcessError:
        return False
