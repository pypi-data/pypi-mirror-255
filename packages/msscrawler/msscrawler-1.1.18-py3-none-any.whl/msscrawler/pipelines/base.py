from ..mixins.database_mixin import DatabaseMixin
from ..mixins.message_connector_mixin import MessageConnectorMixin
from ..log.default import get_default_log


class BasePipeline(DatabaseMixin, MessageConnectorMixin):

    def __init__(self):
        DatabaseMixin.__init__(self)
        MessageConnectorMixin.__init__(self)

        self.logger = None

    def get_logger(self):
        if not self.logger:
            self.logger = get_default_log()

        return self.logger