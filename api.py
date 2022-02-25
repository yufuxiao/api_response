from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Model
from django.http import JsonResponse

from base import Code, ResponseException
from pagination import get_pagination


class ApiResponse(JsonResponse, ResponseException):
    """
    构造一个 API 响应

    :param status: HTTP 响应状态码。
    :param code: API 响应中 code 的值。
    :param message: API 响应中 message 的内容。
    :param data: API 响应中 data 的内容，支持任何可以 JSON 序列化的数据类型。
    """
    def __init__(self, *,
                 status: int = 200,
                 code: Code = Code.OK,
                 message: str = "",
                 data=None,
                 pagination=None,
                 ):
        content = dict(code=code, message=message, status=status, data=data)
        if pagination is not None:
            content["pagination"] = pagination

        JsonResponse.__init__(
            self, data=content, encoder=DjangoJSONEncoder, safe=False,
            json_dumps_params=None,
        )
        ResponseException.__init__(self, f'<ApiResponse status={status} code={code} message="{message}">')


def ok(data, *, message="ok", code=None, fields=None, pagination=None, **kwargs):
    """
    构造一个 OK 响应

    :param data: API 响应中 data 的内容，支持任何可以 JSON 序列化的数据类型，具体见 `ApiResponse` 中的说明。
    :param message: API 响应中 message 的内容。
    :param code: API 响应中 code 的值，默认为 Code.OK。原则上不应该使用其他值。
    :param pagination: 如果是分页响应，可以提供 pagination 对象。
    :param fields: 需要序列化的字段
    :param kwargs: 其他需要的额外参数
    """
    if code is None:
        code = Code.OK

    if isinstance(data, Model) and fields is None:
        raise TypeError(f"Model 对象不支持序列化，如有需要请传入 fields")
    elif isinstance(data, Model) and fields is not None:
        fields_list = [i.name for i in data._meta.fields]
        result = dict()
        for field in fields:
            if field not in fields_list:
                raise AttributeError(f"{field}字段不存在")
            result.setdefault(field, getattr(data, field))
    else:
        result = data

    return ApiResponse(data=result, message=message, code=code, status=200, pagination=pagination)


def page(request, queryset, *, page=None, page_size=None, max_page_size=None, max_records=None, fields=None, **kwargs):
    """构造一个分页响应

    :param request: Django HttpRequest 对象。
    :param queryset: QuerySet 或者任意可迭代对象（iterator）。
    :param message: API 响应中 message 的内容。
    :param page: 如果未指定，将自动从 request 中判断，如果指定了，则强制返回该页。
      一般用于某些输入建议的场景，只返回第一页的内容。
    :param page_size: 如果未指定，将自动从 request 中判断，如果指定了，则强制使用该大小。
      一般用于某些需要强制指定页码大小的场景。
    :param max_records: 最多返回多少记录数，默认为 1000，主要用于防止爬虫。
      若不需要限制（如管理后台接口），请赋值为 -1。
    """
    paginator_page, _, pagination = get_pagination(
        request,
        queryset,
        page=page,
        page_size=page_size,
        max_page_size=max_page_size,
        max_records=max_records,
    )
    data = []
    for item in paginator_page:
        items = dict()
        for field in fields:
            items.setdefault(field, getattr(item, field))
        data.append(items)

    return ok(data=data, pagination=pagination)


def bad_request(message='bad request', *, code=None, data=None, **kwargs):
    if code is None:
        code = Code.BAD_REQUEST
    return ApiResponse(message=message, code=code, data=data)


def not_authorized(message='not authorized'):
    return ApiResponse(status=401, code=Code.NOT_AUTHORIZED, message=message)


def forbidden(message='forbidden'):
    return ApiResponse(status=403, code=Code.FORBIDDEN, message=message)


def not_found(message='not found'):
    return ApiResponse(status=404, code=Code.NOT_FOUND, message=message)


def invalid_endpoint(message='invalid endpoint'):
    return ApiResponse(status=404, code=Code.NOT_FOUND, message=message)


def method_not_allowed(message='method not allowed'):
    return ApiResponse(status=405, code=Code.METHOD_NOT_ALLOWED, message=message)


def internal_server_error(message='internal server error'):
    return ApiResponse(status=500, code=Code.INTERNAL_SERVER_ERROR, message=message)


def not_implemented(message='not implemented'):
    return ApiResponse(status=501, code=Code.NOT_IMPLEMENTED, message=message)


# 在使用 raise 时，请用以下 PascalCase 的函数，以使代码更清晰
BAD_REQUEST = bad_request
NOT_AUTHORIZED = not_authorized
FORBIDDEN = forbidden
NOT_FOUND = not_found
INVALID_ENDPOINT = invalid_endpoint
METHOD_NOT_ALLOWED = method_not_allowed
INTERNAL_SERVER_ERROR = internal_server_error
NOT_IMPLEMENTED = not_implemented
