# -*- coding: utf-8 -*-
#
# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from copy import deepcopy
import os
import re

import yaml as yml
from sphinx.util import ensuredir
from yaml import safe_dump as dump
from settings import API_ROOT

import common
from convert_class import convert_class
from convert_enum import convert_enum
from convert_module import convert_module
from convert_package import convert_package

INITPY = '__init__.py'
MODULE = 'module'
scientific_notation_regex = re.compile(r'^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)$')

def string_representer(dumper, data):
    return dumper.represent_scalar(u"tag:yaml.org,2002:str", data,
                                   style="'" if (scientific_notation_regex.match(data)) else None)
yml.add_representer(str, string_representer)

def build_finished(app, exception):
    """
    Output YAML on the file system.
    """
    def find_node_in_toc_tree(toc_yaml, to_add_node):
        for module in toc_yaml:
            if module['name'] == to_add_node:
                return module

            if 'items' in module:
                items = module['items']
                found_module = find_node_in_toc_tree(items, to_add_node)
                if found_module != None:
                    return found_module

        return None

    def convert_class_to_enum_if_needed(obj):
        if (obj.get('inheritance'), None):
            children = obj.get('inheritance', None)
            inheritanceLines = []
            for child in children:
                iLine = []
                if child.get('inheritance', None) and child['inheritance'][0].get('type', None):
                    iLine.append(child['inheritance'][0]['type'])
                if child.get('type', None):
                    iLine.append(child['type'])
                inheritanceLines.append(iLine)
            if inheritanceLines:
                for iLine in inheritanceLines:
                    for inheritance in iLine:
                        if inheritance.find('enum.Enum') > -1:
                            obj['type'] = 'enum'
                            app.env.docfx_info_uid_types[obj['uid']] = 'enum'
                            return

    def merge_params(arg_params, doc_params):
        merged_params = deepcopy(doc_params)
        # merge arg_params into merged_params
        for arg_param in arg_params:
            for merged_param in merged_params:
                if arg_param['id'] == merged_param['id']:
                    if "defaultValue" in arg_param.keys():
                        merged_param["defaultValue"] = arg_param["defaultValue"]
                    if "type" in arg_param.keys():
                        merged_param["type"] = arg_param["type"]
                    if "isRequired" in arg_param.keys():
                        if  arg_param["isRequired"] == False:
                            merged_param["isRequired"] = arg_param["isRequired"]
                    break
            else:
                merged_params.append(arg_param)
        return merged_params

    def remove_params_without_id(params):
        new_params = []
        for param in params:
            if 'id' in param:
                new_params.append(param)
        return new_params

    normalized_outdir = os.path.normpath(os.path.join(
        app.builder.outdir,  # Output Directory for Builder
        API_ROOT
    ))

    def add_isrequired_if_needed(obj, key: str):
        if key in obj['syntax'] and obj['type'] == 'method':
            for args in obj['syntax'][key]:
                if 'isRequired' not in args and 'defaultValue' not in args:
                    args['isRequired'] = True
    

    ensuredir(normalized_outdir)

    toc_yaml = []
    # Used to record filenames dumped to avoid confliction
    # caused by Windows case insensitive file system
    file_name_set = set()

    # Order matters here, we need modules before lower level classes,
    # so that we can make sure to inject the TOC properly
    # put app.env.docfx_yaml_packages after app.env.docfx_yaml_modules to keep same TOC items order
    for data_set in (app.env.docfx_yaml_modules,
                     app.env.docfx_yaml_packages,
                     app.env.docfx_yaml_classes,
                     app.env.docfx_yaml_functions):  # noqa

        for uid, yaml_data in iter(sorted(data_set.items())):
            if not uid:
                # Skip objects without a module
                continue

            references = []
            # Merge module data with class data
            for obj in yaml_data:
                arg_params = obj.get('syntax', {}).get('parameters', [])
                if(len(arg_params) > 0 and 'id' in arg_params[0]):
                    if (arg_params[0]['id'] == 'self') or (obj['type'] in ['class', 'method'] and arg_params[0]['id'] == 'cls'):
                        # Support having `self` as an arg param, but not documented
                        # Not document 'cls' of constuctors and class methods too
                        arg_params = arg_params[1:]
                        obj['syntax']['parameters'] = arg_params
                if obj['uid'] in app.env.docfx_info_field_data and \
                        obj['type'] == app.env.docfx_info_field_data[obj['uid']]['type']:
                    # Avoid entities with same uid and diff type.
                    # Delete `type` temporarily
                    del(app.env.docfx_info_field_data[obj['uid']]['type'])
                    if 'syntax' not in obj:
                        obj['syntax'] = {}
                    merged_params = []
                    merged_kwargs = []
                    if 'parameters' in app.env.docfx_info_field_data[obj['uid']]:
                        doc_params = app.env.docfx_info_field_data[obj['uid']].get(
                            'parameters', [])
                        if arg_params and doc_params:
                            if len(arg_params) - len(doc_params) > 0:
                                print("Documented params don't match size of params:"" {}".format(obj['uid']))   # lgtm [py/clear-text-logging-sensitive-data]
                            doc_params = remove_params_without_id(doc_params)
                            merged_params = merge_params(arg_params, doc_params)
                    else:
                        merged_params = arg_params

                    if 'keywordOnlyArguments' in app.env.docfx_info_field_data[obj['uid']]:
                        kwargs_from_inspect = obj.get('syntax', {}).get('keywordOnlyArguments', [])
                        kwargs_from_doc = app.env.docfx_info_field_data[obj['uid']].get('keywordOnlyArguments', [])
                        if kwargs_from_inspect and kwargs_from_doc:
                            merged_kwargs = merge_params(kwargs_from_inspect, kwargs_from_doc)

                    obj['syntax'].update(
                        app.env.docfx_info_field_data[obj['uid']])

                    # Merging parameters and keywordOnlyArguments is required,
                    # becasue parameters and keywordOnlyArguments can be in both signature and docstring
                    # For positionalOnlyArguments, it's not required, because it's only in signature so far
                    if merged_params:
                        obj['syntax']['parameters'] = merged_params
                    if merged_kwargs:
                        obj['syntax']['keywordOnlyArguments'] = merged_kwargs

                    add_isrequired_if_needed(obj, 'parameters')
                    add_isrequired_if_needed(obj, 'keywordOnlyArguments')
                    add_isrequired_if_needed(obj, 'positionalOnlyArguments')

                    # Raise up summary
                    if 'summary' in obj['syntax'] and obj['syntax']['summary']:
                        obj['summary'] = obj['syntax'].pop(
                            'summary').strip(" \n\r\r")

                    # Raise up remarks
                    if 'remarks' in obj['syntax'] and obj['syntax']['remarks']:
                        obj['remarks'] = obj['syntax'].pop('remarks')

                    # Raise up seealso
                    if 'seealso' in obj['syntax'] and obj['syntax']['seealso']:
                        obj['seealsoContent'] = obj['syntax'].pop('seealso')

                    # Raise up example
                    if 'example' in obj['syntax'] and obj['syntax']['example']:
                        obj.setdefault('example', []).append(
                            obj['syntax'].pop('example'))

                    # Raise up exceptions
                    if 'exceptions' in obj['syntax'] and obj['syntax']['exceptions']:
                        obj['exceptions'] = obj['syntax'].pop('exceptions')

                    # Raise up references
                    if 'references' in obj['syntax'] and obj['syntax']['references']:
                        obj.setdefault('references', []).extend(
                            obj['syntax'].pop('references'))

                    # add content of temp list 'added_attribute' to children and yaml_data
                    if 'added_attribute' in obj['syntax'] and obj['syntax']['added_attribute']:
                        added_attribute = obj['syntax'].pop('added_attribute')
                        # TODO: yaml_data is updated wihle iterated. 
                        # `added_attribute` items are copied from class api's `obj` to `yaml_data`
                        # Then iterate again
                        # Should iterate uid and merge yaml_data, added_attribute
                        for attrData in added_attribute:
                            existed_Data = next(
                                (n for n in yaml_data if n['uid'] == attrData['uid']), None)
                            if existed_Data:
                                # Update data for already existed one which has attribute comment in source file
                                existed_Data.update(attrData)
                            else:
                                obj.get('children', []).append(attrData['uid'])
                                yaml_data.append(attrData)
                    # Revert `type` for other objects to use
                    app.env.docfx_info_field_data[obj['uid']
                                                  ]['type'] = obj['type']

                if 'references' in obj:
                    # Ensure that references have no duplicate ref
                    ref_uids = [r['uid'] for r in references]
                    for ref_obj in obj['references']:
                        if ref_obj['uid'] not in ref_uids:
                            references.append(ref_obj)
                    obj.pop('references')

                # To distinguish distribution package and import package
                if obj.get('type', '') == 'package' and obj.get('kind', '') != 'distribution':
                    obj['kind'] = 'import'

                if (obj['type'] == 'class' and obj['inheritance']):
                    convert_class_to_enum_if_needed(obj)

            # Build nested TOC
            if uid.count('.') >= 1:
                parent_level = '.'.join(uid.split('.')[:-1])
                found_node = find_node_in_toc_tree(toc_yaml, parent_level)

                if found_node:
                    found_node.pop('uid', 'No uid found')
                    found_node.setdefault('items', [{'name': 'Overview', 'uid': parent_level}]).append(
                        {'name': uid, 'uid': uid})
                else:
                    toc_yaml.append({'name': uid, 'uid': uid})

            else:
                toc_yaml.append({'name': uid, 'uid': uid})

    for data_set in (app.env.docfx_yaml_packages,
                     app.env.docfx_yaml_modules,
                     app.env.docfx_yaml_classes,
                     app.env.docfx_yaml_functions):  # noqa

        for uid, yaml_data in iter(sorted(data_set.items())):
            # Output file
            if uid.lower() in file_name_set:
                filename = uid + "(%s)" % app.env.docfx_info_uid_types[uid]
            else:
                filename = uid
            out_file = os.path.join(normalized_outdir, '%s.yml' % filename)
            ensuredir(os.path.dirname(out_file))
            new_object = {}

            transformed_obj = None
            if yaml_data[0]['type'] == 'package':
                transformed_obj = convert_package(
                    yaml_data, app.env.docfx_info_uid_types)
                mime = "PythonPackage"
            elif yaml_data[0].get('type', None) == 'class':
                transformed_obj = convert_class(yaml_data)
                mime = "PythonClass"
            elif yaml_data[0].get('type', None) == 'enum':
                transformed_obj = convert_enum(yaml_data)
                mime = "PythonEnum"
            else:
                transformed_obj = convert_module(
                    yaml_data, app.env.docfx_info_uid_types)
                mime = "PythonModule"

            if transformed_obj == None:
                print("Unknown yml: " + yamlfile_path)
            else:
                # save file
                common.write_yaml(transformed_obj, out_file, mime)
                file_name_set.add(filename)

    if len(toc_yaml) == 0:
        raise RuntimeError("No documentation for this module.")

    toc_file = os.path.join(normalized_outdir, 'toc.yml')
    with open(toc_file, 'w') as writable:
        writable.write(
            dump(
                [{
                    'name': app.config.project,
                    'items': [{'name': 'Overview', 'uid': 'project-' + app.config.project}] + toc_yaml
                }],
                default_flow_style=False,
            )
        )

    index_file = os.path.join(normalized_outdir, 'index.yml')
    index_children = []
    index_references = []
    for item in toc_yaml:
        index_children.append(item.get('name', ''))
        index_references.append({
            'uid': item.get('name', ''),
            'name': item.get('name', ''),
            'fullname': item.get('name', ''),
            'isExternal': False
        })

    index_obj = [{
        'uid': 'project-' + app.config.project,
        'name': app.config.project,
        'fullName': app.config.project,
        'langs': ['python'],
        'type': 'package',
        'kind': 'distribution',
        'summary': '',
        'children': index_children
    }]
    transformed_obj = convert_package(index_obj, app.env.docfx_info_uid_types)
    mime = "PythonPackage"
    if transformed_obj == None:
        print("Unknown yml: " + yamlfile_path)
    else:
        # save file
        common.write_yaml(transformed_obj, index_file, mime)
        file_name_set.add(filename)
