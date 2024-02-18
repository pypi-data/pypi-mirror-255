import logging
import os
import unittest
from pathlib import Path

from attune_project_api.StorageTuple import ItemStorageGroupEnum
from attune_project_api._contexts import GitObjectStorageContext
from attune_project_api._private.website_compiler import WebsiteCompiler
from attune_project_api.context_project_info import ContextProjectInfo
from attune_project_api.items.step_tuples.step_group_tuple import StepGroupTuple

logger = logging.getLogger(__name__)


class RenderStaticSiteHtmlTest(unittest.TestCase):
    def setUp(self) -> None:
        try:
            logging.basicConfig(level=logging.DEBUG)
            path = "/home/attune/.local/share/com.servertribe.attune/projects"
            path = Path(path).expanduser()
            # projectKey = "hypervkickstarts"
            # projectName = "Hyper-V Kickstarts"
            directoryName = "installgoonubuntu"
            projectName = "Install Go on Ubuntu"
            self.path = path / directoryName
            self.context = GitObjectStorageContext(
                self.path,
                ContextProjectInfo(
                    id=1, directoryName=directoryName, name=projectName
                ),
            )
            self.context.load()
        except Exception as e:
            logger.exception(e)
            raise

    def test_renderHtml(self):
        websiteCompiler = WebsiteCompiler(self.context)

        websiteIndexContent = websiteCompiler.compileIndex()
        with open(self.path / "index.html", "w") as f:
            f.write(websiteIndexContent)

        websiteStyleContent = websiteCompiler.compileStyle()
        try:
            os.mkdir(self.path / "styles")
        except OSError as e:
            logger.exception(e)
        with open(self.path / "styles/style.css", "w") as f:
            f.write(websiteStyleContent)

        for s in self.context.getItems(ItemStorageGroupEnum.Step):
            if isinstance(s, StepGroupTuple) and s.isBlueprint:
                blueprintName = s.name.replace(" ", "-").replace(".", "-")
                websiteBlueprintContent = websiteCompiler.compileBlueprint(s)
                with open(self.path / f"{blueprintName}.html", "w") as f:
                    f.write(websiteBlueprintContent)
