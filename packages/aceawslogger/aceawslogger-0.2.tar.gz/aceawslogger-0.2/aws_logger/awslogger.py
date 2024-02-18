import logging
import json
import copy
import uuid
import os
import boto3
from datetime import datetime


class AWSLogger:
    _source_type = "lambda"

    def __init__(
        self,
        team,
        workload,
        component,
        event,
        context,
        runtime_version=None,
        runtime="python",
    ):
        # Defined Runtime Env Variables: https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html#configuration-envvars-runtime
        region = os.getenv("AWS_REGION", "unspecified")
        memory_size = os.getenv("AWS_LAMBDA_FUNCTION_MEMORY_SIZE", "unspecified")

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/list_tags.html
        lambda_client = boto3.client("lambda")
        list_tags_response = lambda_client.list_tags(
            Resource=context.invoked_function_arn
        )
        tags = list_tags_response.get(
            "Tags", {}
        )  # returns empty object if Tags don't exist

        version = tags.get("ace:version", "unspecified")
        environment = tags.get("ace:environment", "unspecified")
        data_profile = tags.get("ace:data-profile", "confidential")
        department = tags.get("ace:department", "ebiz")

        correlation_id = event.get("headers", {}).get(
            "X-Ace-Correlation-Id", ""
        ).strip() or str(uuid.uuid4())
        session_id = event.get("headers", {}).get(
            "X-Ace-Session-Id", ""
        ).strip() or str(uuid.uuid4())
        current_utc_timestamp = str(datetime.utcnow())

        self.meta = {
            "ace:team": team,
            "ace:workload": workload,
            "ace:component": component,
            "ace:runtime": runtime,
            "ace:runtime:version": runtime_version,
            "ace:source-type": AWSLogger._source_type,
            "aws:lambda:function-arn": context.invoked_function_arn,
            "aws:lambda:function-name": context.function_name,
            "aws:lambda:request-id": context.aws_request_id,
            "ace:correlation-id": correlation_id,
            "ace:session-id": session_id,
            "ace:environment": environment,
            "ace:region": region,
            "aws:lambda:memory-size": memory_size,
            "ace:version": version,
            "ace:data-profile": data_profile,
            "ace:department": department,
            "log:timestamp": current_utc_timestamp,
        }

        self.ace_tags = {}
        logging.getLogger().setLevel(logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def info(self, message, data=None):
        log_data = self.get_log("info", message, data)
        self.logger.info(log_data)

    def debug(self, message, data=None):
        log_data = self.get_log("debug", message, data)
        self.logger.debug(log_data)

    def warn(self, message, data=None):
        log_data = self.get_log("warning", message, data)
        self.logger.warning(log_data)

    def error(self, message, data=None):
        log_data = self.get_log("error", message, data)
        self.logger.error(log_data)

    def get_log(self, level, message, data=None):
        result = {"log:level": level, **self.meta, "log:message": message}
        if data:
            result["log:message:data"] = self.get_json(data)
        return json.dumps(result)

    @staticmethod
    def get_json(data):
        try:
            return json.dumps(data)
        except Exception as e:
            print(e)
            return (
                "Logger Error: Issue running dumps on JSON data (get_json method). Data: "
                + data
            )
