from django.urls import path
from . import views
app_name='manager'
urlpatterns = [
    path('', views.IndexView),
    # path('user/',views.UserManagerView,name='userindex'),
    path('user/',views.UserManagerView,name='userlist'),
    path('login/',views.LoginView.as_view()),
    path('user/<uuid:uid>/',views.UserDetail,name='userdetail'),
    path('logout/',views.LogOut,name='logout'),
    path('user/<uuid:uid>/edit/',views.UserEdit.as_view(),name='useredit'),
    path('user/<uuid:uid>/changepwd/',views.ChangePwd.as_view(),name='changepwd'),
    path('user/create/',views.CreateUser.as_view(),name='usercreate'),
    path('user/<uuid:uid>/delete/',views.UserDel,name='userdel'),
    path('user/<uuid:uid>/<str:op_type>/',views.ChangeUserStatusView,name='userstatus'),
    path('system/',views.SystemManager.as_view(),name='system'),
    path('log/systemlog/',views.SystemLogView,name='systemlog'),
    path('log/operatelog/',views.OperateLogView,name='operatelog'),
    
]