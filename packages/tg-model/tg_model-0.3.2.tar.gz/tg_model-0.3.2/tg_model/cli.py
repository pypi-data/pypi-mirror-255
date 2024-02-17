# -*- coding: utf-8 -*-
# Copyright (C) 2023 TUD | ZIH
# ralf.klammer@tu-dresden.de

import logging

import click
import os

from pprint import pprint

from .collection import CollectionModeler
from .util import cli_startup, prepare_path
from .tei import SynergyAnalyzer
from .yaml import (
    MainConfig,
    MainConfigTemplate,
    SynergyConfigTemplate,
    CollectionConfigTemplate,
)

log = logging.getLogger(__name__)


def _init_ctx(ctx, debug, **kw):
    cli_startup(log_level=debug and logging.DEBUG or logging.INFO)
    ctx.ensure_object(dict)
    ctx.obj["DEBUG"] = debug

    log.info("Projectname: %s" % kw["projectname"])

    kw["basepath"] = prepare_path(kw["basepath"])
    log.info("General projects path: %s" % kw["basepath"])

    kw["projectpath"] = prepare_path(
        "{basepath}/{projectname}".format(**kw), create=True
    )
    log.info("Project path: %s" % kw["projectpath"])

    if "inputpath" in kw:
        kw["inputpath"] = prepare_path(
            kw["inputpath"].format(**kw), create=True
        )
        log.info("Input path: %s" % kw["inputpath"])

    ctx.obj.update(kw)


@click.group()
@click.option("--debug/--no-debug", "-d", is_flag=True, default=False)
@click.option("--projectname", "-n", required=True, help="name of project")
@click.option(
    "--basepath",
    "-b",
    default="./projects",
    help="basic path for all projects",
)
@click.pass_context
def tg_model(ctx, **kw):
    """
    This is an approach on building a fluffy "datamodel" for a TextGrid-ingest
    """
    _init_ctx(ctx, **kw)


@tg_model.command()
@click.pass_context
@click.option("--templates", help="path to individual templates")
def build_collection(ctx, templates=None, **kw):
    mc = MainConfig(ctx.obj["projectpath"])
    for subproject in mc.content["subprojects"]:
        em = CollectionModeler(
            subproject, ctx.obj["projectpath"], templates=templates
        )
        em.render_collection()
    pass


@click.group()
@click.option("--debug/--no-debug", "-d", is_flag=True, default=False)
@click.option("--projectname", "-n", required=True, help="path to project")
@click.option(
    "--basepath",
    "-b",
    default="./projects",
    help="path to project",
    show_default=True,
)
@click.option(
    "--outputpath",
    "-o",
    help="path to the final outputs | defaults to subpath of input within projectsfolder",
)
@click.pass_context
def tg_configs(ctx, **kw):
    _init_ctx(ctx, **kw)


def _main(ctx, **kw):
    kw.update(ctx.obj)
    MainConfigTemplate(ctx.obj["projectpath"]).render(**kw)

    log.info("*" * 50)
    log.info("%s/main.yaml initialized!" % ctx.obj["projectpath"])
    log.info("*" * 50)

    request = MainConfig(ctx.obj["projectpath"]).validate()
    if request:
        log.warn("###Validation failed###")
        for r in request:
            log.warn(r)


@tg_configs.command()
@click.pass_context
@click.option(
    "--inputpath",
    "-i",
    help="Path(-s) to directory containing TEI-documents, can be one or multiple (separated by `,`)",
)
@tg_configs.command()
@click.pass_context
@click.option(
    "--sourcepath",
    "-s",
    help="This is the basic path of the data source.",
)
@click.option(
    "--tei_directory",
    "-t",
    default="tei",
    help="This is the name of the directory where the TEI documents are located. (default='tei')",
)
def main(ctx, **kw):
    """
    Creating main config and subproject directories

    You have 2 options:
    Either you set the concrete path ("inputpath") to one or more
    (comma separated) directories containing TEI documents.
    Or you set the "sourcepath" and the name of the directory
    ("tei_directory"), where the TEI documents are located. And the concrete
    path will be analysed automatically!
    """
    _main(ctx, **kw)


def _synergy(ctx, synergy_analyzer, subproject):
    SynergyConfigTemplate(
        synergy_analyzer,
        projectpath=ctx.obj["projectpath"],
        subproject=subproject,
    ).render()


