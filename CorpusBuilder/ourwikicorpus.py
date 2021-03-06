#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Radim Rehurek <radimrehurek@seznam.cz>
# Copyright (C) 2012 Lars Buitinck <larsmans@gmail.com>
# Licensed under the GNU LGPL v2.1 - http://www.gnu.org/licenses/lgpl.html


import logging
import re
from xml.etree.cElementTree import iterparse # LXML isn't faster, so let's go with the built-in solution

from gensim import utils

logger = logging.getLogger('gensim.corpora.wikicorpus')

# ignore articles shorter than ARTICLE_MIN_WORDS characters (after full preprocessing)
ARTICLE_MIN_WORDS = 50


RE_P0 = re.compile('<!--.*?-->', re.DOTALL | re.UNICODE) # comments
RE_P1 = re.compile('<ref([> ].*?)(</ref>|/>)', re.DOTALL | re.UNICODE) # footnotes
RE_P2 = re.compile("(\n\[\[[a-z][a-z][\w-]*:[^:\]]+\]\])+$", re.UNICODE) # links to languages
RE_P3 = re.compile("{{([^}{]*)}}", re.DOTALL | re.UNICODE) # template
RE_P4 = re.compile("{{([^}]*)}}", re.DOTALL | re.UNICODE) # template
RE_P5 = re.compile('\[(\w+):\/\/(.*?)(()|(.*?))\]', re.UNICODE) # remove URL, keep description
RE_P6 = re.compile("\[([^][]*)\|([^][]*)\]", re.DOTALL | re.UNICODE) # simplify links, keep description
RE_P7 = re.compile('\n\[\[[iI]mage:(.*?)(\|.*?)*\|(.*?)\]\]', re.UNICODE) # keep description of images
RE_P8 = re.compile('\n\[\[[fF]ile:(.*?)(\|.*?)*\|\]\]', re.UNICODE) # keep description of files
RE_P9 = re.compile('<nowiki([> ].*?)(</nowiki>|/>)', re.DOTALL | re.UNICODE) # outside links
RE_P10 = re.compile('<math([> ].*?)(</math>|/>)', re.DOTALL | re.UNICODE) # math content
RE_P11 = re.compile('<(.*?)>', re.DOTALL | re.UNICODE) # all other tags
RE_P12 = re.compile('\n(({\|)|(\|-)|(\|}))(.*?)(?=\n)', re.UNICODE) # table formatting
RE_P13 = re.compile('\n(\||\!)(.*?\|)*([^|]*?)', re.UNICODE) # table cell formatting
RE_P14 = re.compile('\[\[Category:[^][]*\]\]', re.UNICODE) # categories
# Remove File and Image template
RE_P15 = re.compile('\[\[([fF]ile:|[iI]mage)[^]]*(\]\])', re.UNICODE)

RE_H = re.compile('[=]+(.*?)[=]+')

re_definition = re.compile('\[\[([fF]ile:|[iI]mage:)([^|]+)(\|[^\[\]]+)(\|[^\[\]]+)\|(([^\[\]]+)|(\[\[([^\[\]]+)\]\]))*(\]\])', re.UNICODE)
re_definition2 = re.compile('\[\[([fF]ile:|[iI]mage:)([^|]+)(\|[^\[\]]+)\|(([^\[\]]+)|(\[\[([^\[\]]+)\]\]))*(\]\])', re.UNICODE)

RE_EMPTY_BRACKETS = re.compile('\([\s]*\)', re.UNICODE)

RE_BRACKETS_WITH_TEMPLATE = re.compile('\([^\)\(]*[\{]+[^\)\(]*\)', re.UNICODE)

RE_GALLERY = re.compile('<gallery([> ].*?)(</gallery>|/>)', re.DOTALL | re.UNICODE) # math content

