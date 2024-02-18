Storage
=======

The Dyff :doc:`core resource types <core-resources>` correspond to kinds of
records in a database. Each record has a globally unique ``.id`` field and
belongs to a single ``.account``. Associated data that is too large to store in
the database is stored in storage buckets at a path that can be determined from
the corresponding entity.

The Data Store
--------------

We refer to the database of resource instances as the *datastore*. The current
version of the Dyff Platform uses MongoDB as its datastore, but the datastore is
exposed through a DB-agnostic interface, and the intention is for future
versions to support swappable datastore backends.

Entities in the database are identified by globally unique string IDs containing
a UUID4 unique identifier (encoded in hex with the dashes removed).

Accounts
~~~~~~~~

Every resource in the datastore is "owned" by exactly one :class:`Account
<dyff.schema.platform.Account>`. Accounts are granted access to Dyff API
endpoints via :class:`API keys <dyff.schema.platform.APIKey>`. The owner of an
entity is, generally, the account of the API key that was used to create the
entity. Access grants can apply to individual entities or to all entities owned
by a given account. For example, entities owned by the ``public`` account are
accessible to all accounts by default.

Bulk Storage in Buckets
-----------------------

Large data artifacts such as the actual input instances associated with a
dataset are stored in "storage buckets" in canonical paths that are determined
by their keys and certain other properties. The prototype Dyff Platform is
developed on the Google Cloud Platform, and so it uses Google Cloud Storage as
the storage bucket backend. Support for other object storage providers that
conform to the s3 interface is planned.
