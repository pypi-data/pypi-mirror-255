# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['zeitdieb']
setup_kwargs = {
    'name': 'zeitdieb',
    'version': '0.2.0',
    'description': '',
    'long_description': '# Zeitdieb\n\n_Zeitdieb_ allows you to profile the time each line of your code takes.\n\n![Screenshot of the output of zeitdieb](https://raw.githubusercontent.com/digitalarbeiter/zeitdieb/master/screenshot.png)\n\n```\npip install zeitdieb\n```\n\n## Manual usage\n\n```python\nwith StopWatch(additional, callables) as sw:\n    your()\n    code()\nprint(sw)\n```\n\nAlternatively, without using the context manager:\n\n```python\nsw = StopWatch(additional, callables)\nsw.start()\nyour()\ncode()\nsw.finish()\nprint(sw)\n```\n\n\n## Formatting\n\nWhile you can just print the `StopWatch` object, you can also customize the output by using f-strings:\n\n```python\nprint(f"{sw:3b:0.3,0.1}")\n```\n\nThe format spec looks like this: `[width][flags]:[threshold][,threshold]`.\n\n- `width` specifies the width of the time column (e.g. `4` for an output like `2.01`)\n- `flags` are single-letter flags influencing the output:\n    - `b` enables barplot mode: Instead of a numeric time output, a vertical barplot will be printed\n- `threshold`s specify where to start marking times as critical/warnings\n  (red/yellow). The thresholds must be ordered (highest to lowest).\n\n## Integrations\n\nZeitdieb can optionally be intregrated with Pyramid, Flask, or FastAPI. After\nyou\'ve done so, you can trigger tracing with the special header `X-Zeitdieb`.\n\n### Pyramid\n\nPut this somewhere in your Pyramid settings:\n\n```ini\nzeitdieb.format = 20b\n\npyramid.tweens =\n    ...\n    zeitdieb.pyramid\n```\n\n### Flask\n\nFor Flask or flask-based frameworks, adjust your `create_app()` function:\n\n```python\ndef create_app():\n    ...\n    my_flask_app.config["ZEITDIEB_FORMAT"] = "7b:0.5"\n    zeitdieb.flask(my_flask_app)\n```\n\n### FastAPI\n\nFastAPI can be configured by calling `zeitdieb.fastapi()` inside of `create_app()`:\n\n```python\nclass Settings(...):\n    ...\n    zeitdieb_format: Optional[str] = "6b"\n\ndef create_app(...):\n    ...\n    zeitdieb.fastapi(app, settings)\n```\n\n### Settings client headers\n\nTo trigger the tracing of functions, you need to set an `X-Zeitdieb` header:\n\n#### curl\n\n```bash\n$ curl https://.../ -H \'X-Zeitdieb: path.to.module:callable,path.to.othermodule:callable`\n```\n\n#### jsonrpclib\n\n```python\njsonrpclib.ServerProxy(host, headers={"X-Zeitdieb": "path.to.module:callable,path.to.othermodule:callable"})\n```\n\n## Acknowledgements\n\nThis project was created as a result of a learning day @ [solute](https://www.solute.de/ger/).\n',
    'author': 'Patrick Schemitz',
    'author_email': 'ps@solute.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
