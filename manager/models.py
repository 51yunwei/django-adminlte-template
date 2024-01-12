from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractUser
import uuid
# Create your models here.
# 自定义user，还需要在setting文件中配置AUTH_USER_MODELS
class UserDB(AbstractUser):
    uid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    username = models.CharField(max_length=15,verbose_name="用户名", unique=True)
    phone = models.CharField(max_length=11,verbose_name="手机号码", null=True,blank=True)
    email = models.EmailField(verbose_name='邮箱', null=True,blank=True)
    create_time = models.DateTimeField('创建时间',auto_now_add=True)
    update_time = models.DateTimeField('更新时间',auto_now=True)
    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.username
class SystemInfoDB(models.Model):
    system_title = models.CharField(max_length=128,verbose_name="网页title")
    system_name = models.CharField(max_length=128,verbose_name="站点名称")
    class Meta:
        verbose_name = '系统信息'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.system_name

class SystemLogDB(models.Model):
    """系统日志表"""

    id = models.AutoField(primary_key=True)
    re_time = models.CharField(max_length=32, verbose_name='请求时间')
    re_user = models.CharField(max_length=32, verbose_name='操作人')
    re_ip = models.CharField(max_length=32, verbose_name='请求IP')
    re_url = models.CharField(max_length=255, verbose_name='请求url')
    re_method = models.CharField(max_length=11, verbose_name='请求方法')
    re_content = models.TextField(null=True, verbose_name='请求参数')
    rp_content = models.TextField(null=True, verbose_name='响应参数')
    access_time = models.IntegerField(verbose_name='响应耗时/ms')

    class Meta:
        verbose_name = '系统日志'
        verbose_name_plural = verbose_name
class OperateLogDB(models.Model):
    """操作日志表"""
    Op_result_choices = (
        (0, '成功'),
        (1, '失败'),
    )
    uid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    create_time = models.DateTimeField('操作时间',auto_now_add=True)
    op_user = models.CharField(max_length=32, verbose_name='操作人')
    remote_ip = models.CharField(max_length=32, verbose_name='操作IP')
    op_type = models.CharField(max_length=255,verbose_name='操作结果',choices=Op_result_choices)
    result = models.CharField(max_length=11, verbose_name='操作结果')
    op_message = models.TextField(null=True, verbose_name='操作信息')
    
    class Meta:
        verbose_name = '操作日志'
        verbose_name_plural = verbose_name