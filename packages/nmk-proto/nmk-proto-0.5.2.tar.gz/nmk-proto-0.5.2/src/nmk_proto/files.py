from pathlib import Path
from typing import List

from nmk.model.keys import NmkRootConfig
from nmk.model.resolver import NmkListConfigResolver

from nmk_proto.utils import get_input_all_sub_folders, get_input_proto_files, get_proto_deps, get_proto_folder


class ProtoFilesFinder(NmkListConfigResolver):
    def get_value(self, name: str) -> List[Path]:
        # Iterate on source paths, and find all proto files
        return list(filter(lambda f: f.is_file(), get_proto_folder(self.model).rglob("*.proto")))


class ProtoAllSubDirsFinder(NmkListConfigResolver):
    def get_value(self, name: str) -> List[Path]:
        # All sub-folders, relative to proto folder (exactly one per proto file)
        return [p.parent.relative_to(get_proto_folder(self.model)) for p in get_input_proto_files(self.model)]


class ProtoUniqueSubDirsFinder(NmkListConfigResolver):
    def get_value(self, name: str) -> List[Path]:
        # Set filtered subfolders
        return list(set(get_input_all_sub_folders(self.model)))


class ProtoPathOptionsBuilder(NmkListConfigResolver):
    def make_relative(self, p: Path) -> Path:
        # Make it project relative if possible
        if p.is_absolute():  # pragma: no branch
            try:
                return p.relative_to(self.model.config[NmkRootConfig.PROJECT_DIR].value)
            except ValueError:  # pragma: no cover
                # Simply ignore, non project-relative
                pass
        return p  # pragma: no cover

    def get_value(self, name: str) -> List[str]:
        # Return a list of protoc path options
        out = []
        for p in map(self.make_relative, [get_proto_folder(self.model)] + get_proto_deps(self.model)):
            out.extend(["--proto_path", p.as_posix()])
        return out
