# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import abc
from datetime import datetime
from typing import List, Optional

import pydantic

from ....schema.platform import APIKey


class Account(pydantic.BaseModel):
    """An Account in the system. All entities are owned by an Account."""

    name: str
    apiKeys: List[APIKey] = pydantic.Field(default_factory=list)
    # --- Added by system
    id: Optional[str] = None
    creationTime: Optional[datetime] = None


class AuthBackend(abc.ABC):
    @abc.abstractmethod
    def create_account(self, name: str) -> Account:
        """Create a new Account.

        Parameters:
        name: A unique human-readable name

        Returns:
        Entity representing the Account.
        """

    @abc.abstractmethod
    def delete_account(self, account_id: str):
        """Delete an Account.

        Parameters:
        account_id: The unique identifier of the Account.
        """

    @abc.abstractmethod
    def get_account(
        self, *, id: Optional[str] = None, name: Optional[str] = None
    ) -> Optional[Account]:
        """Get Account by ID and/or name.

        Parameters:
        id: The unique identifier of the Account.
        name: The unique name of the Account.
        """

    @abc.abstractmethod
    def add_api_key(self, account_id: str, api_key: APIKey) -> None:
        """Add a new APIKey to an Account.

        Parameters:
        account_id: The unique identifier of the Account.
        api_key: The new API key.
        """

    @abc.abstractmethod
    def revoke_api_key(self, account_id: str, api_key_id: str) -> None:
        """Revoke an APIKey associated with an Account.

        Parameters:
        account_id: The unique identifier of the Account.
        api_key: The unique identifier of the APIKey.
        """

    @abc.abstractmethod
    def revoke_all_api_keys(self, account_id: str) -> List[APIKey]:
        """Revoke all API keys for the given Account.

        Parameters:
        account_id: The unique identifier of the Account.
        """

    @abc.abstractmethod
    def get_api_key(self, account_id: str, api_key_id: str) -> Optional[APIKey]:
        """Get an APIKey associated with an Account by ID.

        Parameters:
        account_id: The unique identifier of the Account.
        api_key_id: The unique identifier of the APIKey.
        """

    @abc.abstractmethod
    def get_all_api_keys(self, account_id: str) -> List[APIKey]:
        """Get the API keys associated with an Account.

        Parameters:
        account_id: The unique identifier of the Account.
        """