@tg_configs.command()
@click.pass_context
def synergy(ctx):
    mc = MainConfig(ctx.obj["projectpath"])
    log.info("*" * 50)
    for subproject in mc.content["subprojects"]:
        synergy_analyzer = SynergyAnalyzer(subproject, ctx.obj["projectpath"])
        _synergy(ctx, synergy_analyzer, subproject)
    log.info(
        "Edit it/them and run 'prepare-config -ct collection' afterwards."
    )
    log.info("*" * 50)


def _collection(ctx, synergy_analyzer, subproject, overwrite):
    CollectionConfigTemplate(
        synergy_analyzer,
        projectpath=ctx.obj["projectpath"],
        subproject=subproject,
    ).render(overwrite=overwrite)


@tg_configs.command()
@click.pass_context
@click.option(
    "--overwrite", "-o", is_flag=True, help="Overwrite already defined values."
)
def collection(ctx, overwrite):
    mc = MainConfig(ctx.obj["projectpath"])
    log.info("*" * 50)
    for subproject in mc.content["subprojects"]:
        synergy_analyzer = SynergyAnalyzer(
            subproject, projectpath=ctx.obj["projectpath"]
        )
        _collection(ctx, synergy_analyzer, subproject, overwrite)
    log.info("Edit it/them and run 'tg_model build-collection' afterwards")
    log.info("*" * 50)


@tg_configs.command()
@click.pass_context
@click.option(
    "--inputpath",
    "-i",
    help="Path(-s) to directory containing TEI-documents, can be one or multiple (separated by `,`)",
)
@click.option(
    "--sourcepath",
    "-s",
    help="This is the basic path of the data source.",
)
@click.option(
    "--tei_directory",
    "-t",
    default="tei",
    help="This is the name of the directory where the TEI documents are located. (default='tei')",
)
@click.option("--overwrite", "-o", is_flag=True)
def all(ctx, overwrite, **kw):
    """
    Creating all configs and subproject directories at once

    You have 2 options:
    Either you set the concrete path ("inputpath") to one or more
    (comma separated) directories containing TEI documents.
    Or you set the "sourcepath" and the name of the directory
    ("tei_directory"), where the TEI documents are located. And the concrete
    path will be analysed automatically!
    """
    _main(ctx, **kw)
    mc = MainConfig(ctx.obj["projectpath"])
    for subproject in mc.content["subprojects"]:
        synergy_analyzer = SynergyAnalyzer(
            subproject, projectpath=ctx.obj["projectpath"]
        )
        _synergy(ctx, synergy_analyzer, subproject)
        _collection(ctx, synergy_analyzer, subproject, overwrite)


@click.group()
@click.option("--debug/--no-debug", "-d", is_flag=True, default=False)
@click.option("--projectname", "-n", required=True, help="path to project")
@click.option(
    "--basepath",
    "-b",
    default="./projects",
    help="path to project",
    show_default=True,
)
@click.option(
    "--outputpath",
    "-o",
    help="path to the final outputs | defaults to subpath of input within projectsfolder",
)
@click.pass_context
def tg_synergy(ctx, **kw):
    """
    This is an approach on building a fluffy "datamodel" for a TextGrid-ingest
    """
    _init_ctx(ctx, **kw)


@tg_synergy.command()
@click.pass_context
def synergetic_nodes(ctx, **kw):
    mc = MainConfig(ctx.obj["projectpath"])
    for subproject in mc.content["subprojects"]:
        pprint(
            SynergyAnalyzer(
                subproject, projectpath=ctx.obj["projectpath"]
            ).synergetic_nodes
        )


@tg_synergy.command()
@click.pass_context
def node_relations(ctx, **kw):
    mc = MainConfig(ctx.obj["projectpath"])
    for subproject in mc.content["subprojects"]:
        pprint(
            SynergyAnalyzer(
                subproject, projectpath=ctx.obj["projectpath"]
            ).node_relations
        )


@tg_synergy.command()
@click.option("--output", "-o")
@click.pass_context
def run(ctx, output=None, **kw):
    mc = MainConfig(ctx.obj["projectpath"])
    for subproject in mc.content["subprojects"]:
        tei_analyzer = SynergyAnalyzer(
            subproject, projectpath=ctx.obj["projectpath"]
        )
        if output:
            tei_analyzer.write_tree(output)
        else:
            tei_analyzer.print_tree()


if __name__ == "__main__":
    main(obj={})
