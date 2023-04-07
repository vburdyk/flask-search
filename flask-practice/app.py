import psutil
from functools import lru_cache
from flask import Flask, abort, request, Response
from statapi.methods import formatters, make_doc
from statapi import methods
from additional.converter import make_bool

app = Flask(__name__)


@app.route('/stats/')
@lru_cache(maxsize=1)  # can use cuz no flask proxies refered
def stats_root():
    """List all methods."""
    format = request.args.get('format')
    res = {'methods': list(methods)}
    if format is not None and format in formatters:
        format_function = formatters[format][1]
        return format_function(res)
    descr = """<h1>{number}) '{name}'</h1>
            <h4>Description: </h4> <p>{description}</p>"""
    res['methods'] = [descr.format(number=n, name=name, description=make_doc(name)) for n, name in enumerate(res['methods'], start=1)]
    return Response(res['methods'])


@app.route('/stats/<string:method>')
def stats(method):
    format = request.args.get('format')
    kwargs = request.args.to_dict()
    kwargs = make_bool(**kwargs)

    try:
        func = methods[method]
    except KeyError:
        abort(404, f'Method {method} not found')

    try:
        # format is set on a statapi module level defaults
        res, mime = func(**kwargs)
    except Exception as exc:
        abort(400)

    # TODO: add error reporting verbosity
    #       e.g. when format is not supported

    return Response(res, mimetype=mime)


if __name__ == '__main__':
    # We need to set logging to be able to see everything
    import logging
    app.logger.setLevel(logging.DEBUG)

    # (!) Never run your app on '0.0.0.0 unless you're deploying
    #     to production, in which case a proper WSGI application
    #     server and a reverse-proxy is needed
    #     0.0.0.0 means "run on all interfaces" -- insecure
    app.run(host='127.0.0.1', port=8000, debug=True)