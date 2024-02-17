# -*- coding: utf-8 -*-
# Copyright (C) 2023 TUD | ZIH
# ralf.klammer@tu-dresden.de

import logging
import os

from copy import deepcopy
from iso639 import Lang
from iso639.exceptions import InvalidLanguageValue
from lxml.etree import (
    Comment,
    dump,
    ElementTree,
    tostring,
    SubElement,
)

from .util import (
    get_tag,
    get_type,
    get_unique_node_id,
    build_xpath,
    get_files,
    split_xpath,
    prepare_path,
)
from .util_eltec import (
    date_to_timeslot,
    gender_to_authorgender,
    wordcount_to_size,
)
from .xml import XMLParserBase
from .yaml import SynergyConfig, CollectionConfig, MainConfig

log = logging.getLogger(__name__)


class TEIParser(XMLParserBase):
    def __init__(
        self,
        tree=None,
        path=None,
        filename=None,
        fullpath=None,
        *args,
        **kw,
    ):
        if tree is not None:
            super().__init__(tree=tree, *args, **kw)
        elif fullpath:
            super().__init__(fullpath, *args, **kw)
        elif all([path, filename]):
            self.path = path
            self.filename = filename
            super().__init__(os.path.join(path, filename), *args, **kw)
        else:
            raise ValueError("TEIParser incorrect initialized")

        self._pure_filename = None
        self._publication = None
        self._pub_place = None
        self._pub_date = None
        self._author = None
        self._author_id = None
        self._author_firstname = None
        self._author_lastname = None
        self._author_fullname = None
        self._title = None
        self._header = None
        self._desc_elements = None
        self._language = None
        self._author_gender = None
        self._genre = None
        self._wordcount = None
        self._eltec_time_slot = None
        self._eltec_author_gender = None
        self._eltec_size = None
        self._eltec_reprint_count = None
        self._as_dict = None

    def __repr__(self):
        return "<TEIParser: %s>" % self.uri

    def get_via_config_value(self, value, section):
        config_val = section.get(value, None)
        result = ""
        # if value == "author_gender":
        #     breakpoint()
        if config_val and config_val["xpath"]:
            xpath = split_xpath(config_val["xpath"])
            node = self.find(xpath["xpath"])
            if node is not None:
                if xpath["rvalue"] == "text":
                    result = node.text
                else:
                    result = node.get(xpath["rvalue"])

                if xpath["akey"] and node.get(xpath["akey"]):
                    result = ":".join([node.get(xpath["akey"]), result])

            else:
                log.warn("Nothing found for %s in %s!" % (config_val, self))
        return result

    def set_config(self, config):
        self._config = config

    @property
    def config(self):
        if self._config is None:
            self.set_config(CollectionConfig())
        return self._config

    @property
    def pure_filename(self):
        if self.filename and self._pure_filename is None:
            self._pure_filename = self.filename.replace(".xml", "")
        return self._pure_filename

    @property
    def header(self):
        if self._header is None:
            self._header = self.find(".//teiHeader")
        return self._header

    @property
    def desc_elements(self):
        if self._desc_elements is None:
            self._desc_elements = []
            for desc_element in self.header.iterchildren():
                self._desc_elements.append(get_tag(desc_element))
        return self._desc_elements

    @property
    def pub_date(self):
        if self._pub_date is None:
            self._pub_date = self.get_via_config_value(
                "date", self.config.obligatory["publication"]
            )
        return self._pub_date

    @property
    def pub_place(self):
        if self._pub_place is None:
            self._pub_place = self.get_via_config_value(
                "place", self.config.obligatory["publication"]
            )
        return self._pub_place

    @property
    def title(self):
        if self._title is None:
            self._title = self.get_via_config_value(
                "title", self.config.obligatory
            )
        return self._title

    @property
    def language(self):
        if self._language is None:
            self._language = self.get_via_config_value(
                "language", self.config.obligatory
            )
            if self._language:
                self._language = self._language.split("-")[0]
                try:
                    self._language = Lang(self._language).pt3
                except InvalidLanguageValue as e:
                    log.warn(e)
                    log.warn("Did not set language for %s" % self)

        return self._language

    @property
    def author_id(self):
        if self._author_id is None:
            self._author_id = self.get_via_config_value(
                "id", self.config.obligatory["author"]
            )
        return self._author_id

    @property
    def author_fullname(self, *args):
        if self._author_fullname is None:
            self._author_fullname = self.get_via_config_value(
                "fullname", self.config.obligatory["author"]
            )
            names = [self.author_firstname, self.author_lastname]
            if all(names):
                self._author_fullname = " ".join(names)
        return self._author_fullname

    @property
    def author_firstname(self):
        if self._author_firstname is None:
            self._author_firstname = self.get_via_config_value(
                "firstname", self.config.obligatory["author"]
            )
        return self._author_firstname

    @property
    def author_lastname(self):
        if self._author_lastname is None:
            self._author_lastname = self.get_via_config_value(
                "lastname", self.config.obligatory["author"]
            )
        return self._author_lastname

    @property
    def author_gender(self):
        if self._author_gender is None:
            self._author_gender = self.get_via_config_value(
                "gender", self.config.obligatory["author"]
            )
        return self._author_gender

    @property
    def genre(self):
        # NOTE: This opens up a wider field, than it seems
        # Especially, as there is no clear definition/vocabulary on how 'genre'
        # needs to be described
        if self._genre is None:
            genre_node = self.find(".//term[@type='text.form']")
            if genre_node is None:
                log.warn("Genre node not found in %s!" % self)
                self._genre = ""
            else:
                self._genre = genre_node.text
        return self._genre

    @property
    def wordcount(self):
        if self._wordcount is None:
            self._wordcount = self.get_via_config_value(
                "wordcount", self.config.obligatory
            )
        return self._wordcount

    # **********
    # ELTeC specs
    @property
    def eltec_time_slot(self):
        if self._eltec_time_slot is None:
            self._eltec_time_slot = date_to_timeslot(self.pub_date)
        return self._eltec_time_slot

    @property
    def eltec_author_gender(self):
        if self._eltec_author_gender is None:
            # idea is to try to get parameter directly from xpath value
            self._eltec_author_gender = self.get_via_config_value(
                "author_gender", self.config.obligatory["eltec_specs"]
            )
            # breakpoint()
            # and only 'generate' it, if it has not been found
            if not self._eltec_author_gender:
                self._eltec_author_gender = gender_to_authorgender(
                    self.author_gender
                )
        return self._eltec_author_gender

    @property
    def eltec_size(self):
        if self._eltec_size is None:
            # idea is to try to get parameter directly from xpath value
            self._eltec_size = self.get_via_config_value(
                "size", self.config.obligatory["eltec_specs"]
            )
            # and only 'generate' it, if it has not been found
            if not self._eltec_size:
                self._eltec_size = wordcount_to_size(self.wordcount)
        return self._eltec_size

    @property
    def eltec_reprint_count(self):
        if self._eltec_reprint_count is None:
            # idea is to try to get parameter directly from xpath value
            self._eltec_reprint_count = self.get_via_config_value(
                "reprint_count", self.config.obligatory["eltec_specs"]
            )
            # ToDo:
            #   find an alternative xpaths and build formatter
        return self._eltec_reprint_count

    # **********

    @property
    def as_dict(self):
        if self._as_dict is None:
            self._as_dict = {
                "id": self.pure_filename,
                "title": self.title,
                "author": {
                    "id": self.author_id,
                },
                "author_gender": self.author_gender,
                "author_name": self.author_fullname,
                "genre": self.genre,
                "language": self.language,
                "pub_date": self.pub_date,
                "pub_place": self.pub_place,
                "eltec": {
                    "time_slot": self.eltec_time_slot,
                    "gender": self.eltec_author_gender,
                    "size": self.eltec_size,
                    "reprint_count": self.eltec_reprint_count,
                },
            }
        return self._as_dict


