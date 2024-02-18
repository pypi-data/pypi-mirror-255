import logging
import os
from pathlib import Path

from mako import exceptions
from mako.lookup import TemplateLookup

from attune_project_api.StorageTuple import ItemStorageGroupEnum
from attune_project_api._contexts import GitObjectStorageContext
from attune_project_api.items.step_tuples.step_group_tuple import StepGroupTuple


logger = logging.getLogger(__name__)

INDEX_FOLDER: Path = Path(
    os.path.dirname(__file__) + "/templates/project_website"
)
STYLE_FOLDER: Path = Path(
    os.path.dirname(__file__) + "/templates/project_website/styles"
)
BLUEPRINT_FOLDER: Path = Path(
    os.path.dirname(__file__) + "/templates/project_website"
)


class WebsiteCompiler:
    def __init__(self, context: GitObjectStorageContext):
        self._context = context

    def blueprints(self):
        blueprints = [
            s
            for s in self._context.getItems(ItemStorageGroupEnum.Step)
            if isinstance(s, StepGroupTuple) and s.isBlueprint
        ]
        return blueprints

    def compileIndex(self) -> str:
        lookup = TemplateLookup(directories=[INDEX_FOLDER])
        htmlTemplate = lookup.get_template("ProjectWebsiteIndex.html.mako")

        try:
            return str(
                htmlTemplate.render(
                    makoGlobal={},
                    projectMetadata=self._context.metadata,
                    blueprints=self.blueprints(),
                )
            )
        except Exception:
            raise Exception(exceptions.text_error_template().render())

    def compileStyle(self) -> str:
        lookup = TemplateLookup(directories=[STYLE_FOLDER])
        styleTemplate = lookup.get_template("ProjectWebsiteStyle.css.mako")

        try:
            return str(styleTemplate.render())
        except Exception:
            raise Exception(exceptions.text_error_template().render())

    def compileBlueprint(self, blueprint) -> str:
        lookup = TemplateLookup(directories=[BLUEPRINT_FOLDER])
        blueprintTemplate = lookup.get_template(
            "ProjectWebsiteBlueprint.html.mako"
        )

        try:
            return str(
                blueprintTemplate.render(
                    makoGlobal={},
                    projectMetadata=self._context.metadata,
                    blueprint=blueprint,
                )
            )
        except Exception:
            raise Exception(exceptions.text_error_template().render())

    def generateWebsite(self) -> None:
        self._context._writeFile(
            "docs/index.html", self.compileIndex().encode()
        )
        self._context._writeFile(
            "docs/styles/style.css", self.compileStyle().encode()
        )
        for s in self._context.getItems(ItemStorageGroupEnum.Step):
            if isinstance(s, StepGroupTuple) and s.isBlueprint:
                blueprintName = s.name.replace(" ", "-").replace(".", "-")
                self._context._writeFile(
                    f"docs/{blueprintName}.html",
                    self.compileBlueprint(s).encode(),
                )
