import unittest
from pathlib import Path

from pytmpdir.directory_ import Directory

from attune_project_api.remote.project_api_clone_controller import (
    ProjectApiCloneController,
)

ATTUNE_TEST_PROJECT_PRIVATE_GITHUB_URL = (
    "https://github.com/Attune-Automation"
    "/devops-unit-tests-private-project.git"
)

ATTUNE_TEST_PROJECT_PRIVATE_GITLAB_URL = (
    "https://gitlab.com/servertribe/attune-projects"
    "/devops-unit-tests-private-project.git"
)


ATTUNE_BUILDS_AND_UPGRADE_PROJECT_URL = (
    "https://gitlab.com/servertribe/attune-projects"
    "/attune-builds-and-upgrades.git"
)

ATTUNE_INSTALL_7Z_PROJECT_URL = (
    "https://github.com/Attune-Automation/Attune-Install-7-Zip.git"
)


NOT_AN_ATTUNE_PROJECT_URL = "https://github.com/Synerty/tcp-over-websocket.git"


class ProjectApiCloneControllerTest(unittest.TestCase):
    def test_fail_clone_private_gitlab_project(self):
        tmpDirectory = Directory()
        self.assertRaises(
            Exception,
            ProjectApiCloneController().clone,
            cloneUrl=ATTUNE_TEST_PROJECT_PRIVATE_GITLAB_URL,
            newProjectPath=Path(tmpDirectory.path) / "test",
        )

        # The clone should not clone anything
        tmpDirectory.scan()
        self.assertEqual(0, len(tmpDirectory.files))

        try:
            ProjectApiCloneController().clone(
                cloneUrl=ATTUNE_TEST_PROJECT_PRIVATE_GITLAB_URL,
                newProjectPath=Path(tmpDirectory.path) / "test2",
            )

        except Exception as e:
            self.assertTrue(
                "The provided password or token is incorrect" in str(e)
            )

        del tmpDirectory

    def test_fail_clone_private_github_project(self):
        tmpDirectory = Directory()
        self.assertRaises(
            Exception,
            ProjectApiCloneController().clone,
            cloneUrl=ATTUNE_TEST_PROJECT_PRIVATE_GITHUB_URL,
            newProjectPath=Path(tmpDirectory.path) / "test",
        )

        # The clone should not clone anything
        tmpDirectory.scan()
        self.assertEqual(0, len(tmpDirectory.files))

        try:
            ProjectApiCloneController().clone(
                cloneUrl=ATTUNE_TEST_PROJECT_PRIVATE_GITHUB_URL,
                newProjectPath=Path(tmpDirectory.path) / "test2",
            )

        except Exception as e:
            self.assertTrue("It may be a private repository" in str(e))

        del tmpDirectory

    def test_fail_not_attune_project(self):
        tmpDirectory = Directory()
        self.assertRaises(
            Exception,
            ProjectApiCloneController().clone,
            cloneUrl=NOT_AN_ATTUNE_PROJECT_URL,
            newProjectPath=Path(tmpDirectory.path) / "test",
        )

        # The clone should not clone anything
        tmpDirectory.scan()
        self.assertEqual(0, len(tmpDirectory.files))

        try:
            ProjectApiCloneController().clone(
                cloneUrl=NOT_AN_ATTUNE_PROJECT_URL,
                newProjectPath=Path(tmpDirectory.path) / "test2",
            )

        except Exception as e:
            print(str(e))
            self.assertTrue("not an Attune Design Project" in str(e))

        # The clone should not clone anything
        tmpDirectory.scan()
        self.assertEqual(0, len(tmpDirectory.files))

        del tmpDirectory

    def test_clone_attune_builds_and_uograde_projects(self):
        tmpDirectory = Directory()
        ProjectApiCloneController().clone(
            cloneUrl=ATTUNE_BUILDS_AND_UPGRADE_PROJECT_URL,
            newProjectPath=Path(tmpDirectory.path) / "projectkey",
        )

        tmpDirectory.scan()

        self.assertIsNotNone(
            tmpDirectory.getFile(pathName="projectkey/git_storage/.gitignore")
        )

    def test_clone_attune_install_7z_project(self):
        tmpDirectory = Directory()
        ProjectApiCloneController().clone(
            cloneUrl=ATTUNE_INSTALL_7Z_PROJECT_URL,
            newProjectPath=Path(tmpDirectory.path) / "projectkey",
        )

        tmpDirectory.scan()

        self.assertIsNotNone(
            tmpDirectory.getFile(pathName="projectkey/git_storage/.gitignore")
        )


if __name__ == "__main__":
    unittest.main()
