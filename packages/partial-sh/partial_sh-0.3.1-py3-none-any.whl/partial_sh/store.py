import logging
import os
from datetime import datetime
from pathlib import Path

from langchain.pydantic_v1 import BaseModel, ValidationError

from .shape import ShapeConfigFile

logger = logging.getLogger(__name__)


class ShapeInfo(BaseModel):
    id: str
    name: str
    filename: str | None = None
    content: ShapeConfigFile | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ShapeStore:
    path: Path
    shape_infos: list[ShapeInfo] = []

    def __init__(self, path: Path):
        self.path = path

    def refresh(self):
        self.shape_infos = []
        self.list()

    def list(self):
        for filename in os.listdir(self.path):
            if filename.endswith(".json"):
                shape_name = filename[:-5].split("__")
                if len(shape_name) < 2:
                    continue
                shape_id = shape_name[0]
                shape_name = shape_name[1]

                # Get when file was created
                created_at = datetime.fromtimestamp(
                    os.path.getctime(self.path / filename)
                )
                # created_at = created_at.isoformat()
                # Get when file was last modified
                updated_at = datetime.fromtimestamp(
                    os.path.getmtime(self.path / filename)
                )
                # updated_at = updated_at.isoformat()

                self.shape_infos.append(
                    ShapeInfo(
                        id=shape_id,
                        name=shape_name,
                        filename=filename,
                        created_at=created_at,
                        updated_at=updated_at,
                    )
                )
        return self.shape_infos

    def find_shape_file(self, shape_arg: str) -> Path:
        """
        Find the shape file based on the shape argument.
        """
        # Refresh the shape store
        self.refresh()
        # Check if the shape argument is already a file
        shape_file = Path(shape_arg)
        if shape_file.is_file():
            return shape_file

        # If not a file, try to find it in the shape store
        shape_file = self.get_filepath_by_id(shape_arg) or self.get_filepath_by_name(
            shape_arg
        )

        if not shape_file or not shape_file.is_file():
            # Handle the error as appropriate for your application
            return None

        return shape_file

    def get_filepath_by_id(self, id: str):
        for shape_info in self.shape_infos:
            if shape_info.id.startswith(id.split("-")[0]):
                filename = shape_info.filename
                shape_path = self.path / filename
                return shape_path
        return None

    def get_filepath_by_name(self, name: str):
        for shape_info in self.shape_infos:
            if shape_info.name.startswith(name):
                filename = shape_info.filename
                shape_path = self.path / filename
                return shape_path
        return None

    def get_by_id(self, id: str):
        for shape_info in self.shape_infos:
            if shape_info.id.startswith(id.split("-")[0]):
                filename = shape_info.filename
                shape_path = self.path / filename
                with open(shape_path, "r") as f:
                    try:
                        shape = ShapeConfigFile.parse_raw(f.read())
                    except ValidationError:
                        logger.error("Error parsing file %s", filename)
                        return None
                shape_info.content = shape
                return shape_info
        return None

    def get_by_name(self, name: str) -> ShapeInfo | None:
        matching_shapes = [p for p in self.shape_infos if p.name.startswith(name)]

        # Sort shapes by updated_at in descending order and get the most recent one
        if matching_shapes:
            latest_shape = max(
                matching_shapes, key=lambda p: p.updated_at or datetime.min
            )

            filename = latest_shape.filename
            shape_path = self.path / filename
            with open(shape_path, "r") as f:
                try:
                    shape = ShapeConfigFile.parse_raw(f.read())
                except ValidationError:
                    logger.error("Error parsing file %s", filename)
                    return None
            latest_shape.content = shape
            return latest_shape
        else:
            return None
