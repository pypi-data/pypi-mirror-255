import os
import sys
from sphinx.application import Sphinx
import sphinx.ext.apidoc as apidoc
import sphinx.cmd.build
import subprocess
from pathlib import Path
from py2docfx import PACKAGE_ROOT
from py2docfx.convert_prepare.package_info import PackageInfo
from py2docfx.convert_prepare.paths import folder_is_hidden
from py2docfx.convert_prepare.subpackage import (get_subpackages,
                                        move_rst_files_to_subfolder)

DEBUG_SPHINX_FLAG = 'PY2DOCFX_DEBUG_SPHINX'

def run_apidoc(rst_path, source_code_path, exclude_paths, package_info: PackageInfo):
    """
    Run sphinx-apidoc to generate RST inside rst_path folder

    Replacing
    https://apidrop.visualstudio.com/Content%20CI/_git/ReferenceAutomation?path=/Python/build.ps1&line=110&lineEnd=126&lineStartColumn=1&lineEndColumn=14&lineStyle=plain&_a=contents
    """
    subfolderList = [name for name in
                       os.listdir(source_code_path)
                       if os.path.isdir(os.path.join(source_code_path, name))
                       and not folder_is_hidden(os.path.join(source_code_path, name))]
    package_paths = package_info.path
    subpackages_rst_record = None
    for subfolder in subfolderList:
        subfolderPath = os.path.join(source_code_path, subfolder)
        if os.path.isdir(subfolderPath):
            print("<CI INFO>: Subfolder path {}.".format(subfolderPath))
            args = [
                "--module-first",
                "--no-headings",
                "--no-toc",
                "--implicit-namespaces",
                "-o",
                rst_path,
                subfolderPath,
            ]
            args.extend(exclude_paths)
            apidoc.main(args)
            if package_info.build_in_subpackage and subfolder == "azure":
                subpackages_rst_record = move_rst_files_to_subfolder(
                    package_paths.doc_folder, package_info.name,
                    get_subpackages(subfolderPath, package_info.name))
    return subpackages_rst_record


def run_converter(rst_path, out_path, conf_path = None):
    """
    Take rst files as input and run sphinx converter

    :return: the location of generated yamls

    Replacing
    https://apidrop.visualstudio.com/Content%20CI/_git/ReferenceAutomation?path=/Python/build.ps1&line=150&lineEnd=161&lineStartColumn=13&lineEndColumn=52&lineStyle=plain&_a=contents
    """

    outdir = os.path.join(out_path, "_build")

    # Sphinx/docutils have memory leak including linecaches, module-import-caches,
    # Use a subprocess on production to prevent out of memory
    debug_into_sphinx = os.environ.get(DEBUG_SPHINX_FLAG, 'false')
    debug_into_sphinx = debug_into_sphinx.lower() in {'true', '1'}
    if debug_into_sphinx:
        app = Sphinx(
            srcdir=rst_path,
            outdir=outdir,
            confdir=conf_path or rst_path,
            doctreedir=os.path.join(outdir, "doctrees"),
            buildername="yaml",
        )
        app.build(force_all=True)
    else:
        sphinx_build_path = sphinx.cmd.build.__file__
        if not sys.executable:
            raise ValueError("Can't get the executable binary for the Python interpreter.")
        sphinx_param = [
            sys.executable, sphinx_build_path,
            rst_path,
            outdir,
            '-c', conf_path or rst_path,
            '-d', os.path.join(outdir, "doctrees"),
            '-b', 'yaml'
        ]

        # TODO: update generate_conf to replace "yaml_builder" with "py2docfx.docfx_yaml.yaml_builder"
        # then no need to manually add docfx_yaml to path
        package_root_parent = os.path.join(PACKAGE_ROOT, 'docfx_yaml')
        env_tmp = os.environ.copy()
        python_path_current = env_tmp.get('PYTHONPATH', None)
        if os.name == 'nt' :
            env_tmp["PYTHONPATH"] = f"{package_root_parent};{python_path_current}" if python_path_current else package_root_parent
        else:
            env_tmp["PYTHONPATH"] = f"{package_root_parent}:{python_path_current}" if python_path_current else package_root_parent
        subprocess.run(sphinx_param, check=True, cwd=PACKAGE_ROOT, env=env_tmp)
    return outdir
