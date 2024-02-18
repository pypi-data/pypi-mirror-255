from enum import Enum
from typing import TYPE_CHECKING, Any, List, Optional

from numpy import deprecate

from LOGS.Auxiliary.Decorators import Endpoint
from LOGS.Auxiliary.Exceptions import EntityCreatingException, LOGSException
from LOGS.Auxiliary.Tools import Tools
from LOGS.Entities.Dataset import Dataset
from LOGS.Entities.FileEntry import FileEntry
from LOGS.Entity.EntityConnector import EntityConnector
from LOGS.Entity.SerializeableContent import SerializeableClass
from LOGS.LOGSConnection import LOGSConnection, MultipartEntry

if TYPE_CHECKING:
    pass


class DatasetSourceType(Enum):
    ManualUpload = 0
    SFTPAutoload = 1
    ClientAutoload = 2
    APIUpload = 3


class DatasetUploadRequest(SerializeableClass):
    _typeMapper = {"files": FileEntry}

    def __init__(self, ref: Any = None):
        self.name: Optional[str] = None
        self.formatId: str = ""
        self.methodId: Optional[int] = None
        self.instrumentId: Optional[int] = None
        self.experimentId: Optional[int] = None
        self.sampleId: Optional[int] = None
        self.ownerId: Optional[int] = None
        self.projectIds: Optional[List[int]] = None
        self.organizationIds: Optional[List[int]] = None
        self.operatorIds: Optional[List[int]] = None
        self.equipmentIds: Optional[List[int]] = None
        self.autoloadBaseDir: str = ""
        self.relativeDir: str = ""
        self.dataSourceId: Optional[str] = None
        self.isViewableEntity: Optional[bool] = None
        self.files: List[FileEntry] = []
        self.filePathsAreAbsolute: Optional[bool] = True

        if isinstance(ref, Dataset) and ref.format:
            self.name = ref.name

            if ref.name:
                self.name = ref.name
            if ref.format:
                self.formatId = ref.format.id
            if ref.owner:
                self.ownerId = ref.owner.id
            if ref._files:
                self.files = ref._files
            if ref.method:
                self.methodId = ref.method.id
            if ref.instrument:
                self.instrumentId = ref.instrument.id
            if ref.experiment:
                self.experimentId = ref.experiment.id
            if ref.sampleId:
                self.sampleId = ref.sampleId
            if ref.owner:
                self.ownerId = ref.owner.id
            if ref.projects:
                self.projectIds = [p.id for p in ref.projects]
            if ref.operators:
                self.operatorIds = [o.id for o in ref.operators]
            if ref.equipments:
                self.equipmentIds = [e.id for e in ref.equipments]
            if ref.isViewableEntity:
                self.isViewableEntity = ref.isViewableEntity
            if ref._files:
                self.files = ref._files
            ref = None

        super().__init__(ref)

    @property
    @deprecate(new_name="formatId")
    def parserId(self):
        return self.formatId

    @parserId.setter
    @deprecate(new_name="formatId")
    def paserId(self, value):
        self.formatId = value


@Endpoint("datasets")
class DatasetCreator(EntityConnector):
    _request: DatasetUploadRequest = DatasetUploadRequest()
    _formatId: str
    _files: List[FileEntry]

    def __init__(self, connection: LOGSConnection, dataset: Dataset):
        self._connection = connection

        if not dataset:
            raise LOGSException("Cannot not create empty dataset")
        if not dataset._files:
            raise LOGSException("Cannot not create dataset without files")
        if not dataset.format or not dataset.format.id:
            raise LOGSException("Cannot not create dataset without a format field")

        self._formatId = dataset.format.id
        self._files = dataset._files
        self._request = self._getDatasetUploadRequest(dataset=dataset)

    def create(self):
        connection, endpoint = self._getConnectionData()

        multipart = [
            MultipartEntry(
                name="Dataset", fileName=None, content=self._request.toDict()
            )
        ]
        multipart.extend(
            [
                MultipartEntry(name="files", fileName=file.id, content=file)
                for file in self._files
            ]
        )

        data, errors = connection.postMultipartEndpoint(
            endpoint=endpoint + ["create"], data=multipart
        )
        if errors:
            raise EntityCreatingException(errors=errors)

        return Tools.checkAndConvert(data, dict, "dataset creation result")

    def _getDatasetUploadRequest(self, dataset: Dataset):
        # print("\n".join([f.fullPath for f in fileList]))
        if not self._files:
            raise LOGSException("Cannot not create dataset without files")
        if not self._formatId:
            raise LOGSException("Cannot not create dataset without a formatId")

        for file in self._files:
            file.addMtime()

        request = DatasetUploadRequest(dataset)

        return request
