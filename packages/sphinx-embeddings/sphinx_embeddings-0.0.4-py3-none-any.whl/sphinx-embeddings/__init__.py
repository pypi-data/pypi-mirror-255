import hashlib
import json
import os
from typing import Dict, Union, List, Callable

from docutils.nodes import section
from sphinx.application import Sphinx
from sphinx.addnodes import document

import logging  # debug
log_id = 'sphinx-embeddings'  # debug
logger = logging.getLogger(log_id)  # debug
handler = logging.FileHandler(f'{log_id}.log')  # debug
logger.addHandler(handler)  # debug
logger.setLevel(logging.DEBUG)  # debug


def prune_docs(actual_docs):
    maybe_docs = data.keys()
    old_docs = [doc for doc in maybe_docs if doc not in actual_docs]
    for doc in old_docs:
        del data[doc]


def on_build_finished(app: Sphinx, exception) -> None:
    prune_docs(app.env.found_docs)
    with open(srcpath, 'w') as f:
        json.dump(data, f, indent=4)
    with open(outpath, 'w') as f:
        json.dump(data, f, indent=4)


def prune_sections(docname, before, after):
    old_data = [hash for hash in before if hash not in after]
    for hash in old_data:
        del data[docname][hash]


def embed(fn: Callable, text: str) -> List:
    return fn(text)


def on_doctree_resolved(app: Sphinx, doctree: document, docname: str) -> None:
    """TODO: Description"""
    before = []
    after = []
    if docname not in data:
        data[docname] = {}
    else:
        before = data[docname].keys()
    for node in doctree.traverse(section):
        text = node.astext()
        hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        after.append(hash)
        if hash in data[docname]:
            continue
        data[docname][hash] = {}
        data[docname][hash]['text'] = text[0:50]
        embedding = app.config.sphinx_embeddings_function(text)
        data[docname][hash]['embedding'] = embedding
    prune_sections(docname, before, after)


def init_configs(app: Sphinx) -> None:
    # https://ai.google.dev/models/gemini#embedding
    app.add_config_value(f'sphinx_embeddings_model', 'gemini/embedding-001', 'html')
    app.add_config_value(f'sphinx_embeddings_function', None, 'html')


def init_globals(srcdir: str, outdir: str) -> None:
    global filename
    global srcpath
    global outpath
    global data
    filename = 'embeddings.json'  # TODO: Make configurable
    srcpath = f'{srcdir}/{filename}'  # TODO: Make configurable
    outpath = f'{outdir}/{filename}'  # TODO: Make configurable
    data = {}
    if os.path.exists(srcpath):
        with open(srcpath, 'r') as f:
            data = json.load(f)


def setup(app: Sphinx) -> Dict[str, Union[bool, str]]:
    """TODO: Description"""
    init_globals(app.srcdir, app.outdir)
    init_configs(app)
    # https://www.sphinx-doc.org/en/master/extdev/appapi.html#sphinx-core-events
    app.connect('doctree-resolved', on_doctree_resolved)
    app.connect('build-finished', on_build_finished)
    cwd = os.path.abspath(os.path.dirname(__file__))
    with open(f'{cwd}/version.json', 'r') as f:
        version = json.load(f)['version']
    return {
        'version': version,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
