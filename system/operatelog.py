from manager.models import OperateLogDB
def OperateLog(request,op_type,op_message,result=0):
     # 请求IP
    data = {}
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    op_user = request.user
    if x_forwarded_for:
        # 如果有代理，获取真实IP
        remote_ip = x_forwarded_for.split(",")[0]
    else:
        remote_ip = request.META.get('REMOTE_ADDR')
    data.update({
        "remote_ip": remote_ip,
        "op_user":op_user,
        "op_type":op_type,
        "result":result,
        "op_message":op_message
    })
    OperateLogDB.objects.create(**data)  # 操作日志入库db