class SynergyParser(TEIParser):
    def __init__(self, projectpath, *args, **kw):
        super().__init__(*args, **kw)
        self._principal = None
        self._rights_holder_url = None
        self._rights_holder_fullname = None
        self._rights_holder_firstname = None
        self._rights_holder_lastname = None
        self._short_title = None
        self._long_title = None
        self._as_dict = None
        self._config = None
        self.projectpath = projectpath

    @property
    def config(self):
        if self._config is None:
            self.set_config(SynergyConfig(self.projectpath))
        return self._config

    def get_via_config_value(self, value, section=None):
        config_val = self.config.get(value, section)
        result = ""
        if config_val and config_val["xpath"]:
            node = self.find(config_val["xpath"])
            if node is not None:
                result = node.text
        return result or None

    @property
    def short_title(self):
        if self._short_title is None:
            self._short_title = self.get_via_config_value("short", "title")
        return self._short_title

    @property
    def long_title(self):
        if self._long_title is None:
            self._long_title = self.get_via_config_value("long", "title")
        return self._long_title

    @property
    def rights_holder_url(self):
        if self._rights_holder_url is None:
            self._rights_holder_url = self.get_via_config_value(
                "url", "rights_holder"
            )
        return self._rights_holder_url

    @property
    def rights_holder_fullname(self):
        if self._rights_holder_fullname is None:
            names = [self.rights_holder_firstname, self.rights_holder_lastname]
            if all(names):
                self._rights_holder_fullname = " ".join(names)
            else:
                self._rights_holder_fullname = None
        return self._rights_holder_fullname

    @property
    def rights_holder_firstname(self):
        if self._rights_holder_firstname is None:
            self._rights_holder_firstname = self.get_via_config_value(
                "firstname", "rights_holder"
            )
        return self._rights_holder_firstname

    @property
    def rights_holder_lastname(self):
        if self._rights_holder_lastname is None:
            self._rights_holder_lastname = self.get_via_config_value(
                "lastname", "rights_holder"
            )
        return self._rights_holder_lastname

    @property
    def as_dict(self):
        if self._as_dict is None:
            self._as_dict = {
                "right_holder_url": self.rights_holder_url,
                "right_holder_forename": self.rights_holder_firstname,
                "right_holder_surname": self.rights_holder_lastname,
                "right_holder_name": self.rights_holder_fullname,
            }
        return self._as_dict


