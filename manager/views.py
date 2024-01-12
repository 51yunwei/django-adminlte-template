from django.shortcuts import render,redirect
from django.views import View
import json
from django.contrib.auth import authenticate,login,logout
from manager.models import UserDB,SystemInfoDB
from django.urls import reverse
from django.http import JsonResponse,HttpResponse
from django.contrib.auth.hashers import check_password
from system.reexpression import reExpression
from system.systeminfo import SystemInfo
from system.operatelog import OperateLog
# Create your views here.
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
        # print('post next====',request.POST.get('next',''),request.POST)
        user = authenticate(username=username,password=password)
        
        if user:
            login(request,user)
            request.session["username"] = username
            request.session.set_expiry(0)  # 关闭浏览器就过期
            OperateLog(request=request,op_type='登录',op_message="登录成功")
            return redirect(next_path)
        login_error_message = '用户名或密码错误'
        OperateLog(request=request,result=1,op_type='登录',op_message=login_error_message)
        print('登录失败')
        return render(request,'login.html',{'login_error_message':login_error_message})
def IndexView(request):
    return render(request,'base.html')

def UserIndex(request):
    return render(request,'user/index.html')
class UserManager(View):
    def get(self,request):
        # if not  request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        #     return render(request,'user/index.html')
        # print('not ajax request')
        UserInfo = UserDB.objects.all()
        # print(user)
        UserList = []
        for User in UserInfo:
            username = User.username
            create_time =User.create_time
            email = User.email
            phone = User.phone
            button = """<div style="display: block;text-align: center;margin: auto;">
            <a class="btn btn-primary btn-sm" href="{0}">
                                <i class="fas fa-folder">
                                </i>
                                详情
                            </a>
                            <a class="btn btn-info btn-sm" href="{1}">
                                <i class="fas fa-pencil-alt">
                                </i>
                                编辑
                            </a>
                            <a class="btn btn-danger btn-sm" data-url="{2}" data-user='{3}' data-toggle="modal" data-target="#mymodal">
                                <i class="fas fa-trash">
                                </i>
                                删除
                            </a>
            </div>
            """.format(reverse('manager:userdetail',kwargs={'uid':User.uid}),reverse('manager:useredit',kwargs={'uid':User.uid}),reverse('manager:userdel',kwargs={'uid':User.uid}),User.username)
            UserList.append({'username': User.username,'create_time':User.create_time.strftime('%Y-%m-%d %H:%M:%S'),'email':User.email,'phone': User.phone,'uid':str(User.uid),'button':button})
            print(username)

        UserDict = {}
        UserDict["data"] = UserList
        OperateLog(request=request,op_type='查询',op_message="查询用户列表")
        return HttpResponse(json.dumps(UserDict))

        # return render(request,'user/index.html',{'UserDict':UserList}) # template循环的时候使用key名称
    def post(self,request):
        return None

def UserDetail(request,uid):
    UserInfo = UserDB.objects.filter(uid=uid)
    if not UserInfo.count():
        OperateLog(request=request,op_type='查询',result=1,op_message="查询的用户不存在")
        return redirect(reverse('manager:userlist'))
    UserInfo = UserInfo.first()
    OperateLog(request=request,op_type='查询',result=1,op_message="查询用户%s详细信息" % UserInfo.username)
    return render(request,'user/detail.html')

def LogOut(request):
    if request.user:
        OperateLog(request=request,op_type='登出',op_message="用户%s退出登录" % request.user)
        logout(request)
        
    return redirect('/login/')

def UserDel(request,uid):
    try:
        op_user = request.user
        if not request.user.is_superuser:
            OperateLog(request=request,op_type='删除用户',result=1,op_message="删除用户失败，操作用户无权限。")
            raise ValueError('无权限操作！')

        if op_user.uid == uid:
            OperateLog(request=request,op_type='删除用户',result=1,op_message="删除用户失败，操作用户无权限。")
            raise ValueError('不能删除当前账号！')
        UserDB.objects.get(uid=uid).delete()
        resultdict =  {'result':0,'message':'删除用户成功'}   
        OperateLog(request=request,op_type='删除用户',op_message="删除用户%s成功" % UserDB.objects.get(uid=uid).username)
    except Exception as err:
        OperateLog(request=request,op_type='删除用户',result=1,op_message="删除用户%s失败，%s" % (UserDB.objects.get(uid=uid).username, err))
        resultdict =  {'result':1,'message':'删除用户失败，%s' % err} 
    finally:
        return JsonResponse(resultdict)
        
