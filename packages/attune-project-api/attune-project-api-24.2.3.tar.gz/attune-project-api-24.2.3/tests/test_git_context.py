import os
import shutil
import tempfile
import unittest
from pathlib import Path

import pygit2
from pygit2._pygit2 import GitError

from attune_project_api import ParameterTuple
from attune_project_api.StorageTuple import ItemStorageGroupEnum
from attune_project_api._contexts.GitObjectStorageContext import (
    GitObjectStorageContext,
)
from attune_project_api.context_project_info import ContextProjectInfo
from attune_project_api.key_util import makeStorageKey
from tests.utils import countCommitsOnBranch

WORKING_BRANCH = "__working__"

MASTER = "master"


class ContextGitRepoTest(unittest.TestCase):
    TEST_REPO = "repo"
    REMOTE_REPO = "remote"

    author = pygit2.Signature("ServerTribe Attune", "attune@servertribe.com")

    def setUp(self) -> None:
        self.tempdir = Path(tempfile.gettempdir())
        self.repopath = self.tempdir / ContextGitRepoTest.TEST_REPO
        self.remotePath = self.tempdir / ContextGitRepoTest.REMOTE_REPO

    def tearDown(self) -> None:
        if os.path.exists(self.repopath):
            shutil.rmtree(self.repopath)
        if os.path.exists(self.remotePath):
            shutil.rmtree(self.remotePath)

    def _createSimpleProject(self, path: Path) -> GitObjectStorageContext:
        context = GitObjectStorageContext(
            path,
            ContextProjectInfo(
                id=1,
                key="test",
                name="test",
            ),
        )

        param = ParameterTuple(
            key="test0",
            name="test0",
            type=ParameterTuple.TEXT,
            comment="# Heading for 0",
        )
        context.addItem(param)
        context.commit("Add test0 parameter")

        param = ParameterTuple(
            key="test1",
            name="test1",
            type=ParameterTuple.TEXT,
            comment="# Heading for 1",
        )
        context.addItem(param)
        context.commit("Add test1 parameter")

        context.squashAndMergeWorking("Add two parameters")

        return context

    def testProjectLoad(self):
        # Should not raise
        GitObjectStorageContext(
            self.repopath,
            ContextProjectInfo(
                id=1,
                key=ContextGitRepoTest.TEST_REPO,
                name=ContextGitRepoTest.TEST_REPO,
            ),
        )

    def testProjectRename(self):
        context = GitObjectStorageContext(
            self.repopath,
            ContextProjectInfo(
                id=1,
                key=ContextGitRepoTest.TEST_REPO,
                name=ContextGitRepoTest.TEST_REPO,
            ),
        )
        repo = pygit2.Repository(self.repopath / "git_storage")

        metadata = context.metadata
        self.assertEqual(metadata.name, ContextGitRepoTest.TEST_REPO)
        commitCount = countCommitsOnBranch(repo, repo.branches["master"])

        newName = "Test2"
        context.renameProject(newName)
        metadata = context.metadata
        self.assertEqual(metadata.name, newName)
        self.assertEqual(metadata.key, makeStorageKey(newName))

        # The rename-operation should have created a new commit on the `master`
        # branch
        self.assertEqual(
            commitCount + 1, countCommitsOnBranch(repo, repo.branches["master"])
        )

        # The user should not be able to rename when a working branch is present
        param = ParameterTuple(key="test", name="Test")
        context.addItem(param)
        context.commit("Add a param")

        newName = "Test3"
        with self.assertRaises(RuntimeError):
            context.renameProject(newName)

        context.squashAndMergeWorking("Add a param")
        # It should be possible to rename after the change are committed
        context.renameProject(ContextGitRepoTest.TEST_REPO)

        # Reload the project context
        context = GitObjectStorageContext(
            self.tempdir / makeStorageKey(newName),
            ContextProjectInfo(
                id=1,
                key=makeStorageKey(newName),
                name=newName,
            ),
        )
        metadata = context.metadata
        self.assertEqual(metadata.name, newName)
        self.assertEqual(metadata.key, makeStorageKey(newName))

    def testBranching(self):
        context = GitObjectStorageContext(
            self.repopath,
            ContextProjectInfo(
                id=1,
                key=ContextGitRepoTest.TEST_REPO,
                name=ContextGitRepoTest.TEST_REPO,
            ),
        )
        repo = pygit2.Repository(self.repopath / "git_storage")

        self.assertTrue(MASTER in repo.branches)
        self.assertFalse(WORKING_BRANCH in repo.branches)

        master: pygit2.Branch = repo.branches[MASTER]
        self.assertEqual(1, countCommitsOnBranch(repo, master))

        param = ParameterTuple(
            key="test0", name="test0", type=ParameterTuple.TEXT
        )
        context.addItem(param)
        context.commit("Add test0 parameter")

        self.assertTrue(WORKING_BRANCH in repo.branches)
        working: pygit2.Branch = repo.branches[WORKING_BRANCH]
        self.assertEqual(2, countCommitsOnBranch(repo, working))

        # Commit and add another item
        param = ParameterTuple(
            key="test1", name="test1", type=ParameterTuple.TEXT
        )
        context.addItem(param)
        context.commit("Add test1 parameter")
        # References to branch need to be fetched every time something
        # changes on the branch
        working: pygit2.Branch = repo.branches[WORKING_BRANCH]
        self.assertEqual(3, countCommitsOnBranch(repo, working))

        # Squash the __working__ branch and merge onto master
        context.squashAndMergeWorking("Add two parameters")
        master: pygit2.Branch = repo.branches[MASTER]
        self.assertEqual(2, countCommitsOnBranch(repo, master))

        self.assertFalse(WORKING_BRANCH in repo.branches)

    def testProjectClone(self):
        self._createSimpleProject(self.remotePath)
        remoteRepo = pygit2.Repository(self.remotePath / "git_storage")

        GitObjectStorageContext.cloneGitRepo(
            self.repopath / "git_storage", str(self.remotePath / "git_storage")
        )
        localRepo = pygit2.Repository(self.repopath / "git_storage")

        self.assertEqual(remoteRepo.head.target, localRepo.head.target)

    def testProjectPushWhenLocalModified(self):
        remoteContext: GitObjectStorageContext = self._createSimpleProject(
            self.remotePath
        )
        remoteRepo: pygit2.Repository = pygit2.Repository(
            self.remotePath / "git_storage"
        )

        # This clone will set the remote of the Git repo to the remote of the
        # Attune project
        GitObjectStorageContext.cloneGitRepo(
            self.repopath / "git_storage",
            str(self.remotePath / "git_storage"),
        )
        localContext = GitObjectStorageContext(
            self.repopath,
            ContextProjectInfo(
                id=1,
                key=ContextGitRepoTest.TEST_REPO,
                name=ContextGitRepoTest.TEST_REPO,
            ),
        )
        localRepo: pygit2.Repository = pygit2.Repository(
            self.repopath / "git_storage"
        )

        # Push when there are no remote changes
        param: ParameterTuple = ParameterTuple(
            key="test0",
            name="test0",
            type=ParameterTuple.TEXT,
            comment="# Heading for test0",
        )
        localContext.addItem(param)
        localContext.commit("Modify comment for test0 parameter")
        localContext.squashAndMergeWorking("Modify comment for test0")

        self.assertNotEqual(remoteRepo.head.target, localRepo.head.target)

        return
        # We cannot yet test this code because the pygit2/libgit2 library does
        # not support pushing to local on-disk non-bare repos. When that is
        # implemented we need to remove the return
        # Error:
        # Failure: builtins.tuple: (<class '_pygit2.GitError'>, GitError("local
        # push doesn't (yet) support pushing to non-bare repos."), <traceback
        # object at 0x107613080>)
        localContext.pushToRemote("origin", "dummy username")
        self.assertEqual(remoteRepo.head.target, localRepo.head.target)

        newParam: ParameterTuple = remoteContext.getItem(
            ItemStorageGroupEnum.Parameter, "test0"
        )
        self.assertEqual(param.comment, newParam.comment)

    def testProjectPushWhenLocalAndRemoteModified(self):
        remoteContext: GitObjectStorageContext = self._createSimpleProject(
            self.remotePath
        )
        remoteRepo: pygit2.Repository = pygit2.Repository(
            self.remotePath / "git_storage"
        )

        # This clone will set the remote of the Git repo to the remote of the
        # Attune project
        GitObjectStorageContext.cloneGitRepo(
            self.repopath / "git_storage",
            str(self.remotePath / "git_storage"),
        )
        localContext = GitObjectStorageContext(
            self.repopath,
            ContextProjectInfo(
                id=1,
                key=ContextGitRepoTest.TEST_REPO,
                name=ContextGitRepoTest.TEST_REPO,
            ),
        )
        localRepo: pygit2.Repository = pygit2.Repository(
            self.repopath / "git_storage"
        )

        param: ParameterTuple = ParameterTuple(
            key="test0",
            name="test0",
            type=ParameterTuple.TEXT,
            comment="# Heading for parameter test0",
        )
        remoteContext.mergeItem(param)
        remoteContext.commit("Modify comment for test0 parameter")
        remoteContext.squashAndMergeWorking("Modify comment for test0")

        param: ParameterTuple = ParameterTuple(
            key="test0",
            name="test0",
            type=ParameterTuple.TEXT,
            comment="# Heading for test0",
        )
        localContext.addItem(param)
        localContext.commit("Modify comment for test0 parameter")
        localContext.squashAndMergeWorking("Modify comment for test0")

        self.assertNotEqual(remoteRepo.head.target, localRepo.head.target)

        return
        # We cannot yet test this code because the pygit2/libgit2 library does
        # not support pushing to local on-disk non-bare repos. When that is
        # implemented we need to remove the return
        # Error:
        # Failure: builtins.tuple: (<class '_pygit2.GitError'>, GitError("local
        # push doesn't (yet) support pushing to non-bare repos."), <traceback
        # object at 0x107613080>)

        # This should raise an error because we have to pull remote changes
        # first before pushing our changes
        with self.assertRaises(GitError):
            localContext.pushToRemote("origin", "dummy username")


if __name__ == "__main__":
    unittest.main()
