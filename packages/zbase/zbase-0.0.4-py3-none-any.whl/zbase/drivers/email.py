import yagmail
from typing import List, Dict
from ..env import getEnv, getEnvBool, getEnvInt


class SMTP(yagmail.SMTP):

    def __init__(self, user=None, password=None, host="smtp.gmail.com", port=None, smtp_starttls=None, smtp_ssl=True, smtp_set_debuglevel=0, smtp_skip_login=False, encoding="utf-8", oauth2_file=None, soft_email_validation=True, dkim=None, **kwargs):
        super().__init__(user, password, host, port, smtp_starttls, smtp_ssl, smtp_set_debuglevel, smtp_skip_login, encoding, oauth2_file, soft_email_validation, dkim, **kwargs)
    

    def sendTpl(self,to:str, subject:str, content:str, args:Dict):
        """
        send template email

        """
        subject = subject.format(**args)
        content = content.format(**args)
        return self.send(to=to, subject=subject, contents=content)
    
    def sendBatch(self,subject:str, content:str ,args:List[Dict]):
        """
        send batch email
        args = [{to:"x@gmai.com" , other args}]
        """
        for arg in args:
            self.sendTpl(to=arg['to'], subject=subject, content=content, args=arg)



def newSMTPEnv() -> SMTP:
    port = getEnvInt('SMTP_PORT', 465)
    starttls = getEnvBool('SMTP_STARTTLS', False)
    ssl = getEnvBool('SMTP_SSL', False)
    if starttls:
        ssl = False
        port = getEnvInt('SMTP_PORT', 587)
    elif ssl:
        starttls =False
        port = getEnvInt('SMTP_PORT', 465)

    return SMTP(user=getEnv('SMTP_USER'), password=getEnv('SMTP_PASSWORD'), host=getEnv('SMTP_HOST'), port=port, smtp_starttls=starttls, smtp_ssl=ssl, smtp_set_debuglevel=getEnvInt('SMTP_SET_DEBUGLEVEL', 0), smtp_skip_login=getEnvBool('SMTP_SKIP_LOGIN', False), encoding=getEnv('SMTP_ENCODING', 'utf-8'), oauth2_file=getEnv('SMTP_OAUTH2_FILE'), soft_email_validation=getEnvBool('SMTP_SOFT_EMAIL_VALIDATION', True), dkim=getEnv('SMTP_DKIM'))