from pathlib import Path
from typing import TYPE_CHECKING

from .utils.sync import poll


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
            return poll()(cls.afetch)(url, **kwargs)

    class Node(Loader, promplate.Node):
        pass

    class Template(Loader, promplate.Template):
        pass

    promplate.template.Loader = Loader
    promplate.template.Template = promplate.Template = Template
    promplate.node.Node = promplate.Node = Node
