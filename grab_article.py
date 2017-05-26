#!/usr/bin/env python
"""Parse HTML into structured text."""
__version__ = "1.0.0"
__author__ = "Alexander Kamyanskiy"

import argparse
import ntpath
import os
import requests
import sys

from bs4 import BeautifulSoup
from bs4.element import Tag
from urllib.parse import urlparse

from exceptions import TextGrabberError
from formatters import ParseHelper


class TextGrabber(object):
    def __init__(self, url, *args, **kwargs):
        self.url = url
        self.article_as_list = []
        self.article_text = ''
        self.parser = ParseHelper()
        self.content = None
        self.soup = None
        self.verbose = kwargs.get('verbose')

    def download(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            if self.verbose:
                print("Page {} was downloaded successful.\n".format(self.url))
        else:
            sys.exit(1)
        self.content = response.content

    def clean_html(self, soup):
        skip_tags = ['aside', 'script', 'style']
        for tag in soup(skip_tags):
            tag.extract()
        return soup

    def _get_path_from_url(self):
        url_parsed = urlparse(self.url)
        full_path = url_parsed.netloc + url_parsed.path
        if full_path.endswith("shtml"):
            return full_path.replace('shtml', 'txt')
        elif full_path.endswith("html"):
            return full_path.replace('html', 'txt')
        splitted = self.url.split("/")[2:]
        last_item = splitted[-1]
        if not last_item:
            filename = splitted[-2] + ".txt"
        elif last_item.endswith('html'):
            filename = last_item.split(".")[0] + ".txt"
        else:
            filename = "default.txt"
        return os.path.join(*splitted, filename)

    def save_result(self):
        if not self.article_as_list:
            raise TextGrabberError("Article was not parsed,"
                                   " run parse method first, please.")
        path = self._get_path_from_url()
        directories = ntpath.dirname(path)
        if not os.path.exists(directories):
            os.makedirs(directories)
        with open(path, encoding="utf-8", mode="w+") as fp:
            fp.write(self.article_text)
        if self.verbose:
            print("File was successfully stored as {0}".format(path))

    def build(self):
        self.download()
        soup = BeautifulSoup(self.content, "html.parser")
        # remove all unnecessary tags like <script>, <style>
        self.soup = self.clean_html(soup)
        self.parse()
        self.save_result()

    def parse(self):
        if self.content is None:
            raise TextGrabberError("Content is None, run download first.")
        title = self.get_title()
        self.article_as_list.append(title)
        self.get_article()

    def get_title(self):
        """
        We suppose that's most possible article title might be in:
        1. <title> tag
        2. <h1> tag

        :return: string , title of article
        """
        splitters = [":", "|", "-"]
        title_tag_items = self.soup.select("title")
        title_h1_items = self.soup.select("h1")
        title_from_tag = ''
        title_from_h1 = ''
        if len(title_h1_items) > 0:
            title_from_h1 = title_h1_items[0].get_text()
        if len(title_tag_items) > 0:
            title_from_tag = title_tag_items[0].get_text()

        title_from_h1 = self.parser.replace_tabular_codes(title_from_h1)
        title_from_h1 = self.parser.normalize_string(title_from_h1)

        title_from_tag = self.parser.replace_tabular_codes(title_from_tag)
        title_from_tag = self.parser.normalize_string(title_from_tag)

        if title_from_h1 in title_from_tag:
            return title_from_h1.strip()

        possible_splitter_weight = []
        for splitter in splitters:
            possible_splitter_weight.append(title_from_tag.split(splitter))

        possible_splitter = splitters.index(max(possible_splitter_weight))
        title = title_from_tag.split(possible_splitter)[0]
        return title.strip()

    def _get_article_nodes(self):
        node_tags = ["p", "pre", "td"]
        nodes = []
        for tag in node_tags:
            search = self.soup.select(tag)
            if search:
                nodes += search
        return nodes

    def _get_best_node(self, nodes):
        weight = 0
        best_node = None
        for node in nodes:
            text = node.get_text()
            if len(text.split(" ")) > weight:
                weight = len(text.split(" "))
                best_node = node
        return best_node

    def get_article(self):
        """
        Set instance attributes: article_as_list, article_text

        1. Suppose that more possible that article might be found by tags
        <p>, <pre>, <td>
        2. We can walk trough these nodes to find the longest nodes those
        have the same parent, so with big possibility that this parent
        contains article.
        3. Get text with rules:
            3.1 every paragraph as separate string
            3.2 if <a> tag inside <p> - format to string [href.value] text
        :return: None

        """

        nodes_to_process = self._get_article_nodes()
        best_node = self._get_best_node(nodes_to_process)
        parent_node = best_node.parent
        for node in parent_node.children:
            if isinstance(node, Tag) and node.name in ["p", "pre", "td"]:
                self.article_as_list.append(self.parser.format_text_line(node))
        self.article_text = self.parser.format_text(self.article_as_list)
        if self.verbose:
            print(self.article_text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parse HTML into structured text.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true",
                       help="Verbose output")
    parser.add_argument("url",
                        help="URL to grab html from.")
    args = parser.parse_args()

    url = args.url
    parsed_url = urlparse(url)
    if not (parsed_url.scheme in ['https', 'http']):
        print("Invalid URL, URL should startswith http:// or https:// scheme.")

    article = TextGrabber(url, verbose=args.verbose)
    article.build()
