import logging
import os
import shutil
import stat
from datetime import datetime
from pathlib import Path
from typing import Optional

import pygit2
import pytz
import requests
from pytmpdir.directory_ import Directory

from attune_project_api._contexts.GitLibMixin import GitRemoteUsernamePassword
from attune_project_api._contexts.GitLibMixin import NotAGitProjectException

logger = logging.getLogger(__name__)

from contextlib import contextmanager


@contextmanager
def _disableRequestSslWarnings():
    import warnings
    import urllib3

    with warnings.catch_warnings():
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        yield None


try:
    WindowsError
except:

    class WindowsError(Exception):
        pass


class ProjectApiCloneController:
    def clone(
        self,
        cloneUrl: str,
        newProjectPath: Path,
        username: Optional[str] = None,
        password: Optional[str] = None,
        requireValidSsl: bool = True,
    ):
        startTime = datetime.now(pytz.UTC)
        if newProjectPath.exists():
            raise Exception(
                f"Project directory already exists: " f"{newProjectPath}"
            )

        if not newProjectPath.parent.exists():
            raise Exception(
                f"Project directory parent does not exist: "
                f"{newProjectPath.parent}"
            )


        auth = None
        if username and password:
            auth = GitRemoteUsernamePassword(username, password)

        logger.debug(
            "Checking if %s has access to %s",
            cloneUrl,
            f"user {auth.username}" if auth else "<anonymous>",
        )
        self._checkServerGitAuthResponse(
            cloneUrl=cloneUrl, auth=auth, requireValidSsl=requireValidSsl
        )

        tmpPath = Directory(autoDelete=False)
        try:
            from attune_project_api._contexts import GitLibMixin

            logger.debug("Starting cone for %s", cloneUrl)
            GitLibMixin.clone(
                clonePath=Path(tmpPath.path) / "git_storage",
                cloneUrl=cloneUrl,
                auth=auth,
                requireValidSsl=requireValidSsl,
            )
            shutil.copytree(tmpPath.path, newProjectPath)
            logger.info(
                f"Cloning complete for {cloneUrl} in "
                f"{datetime.now(pytz.UTC) - startTime}"
            )

        except (pygit2.GitError, NotAGitProjectException, Exception) as e:
            logger.error(
                f"Cloning failed for {cloneUrl} into "
                f"{newProjectPath} in "
                f"{datetime.now(pytz.UTC) - startTime}"
            )
            logger.exception(e)

            msg = str(e)
            if msg.startswith("remote authentication"):
                raise Exception(
                    f"Failed to clone project."
                    f" Authentication failed, Try checking the "
                    f"user and password."
                )
            elif msg.startswith("too many redirects"):
                raise Exception(
                    f"Failed to clone project."
                    f" Too many redirects, check the clone URL."
                )
            else:
                raise e
        finally:
            # Delete the temp directory with this method, that ignores errors

            self._deleteProjectDir(Path(tmpPath.path))


    def _checkServerGitAuthResponse(
        self,
        cloneUrl: str,
        requireValidSsl: bool,
        auth: Optional[GitRemoteUsernamePassword],
    ) -> None:
        headers = {"accept": "text/plain"}

        def makeRequest():
            return requests.get(
                cloneUrl + "/info/refs?service=git-upload-pack",
                headers=headers,
                auth=auth,
            )

        if not requireValidSsl:
            with _disableRequestSslWarnings():
                r = makeRequest()
        else:
            r = makeRequest()

        # All good
        if r.status_code == 200:
            return

        if "text/plain" not in r.headers["content-type"]:
            logger.debug(
                f"_checkServerGitAuthResponse"
                f" status-code={r.status_code},"
                f" content-type={r.headers['content-type']}"
                f" content[:150]={r.text[:150]}"
            )

            raise Exception("Invalid GIT Clone URL")

        msg = f"Status:{r.status_code} - {r.text}"

        # This is what github says if you don't have permission.
        if "Repository not found." in r.text:
            msg += (
                " It may be a private repository or you might not have"
                " access to it, try using different credentials."
            )

        logger.debug(f"_checkServerGitAuthResponse {msg}")

        raise Exception(msg)

    def _deleteProjectDir(self, path: Path) -> None:
        # Helper for read-only files on Windows not being deleted
        # (freed) until interpreter exits
        def remove_readonly(func, path, _):
            logger.warning(f"Ignoring failure to delete %s", path)
            os.chmod(path, stat.S_IWRITE)
            func(path)

        # Delete the folder for the project
        shutil.rmtree(path, ignore_errors=True, onerror=remove_readonly)
