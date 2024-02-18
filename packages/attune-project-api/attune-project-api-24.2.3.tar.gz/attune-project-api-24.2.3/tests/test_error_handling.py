import os
import shutil
import tempfile
import unittest
from pathlib import Path

import pygit2

from attune_project_api.Exceptions import ItemNotFoundError
from attune_project_api.Exceptions import NoChangesToCommitError
from attune_project_api.Exceptions import NonUniqueNameError
from attune_project_api.Exceptions import NonUniqueScriptRefError
from attune_project_api.StorageTuple import ItemStorageGroupEnum
from attune_project_api._contexts import GitObjectStorageContext
from attune_project_api._contexts.GitLibMixin import ATTUNE_WORKING_BRANCH
from attune_project_api.context_project_info import ContextProjectInfo
from attune_project_api.items.parameter_tuple import ParameterTuple
from tests.utils import getLatestCommitIdOnBranch


class ContextErrorHandlingTest(unittest.TestCase):
    TEST_REPO = "test"

    def setUp(self) -> None:
        self.tempdir = Path(tempfile.gettempdir())
        self.repopath = self.tempdir / ContextErrorHandlingTest.TEST_REPO

    def tearDown(self) -> None:
        if os.path.exists(self.repopath):
            shutil.rmtree(self.repopath)

    def testWorkingBranchResetOnError(self):
        context = GitObjectStorageContext(
            self.repopath,
            ContextProjectInfo(
                id=1,
                directoryName=ContextErrorHandlingTest.TEST_REPO,
                name=ContextErrorHandlingTest.TEST_REPO,
            ),
        )
        # Also load the project repository separately
        repo = pygit2.Repository(self.repopath / "git_storage")

        param = ParameterTuple(
            key="test0", name="Test0", type=ParameterTuple.TEXT
        )
        context.addItem(param)
        context.commit("Add a parameter")

        # This should create the working branch if it does not exist and load
        # the latest commit it is based on in the _workingId field. This is the
        # ID of the commit at which the __working__ branch was created
        workingId = None
        with self.assertRaises(Exception), context:
            workingId = getLatestCommitIdOnBranch(repo, ATTUNE_WORKING_BRANCH)
            self.assertTrue(ATTUNE_WORKING_BRANCH in repo.branches)
            self.assertEqual(workingId, context._workingId)

            param = ParameterTuple(
                key="test1", name="Test1", type=ParameterTuple.TEXT
            )
            context.addItem(param)
            context.commit("Add a parameter")

            # __working__ branch ID should have changed due to the commit
            self.assertNotEqual(
                getLatestCommitIdOnBranch(repo, ATTUNE_WORKING_BRANCH),
                workingId,
            )

            # Raise an exception to trigger the reset of working branch
            raise Exception("This is an exception")

        # The working branch should still be there and must be reset to before
        # the parameter commit
        self.assertEqual(
            getLatestCommitIdOnBranch(repo, ATTUNE_WORKING_BRANCH),
            workingId,
        )
        self.assertTrue(ATTUNE_WORKING_BRANCH in repo.branches)
        self.assertIsNone(context._workingId)
        # The master branch should have been checked out at the end
        self.assertEqual(repo.head.name, "refs/heads/master")

        # The item from before the context should still be there
        context.getItem(ItemStorageGroupEnum.Parameter, "test0")
        with self.assertRaises(ItemNotFoundError):
            # The item from within the failure context should not be there
            context.getItem(ItemStorageGroupEnum.Parameter, "test1")

    def testExceptionOnSquashAndMergeInContext(self):
        context = GitObjectStorageContext(
            self.repopath,
            ContextProjectInfo(
                id=1,
                directoryName=ContextErrorHandlingTest.TEST_REPO,
                name=ContextErrorHandlingTest.TEST_REPO,
            ),
        )

        with self.assertRaises(Exception), context:
            param = ParameterTuple(
                key="test0", name="Test0", type=ParameterTuple.TEXT
            )
            context.addItem(param)
            context.commit("Add a parameter")

            param = ParameterTuple(
                key="test1", name="Test1", type=ParameterTuple.TEXT
            )
            context.addItem(param)
            context.commit("Add a parameter")

            # This should raise an exception because we are editing the
            # __working__ branch in the context
            context.squashAndMergeWorking("This commit is not going to succeed")

        with self.assertRaises(NoChangesToCommitError):
            context.squashAndMergeWorking(
                "There is nothing to commit because __working__ was reset"
            )

    def testParameterAndScriptReferenceClash(self):
        context = GitObjectStorageContext(
            self.repopath,
            ContextProjectInfo(
                id=1,
                directoryName=ContextErrorHandlingTest.TEST_REPO,
                name=ContextErrorHandlingTest.TEST_REPO,
            ),
        )

        param = ParameterTuple(
            key="servername", name="Server Name", type=ParameterTuple.TEXT
        )
        context.addItem(param)
        context.commit("Add a parameter")

        with self.assertRaises(NonUniqueNameError):
            param = ParameterTuple(
                key="servername",
                name="Server Name",
                type=ParameterTuple.LIN_SERVER,
            )
            context.addItem(param)

        with self.assertRaises(NonUniqueScriptRefError):
            param = ParameterTuple(
                key="servername",
                name="ServerName",
                type=ParameterTuple.LIN_SERVER,
            )
            context.addItem(param)


if __name__ == "__main__":
    unittest.main()
