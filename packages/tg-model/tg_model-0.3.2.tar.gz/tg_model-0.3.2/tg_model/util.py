# -*- coding: utf-8 -*-
# Copyright (C) 2023 TUD | ZIH
# ralf.klammer@tu-dresden.de

import logging

import os

from functools import reduce
from lxml.etree import QName
from os import getcwd, listdir, mkdir
from os.path import exists, isfile, join
from pathlib import Path


log = logging.getLogger(__name__)


def cli_startup(log_level=logging.INFO, log_file=None):
    log_config = dict(
        level=log_level,
        format="%(asctime)s %(name)-10s %(levelname)-4s %(message)s",
    )
    if log_file:
        log_config["filename"] = log_file

    logging.basicConfig(**log_config)
    logging.getLogger("").setLevel(log_level)


def get_files(path, as_tuple=False, file_ext="xml"):
    return [
        (path, file) if as_tuple else join(path, file)
        for file in listdir(path)
        if isfile("/".join([path, file]))
        and Path(file).suffix == ".%s" % file_ext
    ]


def add_directory(path):
    if not exists(path):
        mkdir(path)


def get_tag(elem):
    if elem is not None:
        tag = QName(elem)
        return tag.localname


def get_type(*args, **kw):
    log.info('Deprecated function "get_type')
    return get_tag(*args, **kw)


def get_unique_node_id(node):
    # build a kind of id
    return "_".join(
        [node.tag] + ["_".join(list(item)) for item in node.items()]
    )


def build_xpath(elem, xpath="", include_items=False):
    xpath += "/" + get_type(elem)
    if include_items:
        for item in elem.items():
            xpath += '[@%s="%s"]' % item
    return xpath


def prepare_path(path, create=False, subpath=None):
    log.debug("prepare_path: %s subpath: %s" % (path, subpath))
    if subpath:
        path = "/".join([path, subpath])

    if path.endswith("/"):
        path = path[:-1]
    if path.startswith("./"):
        path = path.replace(".", getcwd())
    elif not path.startswith("/"):
        path = "/".join([getcwd(), path])
    path = path.replace("//", "/")
    if create and not exists(path):
        parts = path.split("/")

        for i in range(len(parts)):
            if not parts[i]:
                continue
            subpath = "/".join(parts[0 : i + 1])
            log.debug("exists %s: %s" % (subpath, exists(subpath)))
            if not exists(subpath):
                log.debug("mkdir %s" % subpath)
                mkdir(subpath)
    return path


def check_outpath(out):
    log.info("Deprecated: `check_outpath`")
    parts = prepare_path(out).split("/")
    for i in range(len(parts)):
        if not parts[i]:
            continue
        subpath = "/".join(parts[0 : i + 1])
        log.debug("exists %s: %s" % (subpath, exists(subpath)))
        if not exists(subpath):
            log.debug("mkdir %s" % subpath)
            mkdir(subpath)
    return out


def split_xpath(xpath):
    result = {
        "xpath": xpath,
        "full_path": xpath,
        # rvalue ~= return value
        "rvalue": "text",
        # akey ~= additional key
        "akey": None,
    }
    if xpath.find("^") != -1 and xpath.find("~") == -1:
        result["xpath"], result["rvalue"] = xpath.split("^")
    elif xpath.find("^") == -1 and xpath.find("~") != -1:
        result["xpath"], result["akey"] = xpath.split("~")
    elif xpath.find("^") == -1 and xpath.find("~") != -1:
        # ToDO
        log.error("Currently not able to handle both steering commands!")
    return result


# source of that nice function: https://stackoverflow.com/a/47969823/3756733
def deref_multi(data, keys):
    return reduce(lambda d, key: d[key], keys, data)


def find_tei_directory(path, tei_directory, depth):
    log.debug("***find_tei_directory***")
    log.debug((path, tei_directory, depth))
    subpaths = []
    # create list containing only subpaths of "current" path
    dirlist = [
        d for d in os.listdir(path) if os.path.isdir("%s/%s" % (path, d))
    ]
    for subpath in dirlist:
        fullpath = "%s/%s" % (path, subpath)
        # append path if:
        #   - found a path having the same name as he given 'tei_directory' AND
        #   - it has xml-files inside
        if subpath == tei_directory and len(
            get_files(fullpath, file_ext="xml")
        ):
            subpaths.append(fullpath)
            break
        else:
            subpaths += find_tei_directory(fullpath, tei_directory, depth + 1)
    return subpaths
