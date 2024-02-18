from datetime import datetime
from slack_sdk.webhook import WebhookClient
from stdLogger import std_logger as logger

class SlackErrorNotification(object):

    def __new__(cls, slack_webhook, project_name, env):
        slack_webhook = WebhookClient(slack_webhook)

        return slack_webhook
    
    def __init__(self, slack_webhook, project_name, env):
        self.slack_webhook = slack_webhook
        self.project_name = project_name
        self.env = env
        
    def send_slack_message(self, message, error_type):

        now = datetime.now()
        current_datetime = now.strftime("%Y-%m-%d %H:%M:%S")

        slack_err_msg = current_datetime + " | " + logger.custom_message_context(
        ) + " | %s" % message
        
        self.send(
            text=error_type + " has occurred in " + self.project_name + " " + self.env,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type":
                        "mrkdwn",
                        "text":
                        ":poggies: *" + error_type + "* has occurred in *" +
                        self.project_name + "* *" + self.env + "*"
                    }
                },
                {
                    "type":
                    "section",  # Use a code block to display the error message
                    "text": {
                        "type": "mrkdwn",
                        "text": "```" + slack_err_msg + "```"
                    }
                }
            ])