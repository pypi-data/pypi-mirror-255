import backoff
from datetime import datetime, timedelta, timezone

from google.cloud.bigquery import Client as GoogleBigQueryClient
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

from arcane.core.exceptions import GOOGLE_EXCEPTIONS_TO_RETRY


class TableNotUpdatedError(Exception):
    pass

class Client(GoogleBigQueryClient):
    def __init__(self, project=None, credentials=None, _http=None):
        super().__init__(project=project, credentials=credentials, _http=_http)

    def create_bq_dataset(self, dataset_name: str, location: str = 'US'):
        dataset_ref = self.dataset(dataset_name)
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = location
        dataset = self.create_dataset(dataset)

    # full_table_name format: 'project_id.dataset_id.table_name'
    def check_bq_table_exist(self, full_table_name: str) -> bigquery.Table:
        """ This function check if a table exist in a big query dataset.
        Args:
            full_table_name (str): a table name in the format project_id.dataset_id.table_name
        Raises:
            NotFound: The table {full_table_name} was not found
        """
        try:
            return self.get_table(full_table_name)
        except NotFound:
            raise NotFound(f"The table {full_table_name} was not found")

    def check_bq_table_updated(self, full_table_name: str, minutes_since_last_update: int = 30):
        """Check if the given table exist in the dataset and has been updated in the last minutes_since_last_update minutes
        Args:
            full_table_name (str): a table name in the format project_id.dataset_id.table_name
            minutes_since_last_update (int): minute since last update. Default to 30 minutes
        Raises:
            TableNotUpdatedError: Table {full_table_name} has not been updated since {table_update_time}
            NotFound: The table {full_table_name} was not found

        Returns:
            Table: the table object
        """
        table = self.check_bq_table_exist(full_table_name)

        table_update_time = table.modified
        if table_update_time is None:
            raise TableNotUpdatedError(
                f"Table {full_table_name} has never been updated")
        if table_update_time < datetime.now(tz=timezone.utc) - timedelta(minutes=minutes_since_last_update):
            raise TableNotUpdatedError(
                f"Table {full_table_name} has not been updated since {table_update_time}")
        return table

    @backoff.on_exception(backoff.expo, GOOGLE_EXCEPTIONS_TO_RETRY, max_tries=5)
    def load_table_from_uri(self, *args, **kwargs):
        return super().load_table_from_uri(*args, **kwargs)

    @backoff.on_exception(backoff.expo, GOOGLE_EXCEPTIONS_TO_RETRY, max_tries=5)
    def create_table(self, *args, **kwargs):
        return super().create_table(*args, **kwargs)

    @backoff.on_exception(backoff.expo, GOOGLE_EXCEPTIONS_TO_RETRY, max_tries=5)
    def get_table(self, *args, **kwargs):
        return super().get_table(*args, **kwargs)

    @backoff.on_exception(backoff.expo, GOOGLE_EXCEPTIONS_TO_RETRY, max_tries=5)
    def query(self, *args, **kwargs):
        return super().query(*args, **kwargs)



