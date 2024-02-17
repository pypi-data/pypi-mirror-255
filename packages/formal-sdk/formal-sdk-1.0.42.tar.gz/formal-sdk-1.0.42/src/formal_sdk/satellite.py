import grpc


from .gen.admin.v1.satellite_pb2 import (
	CreateSatelliteRequest,
	CreateSatelliteResponse,
	GetSatelliteByIdRequest,
	GetSatelliteByIdResponse,
	GetSatellitesRequest,
	GetSatellitesResponse,
	GetSatelliteApiKeyRequest,
	GetSatelliteApiKeyResponse,
	UpdateSatelliteRequest,
	UpdateSatelliteResponse,
	DeleteSatelliteRequest,
	DeleteSatelliteResponse,
	SatelliteOnlineInstance,
	GetOnlineInstancesBySatelliteIdRequest,
	GetOnlineInstancesBySatelliteIdResponse,
)

from .gen.admin.v1.satellite_pb2_grpc import SatelliteServiceStub
class SatelliteService:
	def __init__(self, base_url, token):
		self.base_url = base_url
		self.channel = grpc.secure_channel(self.base_url, grpc.ssl_channel_credentials())
		self.stub = SatelliteServiceStub(self.channel)
		self.headers = [('x-api-key', token)]

	def CreateSatellite(self, request: CreateSatelliteRequest) -> CreateSatelliteResponse:
		return self.stub.CreateSatellite(request, metadata=self.headers)

	def GetSatelliteById(self, request: GetSatelliteByIdRequest) -> GetSatelliteByIdResponse:
		return self.stub.GetSatelliteById(request, metadata=self.headers)

	def GetSatellites(self, request: GetSatellitesRequest) -> GetSatellitesResponse:
		return self.stub.GetSatellites(request, metadata=self.headers)

	def GetSatelliteApiKey(self, request: GetSatelliteApiKeyRequest) -> GetSatelliteApiKeyResponse:
		return self.stub.GetSatelliteApiKey(request, metadata=self.headers)

	def GetOnlineInstancesBySatelliteId(self, request: GetOnlineInstancesBySatelliteIdRequest) -> GetOnlineInstancesBySatelliteIdResponse:
		return self.stub.GetOnlineInstancesBySatelliteId(request, metadata=self.headers)

	def UpdateSatellite(self, request: UpdateSatelliteRequest) -> UpdateSatelliteResponse:
		return self.stub.UpdateSatellite(request, metadata=self.headers)

	def DeleteSatellite(self, request: DeleteSatelliteRequest) -> DeleteSatelliteResponse:
		return self.stub.DeleteSatellite(request, metadata=self.headers)

