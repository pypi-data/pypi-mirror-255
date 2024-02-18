import json

from th2_common.schema.event.event_batch_router import EventBatchRouter
from th2_common.schema.grpc.router.grpc_router import GrpcRouter
from th2_common_utils import create_event, create_event_id
from th2_grpc_common.common_pb2 import EventBatch

from run_one import Context
from run_one.action_handlers.abstract_action_handler import AbstractActionHandler
from run_one.processors.th2_processor import Th2ProcessorConfig
from run_one.util.util import Action, create_timestamp


class TH2EstoreHandler(AbstractActionHandler):

    def __init__(self, config: Th2ProcessorConfig, grpc_router: GrpcRouter, event_router: EventBatchRouter,
                 *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._config = config
        self._event_router: EventBatchRouter = event_router

    def process(self, action: Action):
        if parent_event_id := Context.get('parent_event_id'):
            message_type = action.extra_data['MessageType']
            action_event_id = create_event_id(book_name=self._config.book, scope=self._config.scope,
                                              start_timestamp=create_timestamp(self._config.timestamp_shift))
            action_event = EventBatch(events=[create_event(name=f'Store {message_type} action event',
                                                           event_id=action_event_id,
                                                           parent_id=parent_event_id,
                                                           event_type='Action event',
                                                           body=json.dumps(action.row).encode('utf-8'))])
            self._event_router.send(action_event)
