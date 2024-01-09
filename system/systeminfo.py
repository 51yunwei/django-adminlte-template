from manager.models import SystemInfoDB
def SystemInfo(request):
    system_info = SystemInfoDB.objects.all()
    if system_info.count():
        system_title = system_info.first().system_title if system_info.first().system_title else '未设置的title'
        system_name = system_info.first().system_name if system_info.first().system_name else '未设置的系统名称'
    else:
        system_title = '未设置的title'
        system_name = '未设置的系统名称'

    return {'systeminfo':{'system_title':system_title,'system_name':system_name}}