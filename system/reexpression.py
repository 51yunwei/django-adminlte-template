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