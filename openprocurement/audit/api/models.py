from couchdb_schematics.document import SchematicsDocument
from pyramid.security import Allow
from schematics.transforms import whitelist, blacklist
from openprocurement.api.utils import get_now
from openprocurement.api.models import Document
from openprocurement.api.models import schematics_embedded_role, schematics_default_role, IsoDateTimeType, ListType
from schematics.types import StringType, IntType, FloatType, BaseType
from schematics.types.serializable import serializable
from schematics.types.compound import ModelType, DictType
from openprocurement.api.models import Model, Period, Revision


# roles
plain_role = (blacklist('_attachments', 'revisions', 'dateModified') + schematics_embedded_role)
create_role = (blacklist('owner_token', 'owner', 'revisions', 'dateModified', 'datePublished', 'planID', 'doc_id', '_attachments') + schematics_embedded_role)
edit_role = (blacklist('owner_token', 'owner', '_attachments', 'revisions', 'dateModified', 'datePublished', 'doc_id', 'planID', 'mode', '_attachments') + schematics_embedded_role)
view_role = (blacklist('owner_token', '_attachments', 'revisions') + schematics_embedded_role)
listing_role = whitelist('dateModified', 'doc_id')
revision_role = whitelist('revisions')
Administrator_role = whitelist('status', 'mode', 'procuringEntity')


class Monitor(SchematicsDocument, Model):

    class Options:
        roles = {
            'plain': plain_role,
            'revision': revision_role,
            'create': create_role,
            'edit': edit_role,
            'view': view_role,
            'listing': listing_role,
            'Administrator': Administrator_role,
            'default': schematics_default_role,
        }

    def __local_roles__(self):
        return dict([('{}_{}'.format(self.owner, self.owner_token), 'plan_owner')])

    # fields
    documents = ListType(ModelType(Document), default=list())  # All documents and attachments related to the item.

    tenderID = StringType()
    mode = StringType(choices=['test'])  # flag for test data ?

    dateModified = IsoDateTimeType()
    datePublished = IsoDateTimeType(default=get_now)
    owner_token = StringType()
    owner = StringType()
    revisions = ListType(ModelType(Revision), default=list())

    __name__ = ''

    def __acl__(self):
        acl = [
            # (Allow, '{}_{}'.format(i.owner, i.owner_token), 'create_award_complaint')
            # for i in self.bids
        ]
        acl.extend([
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_plan'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'upload_plan_documents'),
        ])
        return acl

    def __repr__(self):
        return '<%s:%r@%r>' % (type(self).__name__, self.id, self.rev)

    @serializable(serialized_name='id')
    def doc_id(self):
        """A property that is serialized by schematics exports."""
        return self._id

    def import_data(self, raw_data, **kw):
        """
        Converts and imports the raw data into the instance of the model
        according to the fields in the model.
        :param raw_data:
            The data to be imported.
        """
        data = self.convert(raw_data, **kw)
        del_keys = [k for k in data.keys() if data[k] == self.__class__.fields[k].default or data[k] == getattr(self, k)]
        for k in del_keys:
            del data[k]

        self._data.update(data)
        return self
