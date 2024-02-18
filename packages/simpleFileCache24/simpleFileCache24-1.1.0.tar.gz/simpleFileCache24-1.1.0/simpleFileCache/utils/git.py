from datetime import datetime
from functools import cache
from typing import TypedDict
import requests
from sioDict.etc import getDeep

baseurl= "https://raw.githubusercontent.com/{url}"

class GitMeta(TypedDict):
    id : str
    name : str
    branch : str
    filepath :str

@cache
def extract_github_url(url : str):
    urlsplitted = url.split("/")
    return GitMeta(
        id = urlsplitted[0],
        name = urlsplitted[1],
        branch = urlsplitted[2],
        filepath = "/".join(urlsplitted[3:]),
    )
    
@cache
def meta_repo(url : str):
    meta = extract_github_url(url)
    return f"{meta['id']}/{meta['name']}"

@cache
def meta_filename(url : str):
    meta = extract_github_url(url)
    filepath = meta["filepath"]
    filepath_splitted = filepath.split("/")
    return filepath_splitted[-1]

@cache
def meta_folder(url : str):
    meta = extract_github_url(url)
    filepath = meta["filepath"]
    if "/" not in filepath:
        return ""
    filepath_splitted = filepath.split("/")    
    return "/".join(filepath_splitted[:-1])

def download_github_raw_content(url : str):
    """
    Downloads the raw content from the given GitHub URL.

    Args:
        url (str): The URL of the content to be downloaded.

    Returns:
        bytes: The raw content downloaded from the specified URL.
    """
    url = baseurl.format(url=url)
    res = requests.get(url)
    # if 404
    if res.status_code == 404:
        raise RuntimeError("File not found on github")
    
    return res.content

last_commit_api_url = "https://api.github.com/repos/{id}/commits?path={filename}&limit=1"

def git_last_commit_date(id, filename):
    """
    A function to retrieve the last commit date for a given id and filename using the last_commit_api_url.
    
    Args:
        id: The identifier for the commit.
        filename: The name of the file.
        
    Returns:
        The date of the last commit as a datetime object, or None if there was an error.
    """
    r = requests.get(last_commit_api_url.format(id=id, filename=filename))
    try:
        rjson = r.json()
    except Exception:
        return None

    datestr = getDeep(rjson, 0, "commit", "committer", "date")
    if datestr is None:
        return None
    
    dateobj = datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%SZ")

    return dateobj

def git_last_commit_sha(id, filename) -> str:
    """
    Get the last commit SHA for the given ID and filename.

    Args:
        id (any): The ID for the commit.
        filename (str): The name of the file.

    Returns:
        The last commit SHA if successful, otherwise None.
    """
    r = requests.get(last_commit_api_url.format(id=id, filename=filename))
    try:
        rjson = r.json()
    except Exception:
        return None

    return getDeep(rjson, 0, "sha")