from django.core.paginator import Paginator


def get_pagination(request, queryset,
                   *,
                   page=None, page_size=None, max_page_size=None, max_records=None,
                   ):
    """
    获取分页数据结构

    :param request: HttpRequest 对象。
    :param queryset: QuerySet 或者任意可迭代对象（iterator）。
    :param page: 如果提供了该参数，则使用指定值，否则使用 querystring 中 page 的值，默认为 1。
    :param page_size: 如果提供了该参数，则使用指定值，否则使用 querystring 中 page_size 的值，默认为 10。
    :param max_records: 最多返回多少记录数，默认为 1000，主要用于防止爬虫。
      若不需要限制（如管理后台接口），请赋值为 -1。

    返回三元组：(page, paginator, pagination)

    page: django.core.paginator.Page 对象
    paginator: django.core.paginator.paginator 对象
    pagination: 一个字典，字段格式如下：
      {
        'total': int, 条目总数
        'page': int, 当前页码（页码从1开始）
        'page_size': int, 每页条目数量
        'last_page': int, 最后一页的页码
        'from': int, 当前页第一个元素的编号（编号从1开始，下同）
        'to': int, 当前页最后一个元素的编号
      }
    """
    max_page_size = max_page_size or 50
    max_records = max_records or 1000
    if page_size and page_size > max_page_size:
        raise ValueError(
            f'page_size 超过了允许的最大值：{max_page_size}，'
            '如果确实有需求，请提供 max_page_size 参数'
        )
    if max_page_size > max_records > 0:
        raise ValueError('max_page_size 不能大于 max_records')

    if page is None:
        page = get_int(request, 'page', 1)
    if page_size is None:
        page_size = get_int(request, 'page_size', 10)
        if page_size > max_page_size:
            page_size = max_page_size
    if max_records is None:
        max_records = 1000

    if page * page_size > max_records > 0:
        page = max_records // page_size

    paginator = Paginator(queryset, page_size)
    paginator_page = paginator.get_page(page)
    pagination = {
        'total': paginator.count,
        'page': paginator_page.number,
        'page_size': page_size,
        'last_page': paginator.num_pages,
        'from': paginator_page.start_index(),
        'to': paginator_page.end_index(),
    }

    return paginator_page, paginator, pagination


def get_int(request, name, default=None, raise_on_value_error=False):
    """
    获取一个 int 类型的 querystring 参数

    参数的值必须是整数（支持负数），不支持小数。

    :param request: HttpRequest 对象。
    :param name: 参数名称。
    :param default: 如果 querystring 中没有该参数，则返回 default。
    :param raise_on_value_error: 若为 True，当参数值不是合法整数时，将抛出 ValueError，若为 False（默认），则返回 default 值。
    """
    value = request.GET.get(name, None)

    if value is None:
        return default

    try:
        return int(value)
    except ValueError as e:
        if raise_on_value_error:
            raise e
        return default