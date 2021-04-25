from __future__ import annotations


def append_error(params, err):
    """

    :param params:
    :param err:
    :return:
    """
    if params:
        dict_items = params.copy()
    else:
        dict_items = {}
    if err:
        stack = None
        if hasattr(err, "stack"):
            stack = err.stack
        original_exception = None
        if hasattr(err, "original_exception"):
            original_exception = str(err.original_exception)
        error = {"errorName": str(type(err).__name__), "errorMessage": str(err), "stackTrace": str(stack), "original_exception":original_exception}
        dict_items.update(error)
    logMsg = {key: value for (key, value) in (dict_items.items())}
    return logMsg


def log_json(halo_context, params=None, err=None,provider_context=None):
    """

    :param halo_context:
    :param params:
    :param err:
    :return:
    """

    dict_items = dict(halo_context.table)
    if provider_context:
        dict_items.update(provider_context)
    logMsg = {key: value for (key, value) in (dict_items.items())}
    if params or err:
        pe = append_error(params, err)
        if pe:
            logMsg['params'] = pe

    # logger.debug(json.dumps(logMsg))
    return logMsg
    # return json.dumps(logMsg)
    # {"aws_request_id": "1fcf5a10-9d44-49dd-bbad-9f23945c306f", "level": "DEBUG", "x-user-agent": "halolib:/:GET:f55a", "awsRegion": "REGION", "x-correlation-id": "1f271213-6d32-40b7-b1dc-12e3a9a31bf4", "debug-log-enabled": "false", "functionVersion": "VER", "message": "we did it", "stage": "STAGE", "functionMemorySize": "MEM", "functionName": "halolib"}
