from __future__ import annotations # Avoid A | B annotation break under <= py3.9
import argparse
import os
import sys
from py2docfx import PACKAGE_ROOT
from py2docfx.convert_prepare.generate_document import generate_document
from py2docfx.convert_prepare.get_source import get_source, YAML_OUTPUT_ROOT
from py2docfx.convert_prepare.install_package import install_package
from py2docfx.convert_prepare.post_process.merge_toc import merge_toc, move_root_toc_to_target
from py2docfx.convert_prepare.params import load_file_params, load_command_params
from py2docfx.convert_prepare.package_info import PackageInfo

print("Adding yaml extension to path")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),'docfx_yaml'))
os.chdir(PACKAGE_ROOT)

def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            """A command line tool to run Sphinx with docfx-yaml extension, 
                        transform python source code packages to yamls supported in docfx"""
        )
    )

    parser.add_argument(
        "-o"
        "--output-root-folder",
        default=None,
        dest="output_root",
        help="The output folder storing generated documents, use cwd if not assigned",
    )
    parser.add_argument(
        "--github-token",
        default=None,
        dest="github_token",
        help="Allow pipeline to clone Github source code repo",
    )
    parser.add_argument(
        "--ado-token",
        default=None,
        dest="ado_token",
        help="Allow pipeline to clone Azure DevOps source code repo",
    )
    parser.add_argument(
        "-f",
        "--param-file-path",
        dest="param_file_path",
        help="The json file contains package infomation",
    )
    parser.add_argument(
        "-j",
        "--param-json",
        default=None,
        dest="param_json",
        help="The json string contains package infomation",
    )
    parser.add_argument(
        "-t",
        "--install-type",
        action="store",
        dest="install_type",
        choices=["pypi", "source_code", "dist_file"],
        help="""The type of source package, can be pip package, github repo or a distribution
                        file accessible in public""",
    )
    parser.add_argument(
        "-n",
        "--package-name",
        default=None,
        dest="package_name",
        help="The name of source package, required if INSTALL_TYPE==pypi",
    )
    parser.add_argument(
        "-v",
        "--version",
        default=None,
        dest="version",
        help="The version of source package, if not assigned, will use latest version",
    )
    parser.add_argument(
        "-i",
        "--extra-index-url",
        default=None,
        dest="extra_index_url",
        help="Extra index of pip to download source package",
    )
    parser.add_argument(
        "--url",
        default=None,
        dest="url",
        help="""Valid when INSTALL_TYPE==source_code, url of the repo to
                         clone which contains SDK package source code.""",
    )
    parser.add_argument(
        "--branch",
        default=None,
        dest="branch",
        help="""Valid when INSTALL_TYPE==source_code, branch of the repo to clone which
                         contains SDK package source code.""",
    )
    parser.add_argument(
        "--editable",
        default=False,
        dest="editable",
        help="""Install a project in editable mode.""",
    )
    parser.add_argument(
        "--folder",
        default=None,
        dest="folder",
        help="""Valid when INSTALL_TYPE==source_code, relative folder path inside the repo
                         containing SDK package source code.""",
    )
    parser.add_argument(
        "--prefer-source-distribution",
        dest="prefer_source_distribution",
        action="store_true",
        help="""Valid when INSTALL_TYPE==pypi, a flag which add --prefer-binary
                         option to pip commands when getting package source.""",
    )
    parser.add_argument(
        "--location",
        default=None,
        dest="location",
        help="""Valid when INSTALL_TYPE==dist_file, the url of distribution file
                         containing source package.""",
    )
    parser.add_argument(
        "--build-in-subpackage",
        action="store_true",
        dest="build_in_subpackage",
        help="""When package has lot of big subpackages and each doesn't depend on others
                    enable to fasten build""",
    )
    parser.add_argument(
        "--venv-required",        
        default=True,
        action=argparse.BooleanOptionalAction,
        dest="venv_required",
        help="""Required running env is a virtual env or not.""",
    )
    parser.add_argument(
        "exclude_path",
        default=[],
        nargs="*",
        help="""A list containing relative paths to the root of the package of files/directories
                         excluded when generating documents, should follow fnmatch-style.""",
    )
    return parser


