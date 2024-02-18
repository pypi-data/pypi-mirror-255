# -*- coding: utf-8 -*-
# Copyright (C) 2023 TUD | ZIH
# ralf.klammer@tu-dresden.de

import logging

from yaml import full_load as load_yaml
from pkgutil import get_data
from os import listdir, path
from pyaml import dump as dump_yaml

from .util import (
    split_xpath,
    exists,
    prepare_path,
    get_files,
    deref_multi,
    find_tei_directory,
)


log = logging.getLogger(__name__)


class CollectionMixin(object):
    @property
    def collection(self):
        return self.content["collection"]

    @property
    def elements(self):
        return self.collection["elements"]

    @property
    def sorted_elements(self):
        return sorted(self.elements, key=lambda x: (x["filename"]))

    @property
    def rights_holder(self):
        return self.collection["rights_holder"]

    def rights_holder_lastname(self, value=None):
        if value:
            self.rights_holder["lastname"] = value
        return self.rights_holder["lastname"]

    def rights_holder_firstname(self, value=None):
        if value:
            self.rights_holder["firstname"] = value
        return self.rights_holder["firstname"]

    def rights_holder_fullname(self, value=None):
        if value:
            self.rights_holder["fullname"] = value
        return self.rights_holder["fullname"]

    def rights_holder_url(self, value=None):
        if value:
            self.rights_holder["url"] = value
        return self.rights_holder["url"]

    @property
    def title(self):
        return self.collection["title"]

    def short_title(self, value=None):
        if value:
            self.title["short"] = value
        return self.title["short"]

    def long_title(self, value=None):
        if value:
            self.title["long"] = value
        return self.title["long"]


class YAMLConfigBase(object):
    def __init__(
        self, filename, projectpath=None, subproject=None, *args, **kw
    ):
        self.filename = filename
        self.projectpath = projectpath
        self.subproject = subproject
        if subproject:
            self.path = "%s/%s" % (subproject["basepath"], filename)
        else:
            self.path = "%s/%s" % (projectpath, filename)
        self._content = False

    @property
    def content(self):
        if self._content is False:
            self._content = None
            _data = self.get_data()
            if _data:
                self._content = load_yaml(_data)
        return self._content

    def get_data(self):
        if exists(self.path):
            with open(self.path, "rb") as file:
                return file.read()
        else:
            log.error("%s does not exist!" % self.path)

    def _get(self, key, _dict=None):
        _dict = self.content if _dict is None else _dict
        if key not in _dict:
            return None
        else:
            value = _dict[key]
            log.debug("[_get] value: %s | key: %s" % (value, key))
            return value if value else {}

    def get(self, key, section=None, default=None):
        section_name = section
        section = None
        if section_name:
            section = self._get(section_name)
            if section is None:
                log.error(
                    "Section_name: '%s' not found in %s"
                    % (section_name, self.path)
                )
        value = self._get(key, _dict=section)
        if value:
            return value
        else:
            log.error(
                "'%s' not found in section_name: %s (%s)"
                % (key, section_name, self.path)
            )
            return default


class MainConfig(YAMLConfigBase):
    def __init__(self, *args, **kw):
        super().__init__("main.yaml", *args, **kw)

    def validate(self):
        request = []
        # check if there are any files in the given inputpath
        for subproject in self.content["subprojects"]:
            if not get_files(subproject["inpath"]):
                request.append(
                    "No XML files found at: %s" % subproject["inpath"]
                )
        return request

    @property
    def min_hitrate(self):
        return self.get("min_hitrate", section="proposals", default=50)

    def set_subproject_stats(self):
        for subproject in self.content["subprojects"]:
            files = [
                f
                for f in listdir(subproject["inpath"])
                if not path.isdir("%s/%s" % (subproject["inpath"], f))
            ]
            subproject["stats"] = {"files": len(files)}


class SynergyConfig(YAMLConfigBase):
    def __init__(self, *args, **kw):
        super().__init__("synergy.yaml", *args, **kw)

    @property
    def filepath(self):
        return self.content["filepath"]


class CollectionConfig(YAMLConfigBase, CollectionMixin):
    def __init__(self, *args, **kw):
        super().__init__("collection.yaml", *args, **kw)
        self._obligatory = None
        self._eltec_specs = None

    def save(self):
        if not self.filename:
            raise Exception("No filename given for YAMLConfigTemplate!")
        with open(self.path, "w") as file:
            file.write(dump_yaml(self.content))

    @property
    def obligatory(self):
        if self._obligatory is None:
            self._obligatory = self.content["collection"]["attributes"][
                "obligatory"
            ]
        return self._obligatory

    def get_missing_params(self):
        missing_params = []
        for k in ["short", "long"]:
            keys = ["collection", "title", k]
            if deref_multi(self.content, keys) is None:
                missing_params.append(".".join(keys))
        # for k in ["firstname", "fullname", "lastname", "url"]:
        #     keys = ["collection", "rights_holder", k]
        #     if deref_multi(self.content, keys) is None:
        #         missing_params.append(".".join(keys))
        return missing_params


