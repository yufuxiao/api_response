
### api_response
构造一个 API 响应

### 背景
    为了使 api 返回更明确，我们不使用 JsonResponse 和 Response(drf),这里构造了一些常见的响应，如：ok、page、bad_request、forbidden、not_found 等。

### 注意

    api.ok() 只接收 JSON 类型数据， 简单支持 model 对象序列化，需要指定 fields
    api.page() 接收任意可迭代对象，同样需要指定 fields

### 使用

    def test_api(request):
    tasks = Tasks.objects.get(id=5)
    qs = Tasks.objects.all()
    
    # queryset:
    return api.page(request, qs, fields=["id", "task_name", "test_list", "test_char", "created_at",])
    # model 对象
    return api.ok(tasks, fields=["id", "task_name", "test_list", "test_char", "created_at",])
    
### 支持的响应
    
    api.ok()
    api.page()
    api.bad_request
    api.not_found()
    ...
    
### 在使用 raise 时
    
    api.BAD_REQUEST()
    api.NOT_AUTHORIZED()
    api.FORBIDDEN()
    api.NOT_FOUND()
    ...
    
    
