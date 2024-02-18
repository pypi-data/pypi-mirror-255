import re
from typing import List, Type

from lumigo_core.triggers.trigger_parsing.apigw_parser import (
    ApiGatewayEventTriggerParser,
)
from lumigo_core.triggers.trigger_parsing.appsync_parser import (
    AppsyncEventTriggerParser,
)
from lumigo_core.triggers.trigger_parsing.cloudwatch_parser import (
    CloudwatchEventTriggerParser,
)
from lumigo_core.triggers.trigger_parsing.dynamodb_parser import (
    DynamoDBEventTriggerParser,
)
from lumigo_core.triggers.trigger_parsing.event_trigger_base import EventTriggerParser
from lumigo_core.triggers.trigger_parsing.eventbridge_parser import (
    EventbridgeEventTriggerParser,
)
from lumigo_core.triggers.trigger_parsing.kinesis_parser import (
    KinesisEventTriggerParser,
)
from lumigo_core.triggers.trigger_parsing.load_balancer_parser import (
    LoadBalancerEventTriggerParser,
)
from lumigo_core.triggers.trigger_parsing.s3_parser import S3EventTriggerParser
from lumigo_core.triggers.trigger_parsing.sns_parser import SnsEventTriggerParser
from lumigo_core.triggers.trigger_parsing.sqs_parser import SqsEventTriggerParser

EVENT_TRIGGER_PARSERS: List[Type[EventTriggerParser]] = [
    ApiGatewayEventTriggerParser,
    LoadBalancerEventTriggerParser,
    SnsEventTriggerParser,
    S3EventTriggerParser,
    SqsEventTriggerParser,
    KinesisEventTriggerParser,
    DynamoDBEventTriggerParser,
    CloudwatchEventTriggerParser,
    EventbridgeEventTriggerParser,
    AppsyncEventTriggerParser,
]
INNER_MESSAGES_MAGIC_PATTERN = re.compile(
    r"("
    + "|".join(
        parser.MAGIC_IDENTIFIER
        for parser in EVENT_TRIGGER_PARSERS
        if parser.MAGIC_IDENTIFIER
    )
    + ")"
)
