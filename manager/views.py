from django.shortcuts import render,redirect
from django.views import View
import json
import os
from django.conf import settings
import datetime
from django.contrib.auth import authenticate,login,logout
from manager.models import UserDB,SystemInfoDB,SystemLogDB,OperateLogDB
from django.urls import reverse
from django.http import JsonResponse,HttpResponse
from django.contrib.auth.hashers import check_password
from system.reexpression import reExpression
from system.systeminfo import SystemInfo
from system.operatelog import OperateLog

# Create your views here.
# 登录界面
class LoginView(View):
    def get(self,request):
        if request.user.is_authenticated:
            return render(request,'base.html')
        return render(request,'login.html')
    def post(self,request):
        # 判断用户登录
        next_path = request.GET.get('next','/') # 虽然是post方法，但还是可以用GET来获取路径的参数，即 ?key=value
        username = request.POST.get('username','')
        password = request.POST.get('password','')
        print(request.POST)
        # print('post next====',request.POST.get('next',''),request.POST)
        user = authenticate(username=username,password=password)
        print(user)
        if user:
            login(request,user)
            request.session["username"] = username
            request.session.set_expiry(0)  # 关闭浏览器就过期
            OperateLog.successlog(request=request,op_type='登录',op_message="登录成功")
            return redirect(next_path)
        login_error_message = '用户名或密码错误'
        OperateLog.failedlog(request=request,op_type='登录',op_message='%s用户登录失败' %(username))
        return render(request,'login.html',{'login_error_message':login_error_message})
def IndexView(request):
    return render(request,'main.html')


# 用户列表View
def UserManagerView(request):
    if not  request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return render(request,'user/index.html')
    print('not ajax request')
    UserInfo = UserDB.objects.all()
    # print(user)
    UserList = []
    for User in UserInfo:
        
        button = """<div style="display: block;text-align: center;margin: auto;">
        <a class="btn {0} btn-sm" data-url="{1}" data-target="#mymodal" data-toggle="modal" data-title="修改用户状态" data-body="是否确认{2}用户？">
                            <i class="fas fa-exchange-alt"></i>
                            {2}
                        </a>
        <a class="btn btn-primary btn-sm" href="{3}">
                            <i class="fas fa-folder">
                            </i>
                            详情
                        </a>
                        <a class="btn btn-info btn-sm" href="{4}">
                            <i class="fas fa-pencil-alt">
                            </i>
                            编辑
                        </a>
                        <a class="btn btn-danger btn-sm" data-url="{5}" data-toggle="modal" data-target="#mymodal" data-title="删除用户" data-body="是否确认删除{6}用户？">
                            <i class="fas fa-trash">
                            </i>
                            删除
                        </a>
        </div>
        """.format('btn-success' if User.is_active else 'btn-secondary',reverse('manager:userstatus',kwargs={'uid':User.uid,'op_type':'inactive' if User.is_active else 'active'}),'禁用' if User.is_active else '启用',reverse('manager:userdetail',kwargs={'uid':User.uid}),reverse('manager:useredit',kwargs={'uid':User.uid}),reverse('manager:userdel',kwargs={'uid':User.uid}),User.username)
        UserList.append({'username': User.username,'create_time':User.create_time.strftime('%Y-%m-%d %H:%M:%S'),'superuser':'Y' if User.is_superuser else 'N','passwd_expire_time': User.passwd_expire_time.strftime('%Y-%m-%d %H:%M:%S'),'uid':str(User.uid),'button':button})

    UserDict = {}
    UserDict["data"] = UserList
    OperateLog.successlog(request=request,op_type='查询',op_message="查询用户列表")
    return HttpResponse(json.dumps(UserDict))

# 用户详细信息
def UserDetail(request,uid):
    UserInfo = UserDB.objects.filter(uid=uid)
    if not UserInfo.count():
        OperateLog.failedlog(request=request,op_type='查询',op_message="查询的用户不存在")
        return redirect(reverse('manager:userlist'))
    UserInfo = UserInfo.first()
    OperateLog.successlog(request=request,op_type='查询',op_message="查询用户%s详细信息" % UserInfo.username)
    return render(request,'user/detail.html',{'user':UserInfo})

# 用户登出
def LogOut(request):
    if request.user:
        OperateLog.successlog(request=request,op_type='登出',op_message="用户%s退出登录" % request.user)
        logout(request)
        
    return redirect('/login/')

# 删除用户
def UserDel(request,uid):
    try:
        op_user = request.user
        if not request.user.is_superuser:
            
            raise ValueError('无权限操作！')

        if op_user.uid == uid:
            
            raise ValueError('不能删除当前账号！')
        UserDB.objects.get(uid=uid).delete()
        resultdict =  {'result':0,'message':'删除用户成功'}   
        OperateLog.successlog(request=request,op_type='删除用户',op_message="删除用户%s成功" % UserDB.objects.get(uid=uid).username)
    except Exception as err:
        OperateLog.failedlog(request=request,op_type='删除用户',op_message="删除用户%s失败，%s" % (UserDB.objects.get(uid=uid).username, err))
        resultdict =  {'result':1,'message':'删除用户失败，%s' % err} 
    finally:
        return JsonResponse(resultdict)

