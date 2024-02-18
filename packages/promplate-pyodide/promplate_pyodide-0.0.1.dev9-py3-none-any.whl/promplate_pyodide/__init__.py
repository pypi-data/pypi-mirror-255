from pathlib import Path


def patch_promplate(patch_ensure=False):
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

    if patch_ensure:
        from promplate.prompt.chat import Message
        from promplate.prompt.chat import ensure as _ensure

        from .utils.proxy import to_js

        def ensure(text_or_list: list[Message] | str):
            return to_js(_ensure(text_or_list))

        promplate.prompt.chat.ensure = ensure
