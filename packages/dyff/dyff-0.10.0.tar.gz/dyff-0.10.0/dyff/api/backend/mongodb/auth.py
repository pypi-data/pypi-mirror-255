# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import List, Optional

import pymongo
import pymongo.read_concern
import pymongo.read_preferences
import pymongo.write_concern
from pymongo.client_session import ClientSession

from dyff.schema.platform import APIKey

from ....core.config import config
from ....schema import ids
from ... import timestamp
from ...exceptions import EntityExistsError
from ..base.auth import Account, AuthBackend


class MongoDBAuthBackend(AuthBackend):
    def __init__(self):
        connection_string = config.api.auth.mongodb.connection_string
        self._client = pymongo.MongoClient(connection_string.get_secret_value())

        # Interact with the database in a way that gives strong consistency
        # (These are currently the default settings; I prefer to be explicit)
        self._accounts_db = self._client.get_database(
            config.api.auth.mongodb.database,
            read_concern=pymongo.read_concern.ReadConcern("majority"),
            read_preference=pymongo.ReadPreference.PRIMARY,
            write_concern=pymongo.write_concern.WriteConcern("majority", wtimeout=5000),
        )

    def _get_account(
        self,
        *,
        id: str | None = None,
        name: str | None = None,
        session: ClientSession = None,
    ) -> Optional[Account]:
        filter = {}
        if id is not None:
            filter["_id"] = id
        if name is not None:
            filter["name"] = name
        if len(filter) == 0:
            raise ValueError("must specify at least one of {id, name}")
        result = self._accounts_db.accounts.find_one(filter, session=session)
        if result:
            result = dict(result)
            result["id"] = result["_id"]
            del result["_id"]
            return Account.parse_obj(result)
        return None

    def _insert_account(
        self, account: Account, *, session: ClientSession = None
    ) -> None:
        d = account.dict()
        d["_id"] = d["id"]
        del d["id"]
        self._accounts_db.accounts.insert_one(d, session=session)

    def create_account(self, name: str) -> Account:
        """Create a new Account.

        Parameters:
        name: A unique human-readable name

        Returns:
        Entity representing the Account.
        """
        duplicate_name = self._get_account(name=name)
        if duplicate_name is not None:
            raise EntityExistsError("duplicate account name")
        id = ids.generate_entity_id()
        account = Account(id=id, name=name, creationTime=timestamp.now())
        self._insert_account(account)
        return account

    def delete_account(self, account_id: str):
        """Delete an Account.

        Parameters:
        account_id: The unique identifier of the Account.
        """
        raise NotImplementedError()

    def get_account(
        self, *, id: Optional[str] = None, name: Optional[str] = None
    ) -> Optional[Account]:
        """Get Account by ID.

        Parameters:
        account_id: The unique identifier of the Account.
        """
        return self._get_account(id=id, name=name)

    def add_api_key(self, account_id: str, api_key: APIKey) -> None:
        """Add a new APIKey to an Account.

        Raises ``ValueError`` if an APIKey with the same ID already exists.

        Parameters:
        account_id: The unique identifier of the Account.
        api_key: The new API key.
        """
        account = self._get_account(id=account_id)
        if account is None:
            raise ValueError(f"no Account with .id {account_id}")
        if any(account_key.id == api_key.id for account_key in account.apiKeys):
            raise ValueError(f"APIKey with .id {api_key.id} already exists")
        # Don't have to translate APIKey.id because APIKey isn't a
        # top-level entity
        self._accounts_db.accounts.update_one(
            {"_id": account_id}, {"$push": {"apiKeys": api_key.dict()}}
        )

    def revoke_api_key(self, account_id: str, api_key_id: str) -> None:
        """Revoke an APIKey associated with an Account.

        Parameters:
        account_id: The unique identifier of the Account.
        api_key: The unique identifier of the APIKey.
        """
        account = self._get_account(id=account_id)
        if account is None:
            raise ValueError(f"no Account with .id {account_id}")
        filtered = [api_key for api_key in account.apiKeys if api_key.id != api_key_id]
        if len(filtered) == len(account.apiKeys):
            raise ValueError(f"no APIKey with .id {api_key_id} in account")
        # Don't have to translate APIKey.id because APIKey isn't a
        # top-level entity
        self._accounts_db.accounts.update_one(
            {"_id": account_id},
            {"$set": {"apiKeys": [key.dict() for key in filtered]}},
        )

    def revoke_all_api_keys(self, account_id: str) -> None:
        """Revoke all API keys for the given Account.

        Parameters:
        account_id: The unique identifier of the Account.
        """
        result = self._accounts_db["accounts"].update_one(
            {"_id": account_id}, {"$set": {"apiKeys": []}}
        )
        if result.matched_count != 1:
            raise ValueError(f"no Account with .id {account_id}")

    def get_api_key(self, account_id: str, api_key_id: str) -> Optional[APIKey]:
        """Get an APIKey associated with an Account by ID.

        Parameters:
        account_id: The unique identifier of the Account.
        api_key_id: The unique identifier of the APIKey.
        """
        api_keys = self.get_all_api_keys(account_id)
        for api_key in api_keys:
            if api_key.id == api_key_id:
                return api_key
        return None

    def get_all_api_keys(self, account_id: str) -> List[APIKey]:
        """Get the API keys associated with an Account.

        Parameters:
        account_id: The unique identifier of the Account.
        """
        account = self._get_account(id=account_id)
        if account is None:
            raise ValueError(f"no Account with .id {account_id}")
        account = Account.parse_obj(account)
        return account.apiKeys
