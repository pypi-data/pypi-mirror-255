from datetime import datetime
from typing import Optional

from LOGS.Auxiliary.Decorators import Endpoint
from LOGS.Entities.LabNotebookEntryRelations import LabNotebookEntryRelations
from LOGS.Entity.EntityMinimalWithIntId import EntityMinimalWithIntId
from LOGS.Entity.EntityWithIntId import IEntityWithIntId
from LOGS.Interfaces.ICreationRecord import ICreationRecord
from LOGS.Interfaces.IModificationRecord import IModificationRecord
from LOGS.Interfaces.INamedEntity import INamedEntity
from LOGS.Interfaces.IRelatedEntity import IRelatedEntity
from LOGS.Interfaces.ISoftDeletable import ISoftDeletable
from LOGS.LOGSConnection import LOGSConnection


@Endpoint("lab_notebook_entries")
class LabNotebookEntry(
    IEntityWithIntId,
    IRelatedEntity[LabNotebookEntryRelations],
    INamedEntity,
    ICreationRecord,
    IModificationRecord,
    ISoftDeletable,
):
    _relationType = type(LabNotebookEntryRelations)

    _version: Optional[int]
    _labNotebook: Optional[EntityMinimalWithIntId]
    _labNotebookExperiment: Optional[EntityMinimalWithIntId]
    _entryDate: Optional[datetime]

    def __init__(
        self,
        ref=None,
        id: Optional[int] = None,
        connection: Optional[LOGSConnection] = None,
    ):
        """Represents a connected LOGS entity type"""
        self._version = None
        self._labNotebook = None
        self._labNotebookExperiment = None
        self._entryDate = None

        super().__init__(ref=ref, id=id, connection=connection)

    def fromDict(self, ref, formatDict=None) -> None:
        if isinstance(ref, dict):
            if "name" in ref:
                ref["name"] = ref["name"].replace(" > ", "_")

        super().fromDict(ref, formatDict)

    @property
    def version(self) -> Optional[int]:
        return self._version

    @version.setter
    def version(self, value):
        self._version = self.checkAndConvertNullable(value, int, "version")

    @property
    def labNotebook(self) -> Optional[EntityMinimalWithIntId]:
        return self._labNotebook

    @labNotebook.setter
    def labNotebook(self, value):
        self._labNotebook = self.checkAndConvertNullable(
            value, EntityMinimalWithIntId, "labNotebook"
        )

    @property
    def labNotebookExperiment(self) -> Optional[EntityMinimalWithIntId]:
        return self._labNotebookExperiment

    @labNotebookExperiment.setter
    def labNotebookExperiment(self, value):
        self._labNotebookExperiment = self.checkAndConvertNullable(
            value, EntityMinimalWithIntId, "labNotebookExperiment"
        )

    @property
    def entryDate(self) -> Optional[datetime]:
        return self._entryDate

    @entryDate.setter
    def entryDate(self, value):
        self._entryDate = self.checkAndConvertNullable(value, datetime, "entryDate")
