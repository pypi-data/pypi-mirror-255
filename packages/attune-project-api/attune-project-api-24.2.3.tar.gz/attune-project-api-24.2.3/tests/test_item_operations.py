import os
import shutil
import tempfile
import unittest
from pathlib import Path

import pygit2

from attune_project_api import ParameterTuple
from attune_project_api.Exceptions import NonUniqueNameError
from attune_project_api.StorageTuple import ItemStorageGroupEnum
from attune_project_api._contexts.GitObjectStorageContext import (
    GitObjectStorageContext,
)
from attune_project_api.context_project_info import ContextProjectInfo

WORKING_BRANCH = "__working__"

MASTER = "master"


class ContextItemOperationsTest(unittest.TestCase):
    TEST_REPO = "repo"

    author = pygit2.Signature("ServerTribe Attune", "attune@servertribe.com")

    def setUp(self) -> None:
        self.tempdir = Path(tempfile.gettempdir())
        self.repopath = self.tempdir / ContextItemOperationsTest.TEST_REPO

    def tearDown(self) -> None:
        if os.path.exists(self.repopath):
            shutil.rmtree(self.repopath)

    def testRenaming(self):
        context = GitObjectStorageContext(
            self.repopath,
            ContextProjectInfo(
                id=1,
                key=ContextItemOperationsTest.TEST_REPO,
                name=ContextItemOperationsTest.TEST_REPO,
            ),
        )

        param0 = ParameterTuple(
            key="test0",
            name="test0",
            type=ParameterTuple.TEXT,
            comment="# Heading for 0",
        )
        context.addItem(param0)
        context.commit("Add test0 parameter")

        param1 = ParameterTuple(
            key="test1",
            name="test1",
            type=ParameterTuple.TEXT,
            comment="# Heading for 1",
        )
        context.addItem(param1)
        context.commit("Add test1 parameter")

        # Item names should be checked for clashes when renaming
        with self.assertRaises(NonUniqueNameError):
            context.updateItemKey(param1, "test0")

        # test1 should still exist
        test1 = context.getItem(ItemStorageGroupEnum.Parameter, "test1")
        self.assertEqual(test1.key, param1.key)
        self.assertEqual(test1.name, param1.name)

        # Renaming an item and then renaming it back should work
        param1.name = "test2"
        context.updateItemKey(param1, "test2")
        context.commit("Renamed test1 to test2")

        test2 = context.getItem(ItemStorageGroupEnum.Parameter, "test2")
        # These are the same items
        self.assertEqual(param1.key, "test2")
        self.assertEqual(test2.key, "test2")
        self.assertEqual(test2.key, param1.key)
        self.assertEqual(test2.name, param1.name)
        self.assertEqual(test2.comment, param1.comment)

        param1.name = "test1"
        context.updateItemKey(param1, "test1")
        context.commit("Renamed test2 back to test1")

        test1 = context.getItem(ItemStorageGroupEnum.Parameter, "test1")
        self.assertEqual(param1.key, test1.key)
        self.assertEqual(param1.name, test1.name)
        self.assertEqual(param1.comment, test1.comment)

        # Renaming when updating other fields should work
        param1.name = "test2"
        param1.comment = "This is an updated comment"
        context.updateItemKey(param1, "test2")
        context.mergeItem(param1)
        context.commit("Updated test1 to test2")

        test2 = context.getItem(ItemStorageGroupEnum.Parameter, "test2")
        self.assertEqual(test2.key, param1.key)
        self.assertEqual(test2.name, param1.name)
        self.assertEqual(test2.comment, param1.comment)
        self.assertEqual(test2.comment, "This is an updated comment")


if __name__ == "__main__":
    unittest.main()
