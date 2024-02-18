import grpc


from .gen.admin.v1.integration_mfa_pb2 import (
	ListIntegrationMfasRequest,
	ListIntegrationMfasResponse,
	GetIntegrationMfaByIdRequest,
	GetIntegrationMfaByIdResponse,
	CreateIntegrationMfaRequest,
	CreateIntegrationMfaResponse,
	DeleteIntegrationMfaRequest,
	DeleteIntegrationMfaResponse,
	UpdateIntegrationMfaRequest,
	UpdateIntegrationMfaResponse,
	IntegrationMfa,
)

from .gen.admin.v1.integration_mfa_pb2_grpc import IntegrationMfaServiceStub
class IntegrationMfaService:
	def __init__(self, base_url, token):
		self.base_url = base_url
		self.channel = grpc.secure_channel(self.base_url, grpc.ssl_channel_credentials())
		self.stub = IntegrationMfaServiceStub(self.channel)
		self.headers = [('x-api-key', token)]

	def ListIntegrationMfas(self, request: ListIntegrationMfasRequest) -> ListIntegrationMfasResponse:
		return self.stub.ListIntegrationMfas(request, metadata=self.headers)

	def GetIntegrationMfaById(self, request: GetIntegrationMfaByIdRequest) -> GetIntegrationMfaByIdResponse:
		return self.stub.GetIntegrationMfaById(request, metadata=self.headers)

	def UpdateIntegrationMfa(self, request: UpdateIntegrationMfaRequest) -> UpdateIntegrationMfaResponse:
		return self.stub.UpdateIntegrationMfa(request, metadata=self.headers)

	def CreateIntegrationMfa(self, request: CreateIntegrationMfaRequest) -> CreateIntegrationMfaResponse:
		return self.stub.CreateIntegrationMfa(request, metadata=self.headers)

	def DeleteIntegrationMfa(self, request: DeleteIntegrationMfaRequest) -> DeleteIntegrationMfaResponse:
		return self.stub.DeleteIntegrationMfa(request, metadata=self.headers)