class UserEdit(View):
    def get(self,request,uid):
        UserInfo = UserDB.objects.filter(uid=uid)
        if not UserInfo.count():
            return redirect(reverse('manager:userlist'))
        UserInfo = UserInfo.first()
        return render(request,'user/edit.html')

    def post(self,request,uid):
        op_user = request.user
        if not op_user.is_superuser or op_user.uid != uid: # 如果不是管理员或者修改的不是自己的用户信息
            OperateLog(request=request,op_type='编辑用户',result=1,op_message="修改用户%s信息失败，操作用户无权限。" % uid)
            raise ValueError('无权限修改其他用户的信息')
        try:
            if not request.POST.get('username'):
                raise ValueError('缺少必填参数用户名')
            user = UserDB.objects.filter(uid=uid).first()
            user.email = request.POST.get('email','')
            user.phone = request.POST.get('phone','')
            user.username = request.POST.get('username','')
            user.save()
            resultdict = {'result':0,'message':'修改成功'}     
            OperateLog(request=request,op_type='编辑用户',op_message="修改用户%s信息成功。" % user.username)
        except Exception as err :
            resultdict = {'result':1,'message':'修改用户信息失败%s' % err}
            OperateLog(request=request,op_type='编辑用户',result=1,op_message="修改用户%s信息失败,%s。" % (uid,err))
        finally:
            return JsonResponse(resultdict)
class ChangePwd(View):
    def get(self,request,uid):
        return render(request,'user/changepwd.html')
    def post(self,request,uid):
        op_user = request.user
        if not op_user.is_superuser or op_user.uid != uid: # 如果不是管理员或者修改的不是自己的用户信息

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
            OperateLog(request=request,op_type='编辑用户',op_message="修改用户%s信息成功。" % user.username)
        except Exception as err:
            resultdict = {'result':1,'message':'修改用户信息失败，%s' % err}
            OperateLog(request=request,op_type='编辑用户',result=1,op_message="修改用户%s密码失败,%s。" % (uid,err))
        finally:
            return JsonResponse(resultdict)
class CreateUser(View):
    def get(self,request):
        return render(request,'user/create.html')
    def post(self,request):
        try:
            print(request.POST)
            username = request.POST.get('username','')
            password = request.POST.get('password','')
            confirmpassword = request.POST.get('confirmpassword','')
            email = request.POST.get('email','')
            phone = request.POST.get('phone','')
            
            if not all([username,password,confirmpassword]):
                raise ValueError('缺少必要的参数')
            if password != confirmpassword:
                raise ValueError('两次密码输入不一致')
            print('开始校验')
            if not reExpression.re_username(username) or not reExpression.re_password(password):
                raise ValueError('用户名或密码参数不符合要求')
            
            if email:
                if not reExpression.re_email(email):
                    raise ValueError('邮箱参数不符合要求')
            
            if phone:
                if not reExpression.re_phone(phone):
                    raise ValueError('手机号码参数不符合要求')
            print('校验通过')
            UserDB.objects.create(username=username,password=password,email=email,phone=phone)
            OperateLog(request=request,op_type='创建用户',op_message="创建用户%s信息成功。" % username)
            resultdict = {'result':0,'message':'添加用户成功'}
        except Exception as err:
            print(err)
            resultdict = {'result':1,'message':'添加用户失败，%s' % err}
            OperateLog(request=request,op_type='创建用户',result=1,op_message="创建用户失败,%s。" % (err))
        finally:
            return JsonResponse(resultdict)


class SystemManager(View):
    def get(self,request):
        return render(request,'system.html',SystemInfo(request))
    def post(self,request):
        print(request.POST)
        system_title = request.POST.get('title','')
        system_name = request.POST.get('systemname','')
        try:
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
            OperateLog(request=request,op_type='创建用户',op_message="修改系统信息成功！%s,%s。" % (system_title,system_name))
        except Exception as err:
            print(err)
            resultdict = {'result':1,'message':'修改系统信息失败，%s' % err}
            OperateLog(request=request,op_type='创建用户',result=1,op_message='修改系统信息失败，%s' % err)
        finally:
            return JsonResponse(resultdict)