import re
import shutil
import sys
from pathlib import Path
from typing import List

from nmk.model.builder import NmkTaskBuilder
from nmk.model.cache import venv_libs
from nmk.model.keys import NmkRootConfig
from nmk.model.model import NmkModel
from nmk.model.resolver import NmkListConfigResolver
from nmk.utils import create_dir_symlink, run_with_logs
from nmk_base.common import TemplateBuilder

from nmk_proto.utils import get_input_all_sub_folders, get_input_unique_sub_folders, get_proto_folder, get_proto_paths_options

ERROR_LINE_PATTERN = re.compile("^([^ ]+Error: )(.*)")


# Grab some config items
def get_python_src_folder(model: NmkModel) -> Path:
    return Path(model.config["pythonSrcFolders"].value[0])


def get_python_out_folders(model: NmkModel) -> List[Path]:
    return model.config["protoPythonSrcFolders"].value


class OutputFoldersFinder(NmkListConfigResolver):
    def get_value(self, name: str) -> List[Path]:
        # Do we have a python source folder?
        if "pythonSrcFolders" in self.model.config:
            # Grab some variables values
            target_src = get_python_src_folder(self.model)
            return [target_src / p for p in get_input_unique_sub_folders(self.model)]
        else:
            return []


class OutputPythonFilesFinder(NmkListConfigResolver):
    def get_value(self, name: str) -> List[Path]:
        # Do we have python output folders
        output_folders = get_python_out_folders(self.model)
        if len(output_folders):
            # Grab some variables values
            target_src, proto_src = (get_python_src_folder(self.model), get_proto_folder(self.model))

            # Convert source proto file names to python ones
            return [
                target_src / f"{str(p_file)[:-len(p_file.suffix)]}{suffix}.py"
                for p_file in [Path(p).relative_to(proto_src) for p in self.model.config["protoInputFiles"].value]
                for suffix in ["_pb2", "_pb2_grpc"]
            ] + [p / "__init__.py" for p in output_folders]
        else:
            return []


class OutputProtoFilesFinder(NmkListConfigResolver):
    def get_value(self, name: str) -> List[Path]:
        # Do we have python output folders
        output_folders = get_python_out_folders(self.model)
        if len(output_folders):
            # Grab some variables values
            target_src, proto_src = (get_python_src_folder(self.model), get_proto_folder(self.model))

            # Copied proto file in python folder
            return [target_src / p_file for p_file in [Path(p).relative_to(proto_src) for p in self.model.config["protoInputFiles"].value]]
        else:
            return []


class OutputFoldersFinderWithWildcard(OutputFoldersFinder):
    def get_value(self, name: str) -> List[Path]:
        # Same than parent, with a "*" wildcard
        return [p / "*" for p in super().get_value(name)]


class ProtoLinkBuilder(NmkTaskBuilder):
    def build(self):
        # Only if link is not created yet
        if not self.main_output.exists():
            # Source path
            src_path = venv_libs()

            # Prepare output parent if not exists yet
            self.main_output.parent.mkdir(exist_ok=True, parents=True)

            # Ready to create symlink
            create_dir_symlink(src_path, self.main_output)


class ProtoPythonBuilder(TemplateBuilder):
    def make_absolute(self, option: str) -> Path:
        if not option.startswith("--") and not Path(option).is_absolute():
            return str(Path(self.model.config[NmkRootConfig.PROJECT_DIR].value) / option)
        return option

    def build(self, init_template: str):
        # Grab some config items
        target_src, out_folders, sub_folders = (get_python_src_folder(self.model), get_python_out_folders(self.model), get_input_all_sub_folders(self.model))

        # Clean and re-create target folders
        for output_dir in out_folders:
            candidate_dir = target_src / output_dir
            if candidate_dir.is_dir():
                shutil.rmtree(candidate_dir)
            candidate_dir.mkdir(parents=True, exist_ok=True)

        # Build proto paths list
        proto_paths = [self.make_absolute(o) for o in get_proto_paths_options(self.model)]

        # Iterate on inputs (proto files)
        for proto_file, target_subdir in zip(self.inputs, sub_folders):
            # Delegate to protoc
            run_with_logs(
                [sys.executable, "-m", "grpc_tools.protoc"]
                + proto_paths
                + [
                    "--python_out",
                    str(target_src),
                    "--pyi_out",
                    str(target_src),
                    "--grpc_python_out",
                    str(target_src),
                    str(proto_file),
                ]
            )

            # Also simply copy proto file to output
            shutil.copyfile(proto_file, target_src / target_subdir / proto_file.name)

        # Reorder output files
        importable_files = {out_folder.relative_to(target_src): [] for out_folder in out_folders}
        for candidate in [p.relative_to(target_src) for p in filter(lambda f: f.name.endswith("_pb2.py"), self.outputs)]:
            importable_files[candidate.parent].append(candidate.as_posix()[: -len(candidate.suffix)].replace("/", "."))

        # Browse importable packages
        for p, modules in importable_files.items():
            # Generate init file
            self.build_from_template(Path(init_template), target_src / p / "__init__.py", {"modules": modules})


class ProtoPythonChecker(NmkTaskBuilder):
    def build(self, src_folders: List[Path]):
        target_src = get_python_src_folder(self.model)
        for p in src_folders:
            # Try to import, to verify any name overlap
            cp = run_with_logs([sys.executable, "-c", f"from {p.relative_to(target_src).as_posix().replace('/','.')} import *"], check=False)
            if cp.returncode != 0:
                # Just print meaningfull error
                raise AssertionError(next(filter(lambda m: m is not None, map(ERROR_LINE_PATTERN.match, cp.stderr.splitlines()))).group(2))