class YAMLConfigTemplate(YAMLConfigBase):
    def __init__(self, filename, projectpath, subpath=None, *args, **kw):
        self.projectpath = prepare_path(projectpath, create=True)

        super().__init__(filename, self.projectpath, *args, **kw)

    def get_data(self):
        return get_data(__name__, "templates/%s" % self.filename)

    def save(self):
        if not self.filename:
            raise Exception("No filename given for YAMLConfigTemplate!")
        with open(self.path, "w") as file:
            file.write(dump_yaml(self.content))

    def process_proposals(
        self, attribs, compare_to="sources", orig_content=None
    ):
        main_config = MainConfig(self.projectpath)

        log.debug("Compare to: %s" % compare_to)
        for attrib in attribs:
            orig_attrib = None
            if orig_content:
                orig_attrib = orig_content.get(attrib)
            if attribs[attrib]:
                if "proposals" in attribs[attrib]:
                    # we pop out the 'proposals' and we want to remove them
                    # from the config eiterway
                    proposals = attribs[attrib].pop("proposals")
                    if not proposals:
                        continue

                    # check if the attribute is already defined in the existing
                    # config AND set this
                    # orig_content is None when 'overwrite' is requested
                    if orig_attrib and orig_attrib.get("xpath"):
                        attribs[attrib]["xpath"] = orig_attrib.get("xpath")
                        continue

                    # init some statistics
                    min_hitrate = main_config.min_hitrate  # in %
                    winner = None
                    for _xpath_prop in proposals:
                        xpath_prop = split_xpath(_xpath_prop)
                        log.debug("[process_proposals] %s" % xpath_prop)
                        if compare_to == "sources":
                            hitrate = self.synergy_analyzer.hits_in_sources(
                                xpath_prop["xpath"]
                            )
                            if hitrate > min_hitrate:
                                winner = xpath_prop["full_path"]
                                min_hitrate = hitrate
                        elif compare_to == "synergy":
                            # pass
                            if (
                                self.synergy_analyzer.parser.find(
                                    xpath_prop["xpath"]
                                )
                                is not None
                            ):
                                winner = xpath_prop["full_path"]
                    if winner is not None and "xpath" in attribs[attrib]:
                        log.debug(
                            "[process_proposals] And the winner is `%s` having \
%s percent hitrate"
                            % (winner, min_hitrate)
                        )
                        attribs[attrib]["xpath"] = winner
                else:
                    # ok...there are no proposals at this level
                    # but maybe at the next level, so let's do some
                    # recursion
                    self.process_proposals(
                        attribs[attrib],
                        compare_to=compare_to,
                        orig_content=orig_attrib,
                    )


class MainConfigTemplate(YAMLConfigTemplate):
    def __init__(self, *args, **kw):
        super().__init__("main.yaml", *args, **kw)

    def render(
        self, inputpath=None, sourcepath=None, tei_directory=None, **kw
    ):
        self.content["projectname"] = kw.get("projectpath")
        if not self.content["projectname"]:
            # ToDo: remove usage of 'projectname' completely!
            log.warn(
                "MainConfigTemplate.render - Deprecated usage of projectname"
            )
            self.content["projectname"] = kw.get("projectname")

        if sourcepath and tei_directory:
            tei_directories = find_tei_directory(sourcepath, tei_directory, 0)
        elif inputpath:
            tei_directories = inputpath.split(",")
        else:
            log.error("Neither 'sourcepath' nor 'inputpath' is defined!")
            raise ValueError

        log.debug("tei_directories: %s" % tei_directories)

        subprojects = []
        for p in tei_directories:
            prepared_path = prepare_path(p)
            splitted_pp = prepared_path.split("/")
            length = 3 if len(splitted_pp) >= 3 else len(splitted_pp)
            input_name = "_".join(splitted_pp[-length:])

            outpath = prepare_path(
                kw["outputpath"]
                if "outputpath" in kw and kw["outputpath"]
                else self.projectpath,
                subpath="/".join([input_name, "result"]),
                create=True,
            )

            basepath = prepare_path(
                self.projectpath,
                subpath=input_name,
                create=True,
            )

            subprojects.append(
                {
                    "inpath": prepared_path,
                    "name": input_name,
                    "outpath": outpath,
                    "basepath": basepath,
                }
            )

        self.content["subprojects"] = subprojects

        self.save()

        return MainConfig(self.content["projectname"])


class SynergyConfigTemplate(YAMLConfigTemplate):
    def __init__(self, synergy_analyzer, *args, **kw):
        self.synergy_analyzer = synergy_analyzer
        super().__init__("synergy.yaml", *args, **kw)

    def render(self):
        ca_parser = self.synergy_analyzer.parser
        ca_parser.set_config(self)

        self.process_proposals(
            self.content,
            compare_to="synergy",
        )

        self.content["filepath"] = self.synergy_analyzer.write_tree(
            "%s/synergy.xml" % self.subproject["basepath"]
        )
        self.save()
        log.info("%s initialized!" % self.path)


class CollectionConfigTemplate(YAMLConfigTemplate, CollectionMixin):
    def __init__(self, synergy_analyzer, *args, **kw):
        self.synergy_analyzer = synergy_analyzer
        super().__init__(
            "collection.yaml",
            *args,
            **kw,
        )

    def render(self, overwrite=False):
        cc = CollectionConfig(self.subproject["basepath"])
        syan_parser = self.synergy_analyzer.parser

        for key in [
            "rights_holder_lastname",
            "rights_holder_firstname",
            "rights_holder_fullname",
            "rights_holder_url",
            "short_title",
            "long_title",
        ]:
            new_value = getattr(syan_parser, key)
            old_value = getattr(cc, key)() if cc.content else None
            _func = getattr(self, key)
            _func(
                new_value
                if overwrite or old_value in [None, ""]
                else old_value
            )

        # set long and short title projectname...if they are still not set
        for key in [
            "short_title",
            "long_title",
        ]:
            _func = getattr(self, key)
            if not _func():
                _func(self.subproject["name"])

        for t in self.synergy_analyzer.targets:
            self.elements.append({"fullpath": t.uri, "filename": t.file_name})

        self.process_proposals(
            self.collection["attributes"]["obligatory"],
            orig_content=None
            if overwrite or not cc.content
            else cc.collection["attributes"]["obligatory"],
        )

        self.save()

        log.info("%s initialized!" % self.path)
