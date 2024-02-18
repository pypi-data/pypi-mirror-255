from django.conf import settings
from django.templatetags.static import static

from mail_templated import EmailMessage

from .settings import appkit_settings
from .shortcuts import site_url_base

get_current_site = appkit_settings.CURRENT_SITE_ACCESSOR


class AppkitEmailMessage(EmailMessage):
    sender = settings.DEFAULT_FROM_EMAIL_SENDER

    def __init__(self, template_name=None, site=None, context=None, *args, **kwargs):
        email_context = dict(context) if context else {}

        app_site_url = site_url_base(None)
        email_context.update({
            'app_name': settings.PROJECT_NAME,
            'app_site_url': app_site_url,
            'app_icon_url': f'{app_site_url}{static("images/icon/android-chrome-192x192.png")}',
        })

        if site:
            email_context.update({
                'site_name': site.name,
                'site_url': site_url_base(site),
            })            
            if site.profile.icon:
                email_context['site_icon_url'] = site.profile.icon.image.thumbnail['192x192']

        super().__init__(template_name, email_context, *args, **kwargs)

    def send(self, *args, **kwargs):
        if not self.sender and 'site' in self.context:
            self.sender = self.context['site'].name

        self.from_email = f"{self.sender} <{self.from_email}>"

        self.to = list(*args)
        self.cc = kwargs.pop('cc', [])
        self.bcc = kwargs.pop('bcc', [])
        self.reply_to = kwargs.pop('reply_to', [])
                
        self.context['allow_reply'] = True if self.reply_to else False

        super(AppkitEmailMessage, self).send(*args, **kwargs)
