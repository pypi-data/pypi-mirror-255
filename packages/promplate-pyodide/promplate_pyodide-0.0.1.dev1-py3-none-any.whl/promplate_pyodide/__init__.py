from pathlib import Path
from typing import TYPE_CHECKING, Callable


def patch_promplate():
    import promplate

    class Loader(promplate.template.Loader):

        @classmethod
        async def afetch(cls, url: str, **kwargs):
            if TYPE_CHECKING:

                async def pyfetch(url: str):
                    class Response:
                        async def text(self):
                            return url

                    return Response()

            else:
                from pyodide.http import pyfetch

            res = await pyfetch(cls._join_url(url))
            obj = cls(res.text())
            obj.name = Path(url).stem

            return obj

        @classmethod
        def fetch(cls, url: str, **kwargs):
            if TYPE_CHECKING:
                from io import StringIO

                open_url: Callable[[str], StringIO] = None  # type: ignore
            else:
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
