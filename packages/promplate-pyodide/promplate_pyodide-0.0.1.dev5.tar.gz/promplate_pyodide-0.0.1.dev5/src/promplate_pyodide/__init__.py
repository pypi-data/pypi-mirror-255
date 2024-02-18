from pathlib import Path
from typing import TYPE_CHECKING, Callable

from .utils.js import to_js


def patch_promplate():
    import promplate

    class Loader(promplate.template.Loader):

        @classmethod
        async def afetch(cls, url: str, **kwargs):
            from pyodide.http import pyfetch

            res = await pyfetch(cls._join_url(url))
            obj = cls(await res.text())
            obj.name = Path(url).stem

            return obj

        @classmethod
        def fetch(cls, url: str, **kwargs):
            from pyodide.http import open_url

            res = open_url(cls._join_url(url))
            obj = cls(res.read())
            obj.name = Path(url).stem

            return obj

    class Node(Loader, promplate.Node):
        pass

    class Template(Loader, promplate.Template):
        pass

    promplate.template.Loader = Loader
    promplate.template.Template = promplate.Template = Template
    promplate.node.Node = promplate.Node = Node

    from promplate import parse_chat_markup as parse

    def parse_chat_markup(text: str):
        return to_js(parse(text))

    promplate.chat.parse_chat_markup = promplate.parse_chat_markup = parse_chat_markup