# 修改用户 
class UserEdit(View):
    def get(self,request,uid):
        UserInfo = UserDB.objects.filter(uid=uid)
        if not UserInfo.count():
            return redirect(reverse('manager:userlist'))
        UserInfo = UserInfo.first()
        passwd_expireday = (UserInfo.passwd_expire_time - datetime.datetime.now()).days
        print(passwd_expireday)
        if passwd_expireday > 999 or passwd_expireday < 0:
            passwd_expireday = 0
        return render(request,'user/edit.html',{"user":UserInfo,"passwd_expireday":passwd_expireday})

    def post(self,request,uid):
        op_user = request.user
        print(op_user.is_superuser)
        print('修改用户',request.POST)
        try:
            if not op_user.is_superuser and op_user.uid != uid: # 如果不是管理员或者修改的不是自己的用户信息
                raise ValueError('无权限修改其他用户的信息')
            if not request.POST.get('username'):
                raise ValueError('缺少必填参数用户名')
            user = UserDB.objects.filter(uid=uid).first()
            email = request.POST.get('email','')
            phone = request.POST.get('phone','')
            username = request.POST.get('username','')
            superuser = request.POST.get('superuser','')
            userstat = request.POST.get('userstat','')
            passwd_expireday = request.POST.get('passwd_expireday','')
            data = {
                "email":email,
                "phone":phone,
                "username":username,
                "superuser":superuser,
                "userstat":userstat,
                "passwd_expireday":passwd_expireday,

            }
            print(data)
            success,err = reExpression.UserRe(**data)

            if not success:
                raise ValueError('参数校验错误，%s' % err)
            if request.user.is_superuser:
                user.is_superuser=superuser
                user.is_active=userstat
                if passwd_expireday:
                    passwd_expire_time = datetime.datetime.now() + datetime.timedelta(days=int(passwd_expireday)) # 密码过期时间
                    data.update({"passwd_expire_time":passwd_expire_time})
                    user.passwd_expire_time=passwd_expire_time
            user.email=email
            user.phone=phone
            user.username=username
            user.save()
            resultdict = {'result':0,'message':'修改成功'}     
            OperateLog.successlog(request=request,op_type='编辑用户',op_message="修改用户%s信息成功。" % user.username)
        except Exception as err :
            resultdict = {'result':1,'message':'修改用户信息失败%s' % err}
            OperateLog.failedlog(request=request,op_type='编辑用户',op_message="修改用户%s信息失败,%s。" % (uid,err))
        finally:
            return JsonResponse(resultdict)
# 修改密码
class ChangePwd(View):
    def get(self,request,uid):
        return render(request,'user/changepwd.html')
    def post(self,request,uid):
        op_user = request.user
        if not op_user.is_superuser and op_user.uid != uid: # 如果不是管理员或者修改的不是自己的用户信息

            raise ValueError('无权限修改其他用户的信息')
        try:
            user = UserDB.objects.get(uid=uid)
            if not check_password(request.POST.get('currpassword'),user.password):
                raise ValueError('原密码错误，请重新输入')
            if request.POST.get("newpassword") !=  request.POST.get("confirmpassword"):
                raise ValueError('新密码和确认密码不一致，请重新输入！')
            user.set_password(request.POST.get("confirmpassword"))
            user.save()
            resultdict = {'result':0,'message':'修改密码成功'}
            OperateLog.successlog(request=request,op_type='编辑用户',op_message="修改用户%s信息成功。" % user.username)
        except Exception as err:
            resultdict = {'result':1,'message':'修改用户信息失败，%s' % err}
            OperateLog.failedlog(request=request,op_type='编辑用户',op_message="修改用户%s密码失败,%s。" % (uid,err))
        finally:
            return JsonResponse(resultdict)