class SynergyAnalyzer(object):
    """
    This class helps to find completely synergetic nodes in a set of given
    TEI files.
    INPUT: list of file paths, e.g.: [./1.xml, 2.xml, /tmp/3.xml]
    OUTPUT: xml tree containing all synergetic nodes, e.g.:
        <TEI xmlns="http://www.tei-c.org/ns/1.0">
            <teiHeader>
                <fileDesc>
                    <titleStmt>
                        <principal>
                            <forename>John</forename>
                            <surname>Doe</surname>
                        </principal>
                    </titleStmt>
                </fileDesc>
            </teiHeader>
        </TEI>

    How it works (basically)!
    1. find synergies
        1.1 get all nodes (as xpath) from one (base) file
        1.2 check if each node exists in the other files
            (with same items & content)
            yes: keep node in list
            no: remove node from list
            --> list gets smaller after each checked file!
    2. recombinde synergetic nodes to xml tree structure
        2.1 find all parent nodes for each synergetic node
        2.2 find out which "parent" nodes have common childs
                --> "parent-child-relations"
        2.3 (re-)build tree structure from "parent-child-relations"
    """

    def __init__(
        self,
        subproject,
        projectpath,
        *args,
        **kw,
    ):
        self.subproject = subproject
        self.main_config = MainConfig(projectpath)

        self.sp_projectpath = self.subproject["basepath"]

        files = get_files(self.subproject["inpath"])
        self.files = sorted(files)
        if self.main_config.validate():
            raise LookupError(self.main_config.validate())
        self.base = TEIParser(fullpath=files[0])
        log.debug("This is the base: %s" % self.base)
        self.targets = [TEIParser(fullpath=target) for target in files[1:]]
        self._synergetic_nodes = None
        self._node_relations = None
        self._tree = None
        self._parser = None

    def _get_nodes(self, elem, exclude=[], xpath="./"):
        # this function iters through all nodes/childs of the 'teiHeader'
        # and collects them in a list
        log.debug("_get_nodes: elem=%s" % elem)
        if elem is None:
            elem = self.find(".//teiHeader")
        for child in elem.iterchildren():
            if child.tag is Comment or get_type(child) in exclude:
                continue
            if len(child.getchildren()):
                _xpath = build_xpath(child, xpath, include_items=True)
                self._get_nodes(
                    child,
                    exclude=exclude,
                    xpath=_xpath,
                )
            else:
                # v1.0 test it against base-file to check if the xpath is
                # well defined
                _xpath = build_xpath(child, xpath, include_items=True)
                found = self.base.findall(_xpath, text=child.text)
                if len(found) == 1:
                    self._synergetic_nodes.append(
                        {
                            "xpath": _xpath,
                            "content": child.text,
                        }
                    )
                else:
                    # TODO:
                    # Check cases and find a way to avoid it
                    # Known issues:
                    #   1: redundant elements without dedicated key-definitions
                    #       e.g.:
                    #           <respStmt>
                    #             <resp>Principal investigator</resp>
                    #             <name>Name1</name>
                    #           </respStmt>
                    #           <respStmt>
                    #             <resp>Encoding</resp>
                    #             <name>Name2</name>
                    #           </respStmt>
                    #   2: element specific namespace, e.g.:
                    #       <textDesc>
                    #            <authorGender xmlns="http://123" key="M"/>
                    #       </textDesc>
                    log.warn(
                        "%s is related to %s result(s)!" % (_xpath, len(found))
                    )
                    # breakpoint()

        return

    @property
    def synergetic_nodes(self):
        if self._synergetic_nodes is None:
            self._synergetic_nodes = []
            # 1.1 get all nodes from (base) file
            self._get_nodes(
                self.base.find(".//teiHeader"),  # only analyze 'teiHeader'
                exclude=["abstract", "listBibl"],  # exclude some nodes
            )
            # 1.2 try to find each node in the other files
            for target in self.targets:
                log.debug("Current target: %s" % target)
                for node in self._synergetic_nodes:
                    check = bool(
                        target.findall(node["xpath"], text=node["content"])
                    )
                    # remove node from list, if not found
                    if check is False:
                        self._synergetic_nodes.remove(node)
            log.debug("*" * 50)
            log.debug(
                "Found %i identical nodes." % len(self._synergetic_nodes)
            )
            log.debug("-" * 50)
            for node in self._synergetic_nodes:
                log.debug("%s: %s" % (node["xpath"], node["content"]))
            log.debug("*" * 50)
            self._synergetic_nodes

        return self._synergetic_nodes

    def _recursive_iter_parents(self, node):
        # this function iterates recursively through all parents of a node
        # (within the original tree structure of base file)
        # results in a list of parents of the initial node
        log.debug("'_recursive_iter_parents' -> node: %s" % node)
        # need to 'cache' the original node, as all childs will be removed
        # and therefore also this node will be removed from the tree
        root_parent = node.getparent()
        parent = None
        if not root_parent.tag.endswith("TEI"):
            parent = deepcopy(root_parent)
        log.debug("'_recursive_iter_parents' -> parent: %s" % parent)

        parents = []

        if parent is None:
            log.debug("'_recursive_iter_parents' -> ###end of recursion###")
        else:
            log.debug("'_recursive_iter_parents' -> ###next recursion###")
            parents.append(parent)
            # remove all childs of parent, to have the 'pure' parent node
            for c in parent.iterchildren():
                log.debug("'_recursive_iter_parents/remove_childs' -> %s" % c)
                parent.remove(c)
            # recursion, to get the parent of this parent
            sub_parents = self._recursive_iter_parents(root_parent)
            if sub_parents:
                parents += sub_parents
        return parents

    def _add_node_relations(self, nodes):
        # This function takes a list of nodes and maps them to a kind of
        # parent-child-structure
        # Assumption: one node is the "parent" of the following node
        for i in range(len(nodes)):
            node = nodes[i]
            this_node_key = get_unique_node_id(node)
            if this_node_key not in self._node_relations:
                self._node_relations[this_node_key] = {
                    "childs": {},
                    "node": node,
                }
            if i + 1 < len(nodes):
                child_node_key = get_unique_node_id(nodes[i + 1])
                if (
                    child_node_key
                    not in self._node_relations[this_node_key]["childs"]
                ):
                    self._node_relations[this_node_key]["childs"][
                        child_node_key
                    ] = nodes[i + 1]

    def _set_node_relations(self, node):
        # This functions buils up a global dictionary containing:
        #   all nodes and
        #   the corresponding childs
        # This step is necessary, as some nodes belong to the same upper node
        # (parent)
        parents = self._recursive_iter_parents(node)
        parents.insert(0, node)
        self._add_node_relations(parents[::-1])

    def _recombine_related_nodes(self):
        for rel in self.node_relations:
            node = self.node_relations[rel]["node"]
            childs = self.node_relations[rel]["childs"]
            for child_key in childs:
                child = childs[child_key]
                node.append(child)

    @property
    def node_relations(self):
        # "parent-child-relations"
        # find out which synergetic nodes belong to the same "parent" node
        # to enable build up
        if self._node_relations is None:
            self._node_relations = {}
            # check for synergetic nodes initially, if not already happened
            if self.synergetic_nodes is None:
                self.set_synergetic_nodes()
            # loop through all synergetic nodes to rebuild tree structure
            for node in self.synergetic_nodes:
                self._set_node_relations(self.base.find(node["xpath"]))
        return self._node_relations

    @property
    def tree(self):
        if self._tree is None:
            # we need to recombine the all nodes with their related "child"
            # nodes in order to get the full tree structure
            self._recombine_related_nodes()
            # afterwards we return the "base"-node to representing
            # the full structure
            base_tag = [*self.node_relations][0]
            self._tree = self.node_relations[base_tag]["node"]
        return self._tree

    def dump_tree(self):
        return tostring(
            self.tree, pretty_print=True, encoding="utf-8", with_tail=False
        )

    def print_tree(self):
        dump(self.tree)

    def write_tree(self, filename):
        self.add_files()
        ElementTree(self.tree).write(
            filename, pretty_print=True, xml_declaration=True, encoding="utf-8"
        )
        return filename

    def add_files(self):
        srcDesc = self.tree.find(".//sourceDesc")
        if srcDesc is None:
            srcDesc = SubElement(self.tree, "sourceDesc")
        for file in self.files:
            file_elem = SubElement(srcDesc, "file")
            file_elem.text = file
            file_elem.tail = "\n"

    @property
    def parser(self):
        if self._parser is None:
            self._parser = SynergyParser(self.sp_projectpath, tree=self.tree)
        return self._parser

    def parse(self):
        return self.parser.as_dict

    def hits_in_sources(self, xpath):
        all_sources = [self.base] + self.targets
        count = 0
        for tree in all_sources:
            if tree.find(xpath) is not None:
                count += 1
        return round((count * 100) / len(all_sources), 2)
