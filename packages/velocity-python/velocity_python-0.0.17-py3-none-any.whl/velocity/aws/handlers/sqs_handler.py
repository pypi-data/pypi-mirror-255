from velocity.misc.format import to_json
import json
import sys
import os
import traceback
from velocity.aws import DEBUG


class SqsHandler:
    def __init__(self, aws_event, aws_context):
        self.aws_event = aws_event
        self.aws_context = aws_context
        self.serve_action_default = True
        self.skip_action = False

    def log(self, tx, message, function=None):
        if not function:
            function = "<Unknown>"
            idx = 0
            while True:
                try:
                    temp = sys._getframe(idx).f_code.co_name
                except ValueError as e:
                    break
                if temp in ["x", "log", "_transaction"]:
                    idx += 1
                    continue
                function = temp
                break

        data = {
            "app_name": os.environ["ProjectName"],
            "referer": "SQS",
            "user_agent": "QueueHandler",
            "device_type": "Lambda",
            "function": function,
            "message": message,
            "sys_modified_by": "lambda:BackOfficeQueueHandler",
        }
        tx.table("sys_log").insert(data)

    def serve(self, tx):
        records = self.aws_event.get("Records", [])
        for record in records:
            attrs = record.get("attributes")
            try:
                postdata = {}
                if record.get("body"):
                    postdata = json.loads(record.get("body"))
                if hasattr(self, "beforeAction"):
                    self.beforeAction(attrs=attrs, postdata=postdata)
                actions = []
                action = postdata.get("action")
                if action:
                    actions.append(
                        f"on action {action.replace('-', ' ').replace('_', ' ')}".title().replace(
                            " ", ""
                        )
                    )
                if self.serve_action_default:
                    actions.append("OnActionDefault")
                for action in actions:
                    if self.skip_action:
                        return
                    if hasattr(self, action):
                        getattr(self, action)(attrs=attrs, postdata=postdata)
                        break
                if hasattr(self, "afterAction"):
                    self.afterAction(attrs=attrs, postdata=postdata)
            except Exception as e:
                if hasattr(self, "onError"):
                    self.onError(
                        attrs=attrs,
                        postdata=postdata,
                        exc=e.__class__.__name__,
                        tb=traceback.format_exc(),
                    )

    def OnActionDefault(self, tx, attrs, postdata):
        print(
            f"""
            [Warn] Action handler not found. Calling default action `SqsHandler.OnActionDefault` with the following parameters for attrs, and postdata:
            attrs: {str(attrs)}
            postdata: {str(postdata)}
            """
        )
