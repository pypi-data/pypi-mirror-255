import traceback, os
from datetime import datetime
from slack_sdk.webhook import WebhookClient
from flask import g
from flask_log_request_id import current_request_id

class SlackErrorNotification(WebhookClient):
    
    def __init__(self, slack_webhook, project_name, env):
        super().__init__(slack_webhook)
        self.project_name = project_name
        self.env = env

    def custom_message_context(self):
        """
        追加自定义的内容
        """
        account_name = g.get('account_name', None)
        request_id = current_request_id()
        result = traceback.extract_stack()
        caller = result[len(result) - 3]
        caller_list = str(caller).split(',')
        file_path_of_caller = caller_list[0].lstrip('<FrameSummary file ')

        _line = caller_list[1].split()[1]
        _base_dir = os.getcwd()
        module_line = "%s:%s" % (file_path_of_caller[len(_base_dir):], _line)
        msg = "%s | %s | %s" % (request_id, module_line, account_name)
        return msg
        
    def send_message(self, message, error_type):

        now = datetime.now()
        current_datetime = now.strftime("%Y-%m-%d %H:%M:%S")

        try:
            log_message = " | " + self.custom_message_context() + " | "
        except:
            log_message = " | "

        slack_err_msg = current_datetime + log_message + message

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