# -*- coding: utf-8 -*-
# Copyright (C) 2023 TUD | ZIH
# ralf.klammer@tu-dresden.de

import logging


import requests
from lxml.etree import fromstring, ElementTree, tostring

log = logging.getLogger(__name__)


class XMLParserBase(object):
    def __init__(self, uri=None, tree=None):
        self.uri = uri
        self.tree = tree
        self.load_resource()

    def __repr__(self):
        return "<XSDParserBase: %s>" % self.uri

    @property
    def file_name(self):
        if self.uri:
            return self.uri.split("/")[-1]

    def load_resource(self):
        log.debug("XMLParserBase - load uri: %s" % self.uri)
        try:
            if self.tree is None:
                if self.uri.startswith("http"):
                    resource = requests.get(self.uri).content
                else:
                    with open(self.uri, "r") as file:
                        resource = file.read()
                resource = resource.replace("\t", "  ").encode()
                self.tree = fromstring(resource)
        except Exception as e:
            log.error(e)
            raise "Unable to load XML resource"

    def _decompose_search_string(self, search_string):
        attrib = None
        if search_string.find("/@") != -1:
            decomposed = search_string.split("/@")
            search_string = decomposed[0]
            attrib = decomposed[1]
        return search_string, attrib

    def find(self, search_string, elem=None, text=None, return_text=False):
        search_string, attrib = self._decompose_search_string(search_string)
        result = (elem if elem is not None else self.tree).find(
            search_string, namespaces=self.tree.nsmap
        )
        if result is not None and attrib:
            result.text = result.get(attrib)
        if text:
            if result.text == text:
                return tostring(result) if return_text else result
        else:
            return tostring(result) if return_text and result else result

    def findall(self, search_string, elem=None, text=None):
        search_string, attrib = self._decompose_search_string(search_string)
        results = (elem if elem is not None else self.tree).findall(
            search_string, namespaces=self.tree.nsmap
        )
        if attrib:
            return [result for result in results if result.get(attrib)]
        elif text:
            return [result for result in results if result.text == text]
        else:
            return results

    def write(self, filename):
        ElementTree(self.tree).write(
            filename, pretty_print=True, encoding="utf-8"
        )

    def print_tree(self):
        return tostring(self.tree).decode("utf-8")