def parse_command_line_args(argv) -> (
        list[PackageInfo], list[PackageInfo], str, str, str | os.PathLike, bool):
    parser = get_parser()
    args = parser.parse_args(argv)

    github_token = args.github_token
    ado_token = args.ado_token
    output_root = args.output_root
    venv_required = args.venv_required

    if args.param_file_path:
        (package_info_list, required_packages) = load_file_params(args.param_file_path)
        return (package_info_list, required_packages, github_token,
                ado_token, output_root, venv_required)
    elif args.param_json:
        (package_info_list, required_packages) = load_command_params(args.param_json)
        return (package_info_list, required_packages, github_token,
                ado_token, output_root, venv_required)
    else:
        package_info = PackageInfo()
        if not args.install_type:
            PackageInfo.report_error("install_type", args.install_type)
        package_info.install_type = PackageInfo.InstallType[
            args.install_type.upper()
        ]

        package_info.name = args.package_name
        package_info.version = args.version
        package_info.extra_index_url = args.extra_index_url
        package_info.editable = args.editable
        package_info.prefer_source_distribution = (
            args.prefer_source_distribution
        )
        package_info.build_in_subpackage = args.build_in_subpackage
        package_info.exclude_path = args.exclude_path

        if (
            package_info.install_type == PackageInfo.InstallType.PYPI
            and not package_info.name
        ):
            PackageInfo.report_error("name", "None")

        if package_info.install_type == PackageInfo.InstallType.SOURCE_CODE:
            package_info.url = args.url
            package_info.branch = args.branch
            package_info.folder = args.folder
            if not package_info.url:
                if not package_info.folder:
                    raise ValueError(
                        "When install_type is source_code, folder or url should be provided"
                    )
                else:
                    print(f'Read source code from local folder: {package_info.folder}')

        if package_info.install_type == PackageInfo.InstallType.DIST_FILE:
            package_info.location = args.location
            if not package_info.location:
                PackageInfo.report_error(
                    "location",
                    "None",
                    condition="When install_type is dist_file",
                )
        return ([package_info], [], github_token, ado_token, output_root, venv_required)

def install_required_packages(
        required_package_list: list[PackageInfo], github_token: str, ado_token: str):
    for idx, package in enumerate(required_package_list):
        if package.install_type == package.InstallType.SOURCE_CODE:
            get_source(package, idx, vststoken=ado_token, githubtoken=github_token)
        install_package(package)

def donwload_package_generate_documents(
        package_info_list: list[PackageInfo],
        output_root: str | os.PathLike | None,
        output_doc_folder: os.PathLike | None,
        github_token: str, ado_token: str, start_num: int):

    for idx, package in enumerate(package_info_list):
        package_number = start_num + idx
        get_source(package, package_number, vststoken=ado_token, githubtoken=github_token)
        install_package(package)
        generate_document(package, output_root)
        merge_toc(YAML_OUTPUT_ROOT, package.path.yaml_output_folder)
        if output_doc_folder:
            package.path.move_document_to_target(os.path.join(output_doc_folder, package.name))
    if output_doc_folder:
        move_root_toc_to_target(YAML_OUTPUT_ROOT, output_doc_folder)

def prepare_out_dir(output_root: str | os.PathLike) -> os.PathLike | None:
    # prepare output_root\DOC_FOLDER_NAME (if folder contains files, raise exception)
    if output_root:
        if os.path.exists(output_root):
            if os.path.isfile(output_root):
                raise ValueError(f"""output-root-folder is a path of file,
                                 output-root-folder value: {output_root}""")
            else:
                if len(os.listdir(output_root)) > 0:
                    raise ValueError(f"""output-root-folder isn't empty,
                                    output-root-folder value: {output_root}""")
                return output_root
        else:
            os.makedirs(output_root)
            return output_root
    else:
        return None

def main(argv) -> int:
    (package_info_list, required_package_list, github_token, ado_token, output_root, \
          venv_required) = parse_command_line_args(argv)
    if venv_required and sys.prefix == sys.base_prefix:
        raise ValueError("""Please run in a virtual env to prevent breaking your dev
                        environment when not running on pipeliens""")
    output_doc_folder = prepare_out_dir(output_root)
    install_required_packages(required_package_list, github_token, ado_token)
    donwload_package_generate_documents(
        package_info_list, output_root, output_doc_folder,
        github_token, ado_token, len(list(required_package_list)))
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
