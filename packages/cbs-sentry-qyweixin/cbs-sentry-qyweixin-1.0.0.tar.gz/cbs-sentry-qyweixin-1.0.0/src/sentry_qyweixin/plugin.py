# coding: utf-8

import json

from sentry.plugins.bases.notify import NotificationPlugin

import sentry_qyweixin
from .forms import QYWeixinOptionsForm

from sentry.utils.safe import safe_execute
from sentry.http import safe_urlopen
from sentry.integrations import FeatureDescription, IntegrationFeatures

QYWeixin_API = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={token}"


class QYWeixinPlugin(NotificationPlugin):
    """
    Sentry plugin to send error counts to QYWeixin.
    """
    author = 'ansheng'
    author_url = 'https://github.com/anshengme/sentry-dingding'
    version = sentry_qyweixin.VERSION
    description = 'Send error counts to DingDing.'
    resource_links = [
        ('Source', 'https://github.com/anshengme/sentry-dingding'),
        ('Bug Tracker', 'https://github.com/anshengme/sentry-dingding/issues'),
        ('README', 'https://github.com/anshengme/sentry-dingding/blob/master/README.md'),
    ]

    slug = 'QYWeixin'
    title = 'QYWeixin'
    conf_key = slug
    conf_title = title
    project_conf_form = QYWeixinOptionsForm
    feature_descriptions = [
        FeatureDescription(
            """
            Configure rule based outgoing HTTP POST requests from Sentry.
            """,
            IntegrationFeatures.ALERT_RULE,
        )
    ]
    def is_configured(self, project, **kwargs):
        """
        Check if plugin is configured.
        """
        return bool(self.get_option('access_token', project))

    def notify_users(self, group, event, triggering_rules, fail_silently=False, **kwargs):
        safe_execute(self.send_qyweixin, group, event,  _with_transaction=False)

    def send_qyweixin(self, group, event, **kwargs):
        """
        Process error.
        """
        if not self.is_configured(group.project):
            return

        if group.is_ignored():
            return

        access_token = self.get_option('access_token', group.project)
        ding_title = self.get_option('title', group.project)
        send_url = QYWeixin_API.format(token=access_token)
        title = u"{title} from {project}".format(
            title=ding_title,
            project=event.project.slug
        )

        stacktrace = ''
        for stack in event.get_raw_data().get('stacktrace', { 'frames': [] }).get('frames', []):
            stacktrace += u"{filename} in {method} at line {lineno}\n".format(
                filename=stack['filename'],
                method=stack['function'],
                lineno=stack['lineno']
            )

        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": u"#### {title} \n > {message} \n {detail} \n [View Detail]({url})".format(
                    title=title,
                    detail=stacktrace,
                    message=event.title or event.message,
                    url=u"{}events/{}/".format(group.get_absolute_url(), event.event_id),
                )
            }
        }
        return safe_urlopen(
            method="POST",
            url=send_url,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
