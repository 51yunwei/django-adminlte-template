import re
class reExpression:
    def re_username(istr):
        return bool(istr.isalnum() and len(istr) >= 5)
    def re_password(istr):
        return bool(re.search(r'[a-zA-Z]+', istr) and re.search(r'\d+', istr) and len(istr) > 8 and re.search(r'[!@#\$%\^&\*\(\)-_=+{};:,<.>\?]', istr))
    def re_email(istr):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, istr))
    def re_phone(istr):
        pattern = r'^\+?[0-9]{10,15}$'
        return bool(re.match(pattern, istr))
    def re_passwd_expireday(istr):
        try:
            if int(istr)>=0 and int(istr)<=999: 
                result = True
            else:
                result = False
        except:
            result = False
        finally:
            return result
    def re_switch_button(istr):
        return bool(istr in ['True','False'])


    @classmethod
    def UserRe(cls,**kwargs):
        try:
            if kwargs.get('password'):
                if not cls.re_password(kwargs.get('password')):
                    raise ValueError('密码不符合复杂度要求！')
                if not kwargs.get('confirmpassword'):
                    raise ValueError('两次密码输入不一致1')
                if kwargs.get('password') != kwargs.get('confirmpassword'):
                    raise ValueError('两次密码输入不一致2')
            
            if kwargs.get('username'):
                if not cls.re_username(kwargs.get('username')):
                    raise ValueError('用户名不符合要求')
            
            if kwargs.get('email'):
                if not cls.re_email(kwargs.get('email')):
                    raise ValueError('邮箱参数不符合要求')
            
            if kwargs.get('passwd_expireday'):
                if not cls.re_passwd_expireday(kwargs.get('passwd_expireday')):
                    raise ValueError('密码过期时间设置不符合要求')
                
            if kwargs.get('phone'):
                if not cls.re_phone(kwargs.get('phone')):
                    raise ValueError('手机号码参数不符合要求')
            if kwargs.get('superuser'):
                if not cls.re_switch_button(kwargs.get('superuser')):
                    raise ValueError('参数不符合要求')
            if kwargs.get('userstat'):
                if not cls.re_switch_button(kwargs.get('userstat')):
                    raise ValueError('参数不符合要求')
            return (True,'校验通过')
        except Exception as err:
            return (False,err)
        