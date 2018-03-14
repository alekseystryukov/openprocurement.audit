from openprocurement.api.utils import (
    context_unpack,
    decrypt,
    encrypt,
    get_now,
    generate_id,
    json_view,
    set_ownership,
    APIResourceListing
)
from openprocurement.audit.api.utils import (
    save_monitor,
    monitor_serialize,
    apply_patch,
    op_resource,
    APIResource
)
from openprocurement.audit.api.design import (
    monitors_real_by_dateModified_view,
    monitors_test_by_dateModified_view,
    monitors_by_dateModified_view,
    monitors_real_by_local_seq_view,
    monitors_test_by_local_seq_view,
    monitors_by_local_seq_view,
)
from openprocurement.audit.api.design import FIELDS
from pkg_resources import get_distribution
from logging import getLogger

PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)


VIEW_MAP = {
    u'': monitors_real_by_dateModified_view,
    u'test': monitors_test_by_dateModified_view,
    u'_all_': monitors_by_dateModified_view,
}
CHANGES_VIEW_MAP = {
    u'': monitors_real_by_local_seq_view,
    u'test': monitors_test_by_local_seq_view,
    u'_all_': monitors_by_local_seq_view,
}
FEED = {
    u'dateModified': VIEW_MAP,
    u'changes': CHANGES_VIEW_MAP,
}


@op_resource(name='Monitors', path='/monitors', description="Monitors resource description")
class MonitorsResource(APIResourceListing):

    def __init__(self, request, context):
        super(MonitorsResource, self).__init__(request, context)
        # params for listing
        self.VIEW_MAP = VIEW_MAP
        self.CHANGES_VIEW_MAP = CHANGES_VIEW_MAP
        self.FEED = FEED
        self.FIELDS = FIELDS
        self.serialize_func = monitor_serialize
        self.object_name_for_listing = 'Monitors'
        self.log_message_id = 'monitor_list_custom'

    @json_view(content_type="application/json", permission='create_monitor', validators=tuple())
    def post(self):
        monitor = self.request.validated['monitor']
        monitor.id = generate_id()

        set_ownership(monitor, self.request)
        self.request.validated['monitor'] = monitor
        self.request.validated['monitor_src'] = {}
        if save_monitor(self.request):
            LOGGER.info('Created monitor {}'.format(monitor.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'monitor_create'}, {'plan_id': monitor.id}))
            self.request.response.status = 201
            self.request.response.headers['Location'] = self.request.route_url('Monitor', plan_id=monitor.id)
            return {
                'data': monitor.serialize("view"),
                'access': {
                    'token': monitor.owner_token
                }
            }
