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