from uuid import UUID

from .constant import FileType
from .upload import _path


def test__path():
    source_id = UUID("399a8b22-3187-11ec-8d3d-0242ac130003")
    file_type = FileType.VIZ
    file_path = "filename"

    path = _path(source_id, file_type, file_path)
    assert path == f"visualization-{source_id}/{file_path}"
