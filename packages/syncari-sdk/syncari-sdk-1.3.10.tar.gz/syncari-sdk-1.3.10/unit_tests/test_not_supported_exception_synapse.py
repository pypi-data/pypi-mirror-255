
# pylint: disable=missing-class-docstring, import-error, missing-function-docstring
import json
from syncari.models import *
from syncari.rest.client import NotSupportedException
from syncari.synapse.abstract_synapse import Synapse

class MockSynapse(Synapse):

    def __print(self, funcname, request):
        self.logger.info(funcname)
        self.logger.info(request)
        print()

    def test(self):
        return self.connection

    def synapse_info(self):
        return SynapseInfo(
            name='test_synapse',category='crm',
            metadata=UIMetadata(displayName='Test Synapse', helpUrl='https://support.syncari.com'),
            supportedAuthTypes=[AuthMetadata(authType=AuthType.BASIC_TOKEN)],
            configuredFields=[AuthField(name='CRM ID')])

    def describe(self, desc_request):
        self.__print(self.describe.__name__, desc_request)
        schemas = []
        mock_attr = Attribute.parse_obj({'apiName':'MockAttr','displayName':'MockAttrDisplayName'})
        schemas.append(Schema.parse_obj({'apiName':'MockSchema','displayName':'MockDisplayName','attributes':[mock_attr]}))
        return schemas

    def read(self, sync_request):
        self.__print(self.read.__name__, sync_request)
        watermark = sync_request.watermark
        eds = []
        eds.append(Record.parse_obj({'name':'MockRecord','values':{'key':'val'}}))
        return ReadResponse(watermark=watermark,data=eds)

    def get_by_id(self, sync_request):
        return super().get_by_id(sync_request)

    def create(self, sync_request):
        return super().raise_not_supported_exception()

    def update(self, sync_request):
        return Synapse.raise_not_supported_exception(self)

    def delete(self, sync_request):
        return self.raise_not_supported_exception()

    def extract_webhook_identifier(self, webhook_request):
        raise NotSupportedException(error_response=None)

    # status_code is not considered and always return 405
    def process_webhook(self, webhook_request):
        raise NotSupportedException(error_response=ErrorResponse(message='Custom Operation process_webhook is not supported', status_code=400))

# Check super class error
def test_get_synapse_request():
    synapse_request = Request(type=RequestType.GET_BY_ID,
        connection=get_connection(),
        body=SyncRequest(
            entity=Schema(apiName='test',displayName='Test',attributes=[]), 
            watermark=Watermark(start=0, end=0))).json()
    synapse = MockSynapse(synapse_request)
    resp = synapse.execute()
    assert resp is not None
    err_resp = ErrorResponse.parse_raw(resp)
    assert err_resp.status_code == 405
    assert err_resp.message == 'Operation RequestType.GET_BY_ID is not supported'

# Call the parent method by Super()
def test_create_synapse_request():
    synapse_request = Request(type=RequestType.CREATE,
                              connection=get_connection(),
                              body=SyncRequest(
                                  entity=Schema(apiName='test',displayName='Test',attributes=[]),
                                  watermark=Watermark(start=0, end=0))).json()
    synapse = MockSynapse(synapse_request)
    resp = synapse.execute()
    assert resp is not None
    err_resp = ErrorResponse.parse_raw(resp)
    assert err_resp.status_code == 405
    assert err_resp.message == 'Operation RequestType.CREATE is not supported'

# Call the parent method by Class reference
def test_update_synapse_request():
    synapse_request = Request(type=RequestType.UPDATE,
                              connection=get_connection(),
                              body=SyncRequest(
                                  entity=Schema(apiName='test',displayName='Test',attributes=[]),
                                  watermark=Watermark(start=0, end=0))).json()
    synapse = MockSynapse(synapse_request)
    resp = synapse.execute()
    assert resp is not None
    err_resp = ErrorResponse.parse_raw(resp)
    assert err_resp.status_code == 405
    assert err_resp.message == 'Operation RequestType.UPDATE is not supported'


# Call the parent method by self reference
def test_delete_synapse_request():
    synapse_request = Request(type=RequestType.DELETE,
                              connection=get_connection(),
                              body=SyncRequest(
                                  entity=Schema(apiName='test',displayName='Test',attributes=[]),
                                  watermark=Watermark(start=0, end=0))).json()
    synapse = MockSynapse(synapse_request)
    resp = synapse.execute()
    assert resp is not None
    err_resp = ErrorResponse.parse_raw(resp)
    assert err_resp.status_code == 405
    assert err_resp.message == 'Operation RequestType.DELETE is not supported'

# Check Custom message error
def test_process_webhook_request():
    synapse_request = Request(type=RequestType.PROCESS_WEBHOOK,
                              connection=get_connection(),
                              body=WebhookRequest(body=json.dumps([{'key':'value'}]))).json()
    synapse = MockSynapse(synapse_request)
    resp = synapse.execute()
    assert resp is not None
    err_resp = ErrorResponse.parse_raw(resp)
    assert err_resp.status_code == 405
    assert err_resp.message == 'Custom Operation process_webhook is not supported'

# Check default exception message
def test_extract_webhook_identifier():
    synapse_request = Request(type=RequestType.EXTRACT_WEBHOOK_IDENTIFIER,
                              connection=get_connection(),
                              body=WebhookRequest(body=json.dumps([{'key':'value'}]))).json()
    synapse = MockSynapse(synapse_request)
    resp = synapse.execute()
    assert resp is not None
    err_resp = ErrorResponse.parse_raw(resp)
    assert err_resp.status_code == 405
    assert err_resp.message == 'Operation is not supported'

def get_connection():
    authConfig=AuthConfig(endpoint='http://endpoint.com')
    connection = Connection(id='1', name='name', authConfig=authConfig, idFieldName='idfield', watermarkFieldName='watermarkfield', 
        endpoint='http://endpoint.com', createdAtFieldName='createdfield', updatedAtFieldName='updatedfield', oAuthRedirectUrl='http://redirect.com')
    return connection