def filter_wiki(raw):
    """
    Filter out wiki mark-up from `raw`, leaving only text. `raw` is either unicode
    or utf-8 encoded string.
    """
    # parsing of the wiki markup is not perfect, but sufficient for our purposes
    # contributions to improving this code are welcome :)
    text = utils.to_unicode(raw, 'utf8', errors='ignore')
    text = utils.decode_htmlentities(text) # '&amp;nbsp;' --> '\xa0'
    return remove_markup(text)


def remove_markup(text):
    # remove \n in beginig of article
    text = re.sub(RE_P2, "", text) # remove the last list (=languages)
    # the wiki markup is recursive (markup inside markup etc)
    # instead of writing a recursive grammar, here we deal with that by removing
    # markup in a loop, starting with inner-most expressions and working outwards,
    # for as long as something changes.
    text = remove_template(text)
    text = remove_in_subparagraph(text) #удаляем разметку для картинок и файлов, удаляем разметку
                                        #  сдвигов и разноуровневых списков без поинтов,
                                        # "обрубаем" статью на стаднадртных для википедии блоках References, See also и Notes
    iters = 0
    while True:
        old, iters = text, iters + 1
        text = re.sub(RE_P0, "", text) # remove comments
        text = re.sub(RE_P1, '', text) # remove footnotes
        text = re.sub(RE_P9, "", text) # remove outside links
        text = re.sub(RE_P10, "", text) # remove math content
        text = re.sub(RE_P11, "", text) # remove all remaining tags
        text = re.sub(RE_P14, '', text) # remove categories
        text = re.sub(RE_P5, '\\3', text) # remove urls, keep description
        text = re.sub(RE_P6, '\\2', text) # simplify links, keep description only
        # remove table markup
        text = text.replace('||', '\n|') # each table cell on a separate line
        text = re.sub(RE_P12, '', text) # remove formatting lines
        text = re.sub(RE_P13, '', text) # remove cell content
        #text = re.sub(RE_P13, '\n\\3', text) # leave only cell content
        # remove empty mark-up
        text = re.sub(RE_H, '\\1', text)
        text = text.replace('[]', '')
        text = text.replace('\'\'\'', '')
        text = text.replace('\'\'', '')
        if old == text or iters > 2: # stop if nothing changed between two iterations or after a fixed number of iterations
            break


    # the following is needed to make the tokenizer see '[[socialist]]s' as a single word 'socialists'
    # TODO is this really desirable?
    text = text.replace('[', '').replace(']', '') # promote all remaining markup to plain text
    text = re.sub(RE_EMPTY_BRACKETS, "", text) # remove empty brackets
    result = re.match(r'[\n]+', text) # удаляем переносы строк
    if result is not None:
        text = text[result.end(0):]
    return text



def remove_template(s):
    s = re.sub(RE_BRACKETS_WITH_TEMPLATE, "", s)
    n_open, n_close = 0, 0
    starts, ends = [], []
    in_template = False
    prev_c = None
    in_as_of_template = False
    as_of_templates_index, as_of_templates_content = [], []
    for i, c in enumerate(iter(s)):
        if not in_template:
            if c == '{' and c == prev_c:
                starts.append(i - 1)
                in_template = True
                n_open = 1
        if in_template:
            if c == 'as' or c== 'As':
                in_as_of_template = True
                as_of_templates_index.append(len(starts))
                as_of_templates_content.append([])
            elif in_as_of_template and c != '|' and c != 'of':
                as_of_templates_content[-1].append(c)

            if c == '{':
                n_open += 1
            elif c == '}':
                n_close += 1
            if n_open == n_close:
                ends.append(i)
                in_template = False
                n_open, n_close = 0, 0
        prev_c = c

    # Remove all the templates
    if len(as_of_templates_index) == 0:
        s_buf = ''.join([s[end + 1:start] for start, end in
                    zip(starts + [None], [-1] + ends)])
    else:
        current_index = 0
        s_buf = ''
        coordinate = zip(starts + [None], [-1] + ends)
        for i, index in enumerate(as_of_templates_index):
            s_buf = s_buf.join([s[end + 1:start] for start, end in
                                coordinate[current_index:index]])
            current_index = index
            s_buf.join('as of '+ as_of_templates_content[i][0])
    return s_buf


