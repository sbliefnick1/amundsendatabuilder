from typing import Union, Dict, Any, Iterator  # noqa: F401

from databuilder.models.neo4j_csv_serde import (
    Neo4jCsvSerializable, RELATION_START_KEY, RELATION_END_KEY,
    RELATION_START_LABEL, RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE
)
from databuilder.models.table_metadata import TableMetadata
from databuilder.models.user import User
from databuilder.publisher.neo4j_csv_publisher import UNQUOTED_SUFFIX


class TestColumnUsageModel(Neo4jCsvSerializable):

    """
    A model represents user <--> column graph model
    Currently it only support to serialize to table level
    """
    TABLE_NODE_LABEL = TableMetadata.TABLE_NODE_LABEL
    TABLE_NODE_KEY_FORMAT = TableMetadata.TABLE_KEY_FORMAT

    USER_TABLE_RELATION_TYPE = 'READ'
    TABLE_USER_RELATION_TYPE = 'READ_BY'

    # Property key for relationship read, readby relationship
    READ_RELATION_COUNT = 'read_count{}'.format(UNQUOTED_SUFFIX)

    def __init__(self,
                 database,     # type: str
                 cluster,      # type: str
                 schema_name,  # type: str
                 table_name,   # type: str
                 column_name,  # type: str
                 user_email,   # type: str
                 read_count,   # type: int
                 ):
        # type: (...) -> None
        self.database = database
        self.cluster = cluster
        self.schema_name = schema_name
        self.table_name = table_name
        self.column_name = column_name
        self.user_email = user_email
        self.read_count = read_count

        self._node_iter = iter(self.create_nodes())
        self._relation_iter = iter(self.create_relation())

    def create_next_node(self):
        # type: () -> Union[Dict[str, Any], None]

        try:
            return next(self._node_iter)
        except StopIteration:
            return None

    def create_nodes(self):
        # type: () -> List[Dict[str, Any]]
        """
        Create a list of Neo4j node records
        :return:
        """

        return User(email=self.user_email).create_nodes()

    def create_next_relation(self):
        # type: () -> Union[Dict[str, Any], None]

        try:
            return next(self._relation_iter)
        except StopIteration:
            return None

    def create_relation(self):
        # type: () -> Iterator[Any]
        return [{
            RELATION_START_LABEL: TableMetadata.TABLE_NODE_LABEL,
            RELATION_END_LABEL: User.USER_NODE_LABEL,
            RELATION_START_KEY: self._get_table_key(),
            RELATION_END_KEY: self._get_user_key(self.user_email),
            RELATION_TYPE: TestColumnUsageModel.TABLE_USER_RELATION_TYPE,
            RELATION_REVERSE_TYPE: TestColumnUsageModel.USER_TABLE_RELATION_TYPE,
            TestColumnUsageModel.READ_RELATION_COUNT: self.read_count
        }]

    def _get_table_key(self):
        # type: (ColumnReader) -> str
        return TableMetadata.TABLE_KEY_FORMAT.format(db=self.database,
                                                     cluster=self.cluster,
                                                     schema=self.schema_name,
                                                     tbl=self.table_name)

    def _get_user_key(self, email):
        # type: (str) -> str
        return User.get_user_model_key(email=email)

    def __repr__(self):
        # type: () -> str
        return 'TableColumnUsage(col_readers={!r})'.format(self.col_readers)
