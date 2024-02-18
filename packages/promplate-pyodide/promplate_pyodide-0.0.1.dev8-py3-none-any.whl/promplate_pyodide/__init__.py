from pathlib import Path

from .utils.proxy import to_js


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


def patch_openai():
    def ensure(text_or_list: str):
        return to_js(promplate.chat.ensure(text_or_list))

    import promplate.llm.openai

    promplate.llm.openai.ensure = ensure


def patch_all():
    patch_promplate()
    patch_openai()