def remove_in_subparagraph(s):
    #удаляем коллекции изображений внутри тега <gallery>
    s = re.sub(RE_GALLERY, ' ', s)
    #кажется, что в сыром дампе разметка файлов вынесена в отдельный абзац
    # RE_P15  не работает на цельном тексте, т.е. там не учтено, что в описании файла могут присутствовать [[ и ]]
    # как элементы wiki-разметки, удовлетворяющие такому условию регулярки re_definition и re_definition2 вешают
    # программу, поэтому пока решила разбивать на абзацы и выкидывать те, которые описывают файлы\картинки
    # руки оторвать, но здесь же удаляю разметку
    text = ''
    for subparagraph in s.split('\n'):
        if subparagraph.startswith(':'):
            text += (subparagraph[-1] + '\n')
        elif subparagraph.startswith(';'):
            subparagraph = subparagraph.replace(':', '', 1)
            text += (subparagraph[-1] + '\n')
        elif subparagraph.startswith('== References ==') or subparagraph.startswith('==References=='):
            return text
        elif subparagraph.startswith('==See also') or subparagraph.startswith('== See also'):
            return text
        elif subparagraph.startswith('==Notes') or subparagraph.startswith('== Notes'):
            return text
        elif re.match(RE_P15, subparagraph) is None:
            text += (subparagraph + '\n')
    return text


def tokenize(content):
    """
    Tokenize a piece of text from wikipedia. The input string `content` is assumed
    to be mark-up free (see `filter_wiki()`).
    Return list of tokens as utf8 bytestrings. Ignore words shorted than 2 or longer
    that 15 characters (not bytes!).
    """
    # TODO maybe ignore tokens with non-latin characters? (no chinese, arabic, russian etc.)
    return [token.encode('utf8') for token in utils.tokenize(content, lower=True, errors='ignore')
            if 1 <= len(token) <= 150 and not token.startswith('_')]


def get_namespace(tag):
    """Returns the namespace of tag."""
    m = re.match("^{(.*?)}", tag)
    namespace = m.group(1) if m else ""
    if not namespace.startswith("http://www.mediawiki.org/xml/export-"):
        raise ValueError("%s not recognized as MediaWiki dump namespace"
                         % namespace)
    return namespace
_get_namespace = get_namespace

def extract_pages(f, filter_namespaces=False):
    """
    Extract pages from MediaWiki database dump.
    Return an iterable over (str, str) which generates (title, content) pairs.
    """
    elems = (elem for _, elem in iterparse(f, events=("end",)))

    # We can't rely on the namespace for database dumps, since it's changed
    # it every time a small modification to the format is made. So, determine
    # those from the first element we find, which will be part of the metadata,
    # and construct element paths.
    elem = next(elems)
    namespace = get_namespace(elem.tag)
    ns_mapping = {"ns": namespace}
    page_tag = "{%(ns)s}page" % ns_mapping
    text_path = "./{%(ns)s}revision/{%(ns)s}text" % ns_mapping
    title_path = "./{%(ns)s}title" % ns_mapping
    ns_path = "./{%(ns)s}ns" % ns_mapping
    pageid_path = "./{%(ns)s}id" % ns_mapping

    for elem in elems:
        if elem.tag == page_tag:
            title = elem.find(title_path).text
            text = elem.find(text_path).text

            ns = elem.find(ns_path).text
            if filter_namespaces and ns not in filter_namespaces:
                text = None

            pageid = elem.find(pageid_path).text
            yield title, text or "", pageid     # empty page will yield None

            # Prune the element tree, as per
            # http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
            # except that we don't need to prune backlinks from the parent
            # because we don't use LXML.
            # We do this only for <page>s, since we need to inspect the
            # ./revision/text element. The pages comprise the bulk of the
            # file, so in practice we prune away enough.
            elem.clear()
_extract_pages = extract_pages  # for backward compatibility