# 创建用户
class CreateUser(View):
    def get(self,request):
        return render(request,'user/create.html')
    def post(self,request):
        try:
            if not request.user.is_superuser:
                raise ValueError('无权限创建用户！')
            username = request.POST.get('username','')
            password = request.POST.get('password','')
            passwd_expireday = request.POST.get('passwd_expireday','')
            confirmpassword = request.POST.get('confirmpassword','')
            superuser = request.POST.get('superuser',False)
            userstat = request.POST.get('userstat',True)
            email = request.POST.get('email','')
            phone = request.POST.get('phone','')
            if not all([username,password,confirmpassword]):
                raise ValueError("参数不符合要求")
            data= {
                "username":username,
                "password":password,
                "confirmpassword":confirmpassword,
                "email":email,
                "phone":phone,
                "is_superuser":superuser,
                "is_active":userstat,
                "passwd_expire_time":passwd_expireday,
                }
            print(data)
            success,err = reExpression.UserRe(**data)

            if not success:
                raise ValueError('参数校验错误，%s' % err)
            if passwd_expireday:
                passwd_expire_time = datetime.datetime.now() + datetime.timedelta(days=int(passwd_expireday)) # 密码过期时间
                data.update({"passwd_expire_time":passwd_expire_time})
            else:
                data.pop("passwd_expire_time")
            data.pop('confirmpassword')
            UserDB.objects.create_user(**data)
            OperateLog.successlog(request=request,op_type='创建用户',op_message="创建用户%s信息成功。" % username)
            resultdict = {'result':0,'message':'添加用户成功'}
        except Exception as err:
            print(err)
            resultdict = {'result':1,'message':'添加用户失败，%s' % err}
            OperateLog.failedlog(request=request,op_type='创建用户',op_message="创建用户失败,%s。" % (err))
        finally:
            return JsonResponse(resultdict)

# 系统管理
class SystemManager(View):
    def get(self,request):
        return render(request,'system.html',SystemInfo(request))
    def post(self,request):
       
        try:
            if not request.user.is_superuser:
                raise ValueError('无权限修改系统信息！')
            logimg = request.FILES.get('logoimg','')
            if logimg:
                path = os.path.join(settings.STATICFILES_DIRS[0],'image/' + 'logo.png')  # 上传文件本地保存路径， image是static文件夹下专门存放图片的文件夹
                with open(path,'wb') as wf:
                    wf.write(bytes(logimg.read()))
                message = '修改网站图标成功.'
                return JsonResponse({"result":0,"message":message})

            system_title = request.POST.get('title','')
            system_name = request.POST.get('systemname','')
            if not all([system_title,system_name]):
                raise ValueError('缺少必要的参数')
            systeminfo = SystemInfoDB.objects.all()
            if not systeminfo.count():
                SystemInfoDB.objects.create(system_title=system_title,system_name=system_name)
            else:
                systeminfo = systeminfo.first()
                systeminfo.system_title=system_title
                systeminfo.system_name=system_name
                systeminfo.save()
            resultdict = {'result':0,'message':'修改系统信息成功！'}
            OperateLog.successlog(request=request,op_type='创建用户',op_message="修改系统信息成功！%s,%s。" % (system_title,system_name))
        except Exception as err:
            print(err)
            resultdict = {'result':1,'message':'修改系统信息失败，%s' % err}
            OperateLog.failedlog(request=request,op_type='创建用户',op_message='修改系统信息失败，%s' % err)
        finally:
            return JsonResponse(resultdict)

# 系统日志
def SystemLogView(request):
    if not  request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return render(request,'log/systemlog.html')
    Systemlog = SystemLogDB.objects.all()
    SystemlogList = []
    for Slog in Systemlog:
        SystemlogList.append({'re_time': Slog.re_time,'re_user':Slog.re_user,'re_ip':Slog.re_ip,'re_url':Slog.re_url,'re_method': Slog.re_method,'access_time':Slog.access_time})
       

    SystemLogDict = {}
    SystemLogDict["data"] = SystemlogList
    OperateLog.successlog(request=request,op_type='查询',op_message="查询系统日志")
    return HttpResponse(json.dumps(SystemLogDict))

# 操作日志
def OperateLogView(request):
    if not  request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return render(request,'log/operatelog.html')
    OperateLogQ = OperateLogDB.objects.all()
    OperateLogList = []
    for Olog in OperateLogQ:
        OperateLogList.append({'create_time': Olog.create_time.strftime('%Y-%m-%d %H:%M:%S'),'op_user':Olog.op_user,'remote_ip':Olog.remote_ip,'op_type':Olog.op_type,'result': Olog.result,'op_message':Olog.op_message})
       

    OperateLogDict = {}
    OperateLogDict["data"] = OperateLogList
    OperateLog.successlog(request=request,op_type='查询',op_message="查询操作日志")
    print(OperateLogDict,'OperateLogDict=====')
    return HttpResponse(json.dumps(OperateLogDict))

def ChangeUserStatusView(request,uid,op_type):
    if op_type not in ['active','inactive']:
        raise ValueError('参数错误！')
    op_user = request.user
    try:
        if not op_user.is_superuser: # 如果不是管理员或者修改的不是自己的用户信息
            raise ValueError('无权限操作！')
        user = UserDB.objects.get(uid=uid)
        user.is_active = True if op_type == 'active' else False
        user.save()
        resultdict = {'result':0,'message':'修改用户状态成功！'}
        OperateLog.successlog(request=request,op_type='编辑用户',op_message="修改用户状态%s成功。" % user.username)
    except Exception as err:
        resultdict = {'result':1,'message':'修改用户状态失败，%s' % err}
        OperateLog.failedlog(request=request,op_type='编辑用户',op_message="修改用户%s状态失败，%s。" % (uid,err))
    finally:
        return JsonResponse(resultdict)
        