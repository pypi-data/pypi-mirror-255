from __future__ import annotations # Avoid A | B annotation break under <= py3.9
import os
from py2docfx.convert_prepare.generate_conf import generate_conf
from py2docfx.convert_prepare.git import checkout
from py2docfx.convert_prepare.package_info import PackageInfo
from py2docfx.convert_prepare.sphinx_caller import run_apidoc, run_converter
from py2docfx.convert_prepare.subpackage import merge_subpackage_files

CONF_TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "conf_templates")

def generate_document(pkg: PackageInfo, output_root: str | os.PathLike):
    # Copy manual written RST from target doc repo
    package_paths = pkg.path
    if output_root:
        manual_rst_dir = f"{output_root}/ci_scripts/ref/{pkg.name}"
        use_manual_rst = package_paths.copy_manual_rst(manual_rst_dir)
    else:
        use_manual_rst = False
    subpackages_rst_record = None

    if not use_manual_rst:
        # use apidoc to generate RST files
        package_paths.create_doc_folder()
        package_paths.remove_all_rst()
        exclude_paths = pkg.get_exluded_command()

        if pkg.install_type == pkg.InstallType.SOURCE_CODE and getattr(pkg, "branch", None):
            checkout(package_paths.source_folder, pkg.branch)

        print(f"<CI INFO>: Generating RST files for {pkg.name}.")
        subpackages_rst_record = run_apidoc(package_paths.doc_folder, package_paths.source_folder,
                                            exclude_paths, pkg)

    print("<CI INFO>: Listing RST files:")
    for rst_file in os.listdir(package_paths.doc_folder):
        print(rst_file)

    print("<CI INFO>: Running Sphinx build...")
    generate_conf(pkg, package_paths.doc_folder, CONF_TEMPLATE_DIR)
    run_converter(package_paths.doc_folder, package_paths.yaml_output_folder)

    subpackages_path_record = {}
    if pkg.build_in_subpackage:
        subpackages_yaml_path = os.path.join(package_paths.yaml_output_folder, "subpackages")
        for (subpackage_name, subpackage_path) in subpackages_rst_record.items():
            subpackage_yaml_path = os.path.join(subpackages_yaml_path, subpackage_name)
            subpackages_path_record[subpackage_name] = subpackage_yaml_path
            run_converter(subpackage_path, subpackage_yaml_path)

        merge_subpackage_files(subpackages_path_record, package_paths.yaml_output_folder, pkg.name)
