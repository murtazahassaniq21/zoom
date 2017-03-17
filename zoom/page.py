"""
    zoom.page

"""

import os

from zoom.fill import dzfill
from zoom.response import HTMLResponse

import zoom.helpers


class Page(object):
    """a web page"""

    def __init__(self, content, *args, **kwargs):
        self.content = content
        self.template = kwargs.pop('template', 'default')
        self.theme = kwargs.pop('theme', 'default')
        self.args = args
        self.kwargs = kwargs

    def helpers(self):
        """provide helpers"""
        return {'page_' + k: v for k, v in self.__dict__.items()}

    def render(self, request):
        """render page"""

        def not_found(name):
            """what happens when a helper is not found"""
            def missing_helper(*args, **kwargs):
                """provide some info for missing helpers"""
                parts = ' '.join(
                    [name] +
                    ['{!r}'.format(a) for a in args] +
                    ['{}={!r}'.format(k, v) for k, v in kwargs.items()]
                )
                return '&lt;dz:{}&gt; missing'.format(
                    parts,
                )
            return missing_helper

        def filler(helpers):
            """callback for filling in templates"""
            def _filler(name, *args, **kwargs):
                """handle the details of filling in templates"""

                if hasattr(self, name):
                    attr = getattr(self, name)
                    if callable(attr):
                        repl = attr(self, *args, **kwargs)
                    else:
                        repl = attr
                    return dzfill(repl, _filler)

                helper = helpers.get(name, not_found(name))
                if callable(helper):
                    repl = helper(*args, **kwargs)
                else:
                    repl = helper
                return dzfill(repl, _filler)
            return _filler

        helpers = {}
        helpers.update(zoom.helpers.__dict__)
        helpers.update(request.site.helpers())
        helpers.update(self.helpers())
        helpers.update(dict(
            title=request.site.name,
            site_url=request.site.url,
            request_path=request.path,
            css='',
            js='',
            head='',
            tail='',
            styles='',
            libs='',
        ))

        template = 'default'
        theme_path = request.site.theme_path
        filename = os.path.join(theme_path, template + '.html')

        with open(filename) as reader:
            template = reader.read()
        return HTMLResponse(
            dzfill(template, filler(helpers))
        )


page = Page  # pylint: disable=invalid-name
