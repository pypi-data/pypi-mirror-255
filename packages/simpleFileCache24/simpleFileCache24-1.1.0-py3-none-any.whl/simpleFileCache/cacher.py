
import datetime
from functools import cache
import os
import shutil
from simpleFileCache.index import CacheIndexDict, CacheIndexEntry, newEntry
import typing
from simpleFileCache.utils.hashing import hash_bytes, hash_file, verify_file_hash
import requests
from simpleFileCache.utils.git import (
    git_last_commit_sha,
    download_github_raw_content,
    meta_repo, extract_github_url
)
from simpleFileCache.logger import logger

class Cacher:
    def __init__(
        self, 
        path : str,
        cacheDictStrategy : typing.Literal["moduleFile", "keyring"] = "keyring",
        raiseNonIndexedFiles : bool = False
    ):
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        self.__path = path
        self.__path_lastm = self.__pathModifiedDate
        
        self.__cacheFolder = os.path.join(self.__path, "cache")
        
        
        os.makedirs(self.__cacheFolder, exist_ok=True)
        self.__storeDict = CacheIndexDict(os.path.join(path, "index.json"), privateKey=cacheDictStrategy)
        if "cache" not in self.__storeDict:
            self.__storeDict["cache"] = {}
        self.__cacheDict : CacheIndexDict = self.__storeDict["cache"]
        if "alias" not in self.__storeDict:
            self.__storeDict["alias"] = {}
        self.__aliasDict : CacheIndexDict = self.__storeDict["alias"]
        
        if len(self.cacheFiles) > 0 and len(self.__cacheDict) == 0:
            if not raiseNonIndexedFiles:
                print(f"index at {self.__path} contains non-indexed files")
            else:
                raise RuntimeError(f"index at {self.__path} contains non-indexed files")
    
    @property
    def __pathModifiedDate(self):
        return os.path.getmtime(self.__path)
    
    def resetCache(self, force : bool = False):
        if self.__path_lastm != self.__pathModifiedDate or force:
            self.__path_lastm = self.__pathModifiedDate
            self.cacheFilePresent.cache_clear()
            self.cacheFileIntegrityCheck.cache_clear()
            self.cacheFileFetch.cache_clear()
            self.updateNeeded.cache_clear()
            
    @cache
    def cacheFilePresent(self, path : str):
        
        entry :typing.Union[CacheIndexEntry, dict] = self.__cacheDict.get(path, None)
        if entry is None:
            return False
        
        checksum = entry.get("checksum")
        return os.path.exists(os.path.join(self.__cacheFolder, checksum))
    
    @cache
    def cacheFileIntegrityCheck(self, path : str):
        entry :typing.Union[CacheIndexEntry, dict] = self.__cacheDict.get(path, None)
        
        checksum = entry.get("checksum")
        filebytes = self.cacheFileFetch(path)
        return verify_file_hash(filebytes, checksum)
        
    @cache
    def cacheFileFetch(self, path : str):
        logger.debug(f"Fetching cache file {path}")

        entry :typing.Union[CacheIndexEntry, dict] = self.__cacheDict.get(path)
        
        checksum : str = entry.get("checksum")
        
        with open(os.path.join(self.__cacheFolder, checksum), "rb") as f:
            return f.read()
    
    @cache
    def updateNeeded(self, path : str, interval : int):
        entry : typing.Union[CacheIndexEntry, dict] = self.__cacheDict.get(path, None)
        if entry is None:
            return True

        if not self.cacheFilePresent(path):
            return True
        
        # file exists
        if not self.cacheFileIntegrityCheck(path):
            return True
        
        updateableInterval = entry.get("updatableInterval", None)
        
        if updateableInterval != interval and interval is not None:
            updateableInterval = interval
        
        if updateableInterval is None:
            return False
        
        lastPulled = entry.get("lastPulled", None)
        if lastPulled is None:
            return True
        
        time_since_last_pull = datetime.datetime.now() - datetime.datetime.fromisoformat(lastPulled)
        return time_since_last_pull.total_seconds() > updateableInterval
        
    @property
    def cacheFiles(self):
        return os.listdir(self.__cacheFolder)

    def item_gitraw(self, path : str, force : bool = False, updatableInterval : int = 24*3600):
        self.resetCache()
        
        if not force and not self.updateNeeded(path, updatableInterval):
            logger.debug(f"{path} is up to date")
            return self.cacheFileFetch(path)
        
        
        currentSha = git_last_commit_sha(meta_repo(path), extract_github_url(path)["filepath"])
        entry = self.__cacheDict.get(path, None)
        if entry is not None:
            entry : typing.Union[CacheIndexEntry, dict]
            sha = entry.get("lastCommitted", None)
            if sha is not None and currentSha == sha:
                return self.cacheFileFetch(path)
                
        dbytes = download_github_raw_content(path)
        checksum = hash_bytes(dbytes)
        with open(os.path.join(self.__cacheFolder, checksum), "wb") as f:
            f.write(dbytes)
        
        
        newEntry(
            self.__storeDict,
            path,
            checksum=checksum,
            type="gitraw",
            lastCommitted=currentSha,
            updatableInterval=updatableInterval,
            lastPulled=datetime.datetime.now().isoformat()
        )

    def item_local(self, path : str, force : bool = False, updatableInterval : int = 24*3600):
        self.resetCache()
        if not os.path.exists(path):
            raise FileNotFoundError(f"file at {path} does not exist")
        
        originalPath = path
        path = os.path.abspath(path)
        
        if originalPath != path and originalPath in self.__aliasDict and self.__aliasDict[originalPath] != path:
            raise FileExistsError(
                f"Theres already a file taking this key {self.__aliasDict[originalPath]}"
            )
        
        if not force and not self.updateNeeded(path, updatableInterval):
            logger.debug(f"{path} is up to date")
            return self.cacheFileFetch(path)

        checksum = hash_file(path)
        shutil.copyfile(path, os.path.join(self.__cacheFolder, checksum))
        with self.__storeDict.saveLock():
            newEntry(
                self.__cacheDict,
                path,
                checksum=checksum,
                type="local",
                updatableInterval=updatableInterval,
                lastPulled=datetime.datetime.now().isoformat()
            )
            
            if originalPath != path:
                self.__aliasDict[originalPath] = path
    
    def item_url(self, path : str, force : bool = False, updatableInterval : int = 24*3600):
        self.resetCache()
        if not force and not self.updateNeeded(path, updatableInterval):
            logger.debug(f"{path} is up to date")
            return self.cacheFileFetch(path)
        
        res = requests.get(path)
        if res.status_code != 200:
            raise RuntimeError(f"failed to fetch {path}")
        
        checksum = hash_bytes(res.content)
        newEntry(
            self.__cacheDict,
            path,
            checksum=checksum,
            type="url",
            updatableInterval=updatableInterval,
            lastPulled=datetime.datetime.now().isoformat()
        )
        with open(os.path.join(self.__cacheFolder, checksum), "wb") as f:
            f.write(res.content)

        return self.cacheFileFetch(path)
    
    def item_gitraw_permanent(self, path : str):
        return self.item_gitraw(path, updatableInterval=None)
    
    def item_local_permanent(self, path : str):
        return self.item_local(path, updatableInterval=None)
    
    def item_url_permanent(self, path : str):
        return self.item_url(path, updatableInterval=None)
    
    def item_direct(self, path : str):
        self.resetCache()
        if not os.path.exists(path):
            raise FileNotFoundError(f"file at {path} does not exist")
        
        path = os.path.abspath(path)
        
        checksum = hash_file(path)
        newEntry(
            self.__cacheDict,
            path,
            checksum=checksum,
            type="direct",
            lastPulled=datetime.datetime.now().isoformat()
        )
        shutil.copyfile(path, os.path.join(self.__cacheFolder, checksum))
        
    def fileCopyTo(self, path : str, dst : str):
        checksum = self.fileGetChecksum(path)
        try:
            shutil.copyfile(os.path.join(self.__cacheFolder, checksum), dst)
        except FileExistsError:
            pass
    
        
    def fileGetChecksum(self, path : str) -> str:
        if path not in self.__cacheDict:
            if path in self.__aliasDict:
                path = self.__aliasDict[path]
            else:
                raise FileNotFoundError(f"file at {path} does not exist in cache")
        
        entry : CacheIndexEntry = self.__cacheDict[path]
        
        return entry.get("checksum")
        
    def fileGet(self, path : str):
        checksum : str = self.fileGetChecksum(path)
        
        with open(os.path.join(self.__cacheFolder, checksum), "rb") as f:
            return f.read()
    
    def setAlias(self, path : str, *alias : str, ignoreErrors : bool = False):
        try:
            with self.__storeDict.saveLock():
                for a in alias:
                    if a in self.__aliasDict:
                        raise FileExistsError(f"Theres already a file taking this key {self.__aliasDict[a]}")
                
                    self.__aliasDict[a] = path
        except FileExistsError:
            if not ignoreErrors:
                raise
    
    def pruneCache(self):
        existingChecksums = set()
        for path in self.__cacheDict:
            existingChecksums.add(self.__cacheDict[path].get("checksum"))
        
        for checksum in os.listdir(self.__cacheFolder):
            if checksum not in existingChecksums:
                os.remove(os.path.join(self.__cacheFolder, checksum))
