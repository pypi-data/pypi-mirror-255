# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import abc
from typing import Optional

from dyff.schema.platform import (
    Audit,
    Dataset,
    DataSource,
    EntityStatus,
    EntityStatusReason,
    Evaluation,
    InferenceService,
    InferenceSession,
    Labeled,
    Model,
    Report,
)


class CommandBackend(abc.ABC):
    @abc.abstractmethod
    def update_status(
        self, id: str, *, status: str, reason: Optional[str] = None
    ) -> None:
        """Update the status of an entity.

        Parameters:
          id: The entity .id
          status: New .status value
          reason: New .reason value
        """

    @abc.abstractmethod
    def update_labels(self, id: str, labels: Labeled) -> None:
        """Updated the labels of a labeled entity.

        :param id: The ID of the entity to update.
        :type id: str
        :param labels: The labels to update.
        :type labels: Labeled
        """

    @abc.abstractmethod
    def create_audit(self, spec: Audit) -> Audit:
        """Create a new Audit entity in the system.

        Parameters:
          spec: Specification of the Audit. The system fields of the spec
            such as ``.id`` must be **unset**.

        Returns:
          A copy of ``spec`` with all system fields set.
        """

    @abc.abstractmethod
    def create_data_source(self, spec: DataSource) -> DataSource:
        """Create a new DataSource entity in the system.

        Parameters:
          spec: Specification of the DataSource. The system fields of the spec
            such as ``.id`` must be **unset**.

        Returns:
          A copy of ``spec`` with all system fields set.
        """

    @abc.abstractmethod
    def create_dataset(self, spec: Dataset) -> Dataset:
        """Create a new Dataset entity in the system.

        Parameters:
          spec: Specification of the Dataset. The system fields of the spec
            such as ``.id`` must be **unset**.

        Returns:
          A copy of ``spec`` with all system fields set.
        """

    @abc.abstractmethod
    def create_evaluation(self, spec: Evaluation) -> Evaluation:
        """Create a new Evaluation entity in the system.

        Parameters:
          spec: Specification of the Evaluation. The system fields of the spec
            such as ``.id`` must be **unset**.

        Returns:
          A copy of ``spec`` with all system fields set.
        """

    @abc.abstractmethod
    def create_inference_service(self, spec: InferenceService) -> InferenceService:
        """Create a new InferenceService entity in the system.

        Parameters:
          spec: Specification of the InferenceService. The system fields of the spec
            such as ``.id`` must be **unset**.

        Returns:
          A copy of ``spec`` with all system fields set.
        """

    @abc.abstractmethod
    def create_inference_session(self, spec: InferenceSession) -> InferenceSession:
        """Create a new InferenceSession entity in the system.

        Parameters:
          spec: Specification of the InferenceSession. The system fields of the spec
            such as ``.id`` must be **unset**.

        Returns:
          A copy of ``spec`` with all system fields set.
        """

    @abc.abstractmethod
    def create_model(self, spec: Model) -> Model:
        """Create a new Model entity in the system.

        Parameters:
          spec: Specification of the Model. The system fields of the spec
            such as ``.id`` must be **unset**.

        Returns:
          A copy of ``spec`` with all system fields set.
        """

    @abc.abstractmethod
    def create_report(self, spec: Report) -> Report:
        """Create a new Report entity in the system.

        Parameters:
          spec: Specification of the Report. The system fields of the spec
            such as ``.id`` must be **unset**.

        Returns:
          A copy of ``spec`` with all system fields set.
        """

    def terminate_workflow(self, id: str) -> None:
        """Terminate a running workflow.

        :param id: The ID of the workflow.
        :type id: str
        """
        self.update_status(
            id,
            status=EntityStatus.terminated,
            reason=EntityStatusReason.terminate_command,
        )

    def delete_entity(self, id: str) -> None:
        """Delete an existing entity.

        :param id: The ID of the entity.
        :type id: str
        """
        self.update_status(
            id,
            status=EntityStatus.deleted,
            reason=EntityStatusReason.delete_command,
        )
