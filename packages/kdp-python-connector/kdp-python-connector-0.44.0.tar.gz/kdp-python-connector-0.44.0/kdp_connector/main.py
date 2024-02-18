from kdp_connector.configuration.configurationUtil import ConfigurationUtil
from kdp_connector.configuration.authenticationUtil import AuthenticationUtil
from kdp_connector.configuration.keycloak_authentication import KeycloakAuthentication
from kdp_connector.connectors.batch_write import WriteApi
from kdp_connector.connectors.ingest_job_api import IngestJobApi
from kdp_connector.connectors.read import ReadApi
from kdp_connector.connectors.kdp_api import KdpApi
from kdp_connector.connectors.query import QueryApi
from kdp_connector.connectors.index_management import IndexManagementApi
from kdp_connector.connectors.upload import UploadApi
from kdp_connector.connectors.Storage import StorageApi
from kdp_connector.connectors.audit_log import AuditLogApi
from kdp_connector.connectors.audit_log_configs import AuditLogConfigsApi
from kdp_api.models import SecurityLabelInfoParams
from kdp_api.model.audit_log_configuration_paginator import AuditLogConfigurationPaginator
from kdp_api.model.audit_log_configuration import AuditLogConfiguration
from kdp_api.model.audit_log_paginator import AuditLogPaginator
from pandas import DataFrame

class KdpConn(object):
    """This class contains convenience methods used for interacting with KDP"""

    def __init__(self, path_to_ca_file: str = '', host: str = 'https://api.app.koverse.com',
                 discard_unknown_keys: bool = True):
        self.path_to_ca_file = path_to_ca_file
        self.host = host
        self.discard_unknown_keys = discard_unknown_keys

    def create_configuration(self, jwt: str):
        """This method will be used to create the connection configuration
            :param str jwt: JWT token

            :returns: KDP connection configuration

            :rtype: Configuration
        """
        config = ConfigurationUtil()
        return config.create_configuration(self.host, jwt, self.path_to_ca_file, self.discard_unknown_keys)

    # Auth
    def create_authentication_token(self, email: str, password: str, workspace_id: str,
                                    strategy: str = 'local') -> object:
        """This method will be used to authenticate to KDP

            :param str email: User email
            :param str password: User password
            :param str workspace_id: User workspace
            :param str strategy: Defaults to "local"

            :returns: Authentication token

            :rtype: AuthenticationDetails
        """
        config = self.create_configuration('')

        auth_util = AuthenticationUtil()
        auth_response = auth_util.create_authentication_token(config, email, password, workspace_id, strategy)
        return auth_response

    # Auth, only applicable if jwt is created for auth-proxy
    def create_proxy_authentication_token(self, first_name: str, workspace_id: str, jwt: str = None,
                                          strategy: str = 'proxy') -> object:
        """This method will be used to authenticate to KDP. Only request from auth-proxy with be accepted.

            :param str first_name: User's first name
            :param str workspace_id: User workspace
            :param str strategy: Defaults to "proxy"

            :returns: Authentication token

            :rtype: AuthenticationDetails
        """
        config = self.create_configuration(jwt=jwt)

        auth_util = AuthenticationUtil()
        auth_response = auth_util.create_proxy_authentication_token(config, first_name, workspace_id, strategy)
        return auth_response

    def create_keycloak_authentication_token(self, realm: str, client_id: str, client_secret: str, username: str, password: str, workspace_id: str, host: str,
                                             verify_ssl: True) -> object:
        """This method will be used to authenticate to Koverse via Keycloak

              :param str realm: Keycloak URL including host, realm, broker, etc.
              :param str client_id: Keycloak Client ID
              :param str client_secret: Keycloak Client Password
              :param str username: Username for keycloak authentication
              :param str password: Password for Keycloak authentication, optional, requires email
              :param str host: The keycloak host
              :param str workspace_id: Koverse Workspace ID
              :param str verify_ssl: Boolean when set true call verifies SSL

              :returns: Koverse Authentication token

              :rtype: AuthenticationDetails
          """

        keycloak_auth = KeycloakAuthentication()

        keycloak_auth.set_configuration(realm=realm, client_id=client_id, client_secret=client_secret, username=username, password=password, host=host, verify_ssl=verify_ssl)
        auth_util = AuthenticationUtil()
        config = self.create_configuration('')

        print('Calling to get koverse token from keycloak login')

        return auth_util.get_koverse_token_from_keycloak_login(config=config, keycloak=keycloak_auth, workspace_id=workspace_id)

    # , kc_username: str, kc_password: str,
    # WRITE
    def batch_write(self, dataframe, dataset_id: str, jwt: str, batch_size: int = 100, is_async: bool = True):
        """This method will be used to write batches of data to KDP

            :param DataFrame dataframe: Data to write to KDP
            :param str dataset_id: ID of the KDP dataset where the data will be written
            :param str jwt: JWT token
            :param int batch_size: Defaults to 100
            :param bool is_async: Defaults to True

            :returns: Set of partitions data was written to

            :rtype: set
        """
        config = self.create_configuration(jwt)
        write_api = WriteApi(configuration=config)
        return write_api.batch_write(config=config, dataset_id=dataset_id, dataframe=dataframe, batch_size=batch_size, is_async=is_async)

    # WRITE
    def batch_write_v2(self, dataframe: DataFrame, dataset_id: str, jwt: str, security_label_info_params: SecurityLabelInfoParams = None,
                       batch_size: int = 100, is_async: bool = True, is_compressed: bool = False):

        """This method will be used to write batches of data to KDP

            :param DataFrame dataframe: Data to write to KDP
            :param str dataset_id: ID of the KDP dataset where the data will be written
            :param str jwt: JWT token
            :param SecurityLabelInfoParams security_label_info_params: Security Label Parser Parameter configuration
            :param int batch_size: Defaults to 100
            :param bool is_async: Is the request async. Defaults to True
            :param bool is_compressed: If true, gzip-compress the request payload. Defaults to False

            :returns: Set of partitions data was written to

            :rtype: set
        """
        config = self.create_configuration(jwt)
        write_api = WriteApi(configuration=config)
        return write_api.batch_write_v2(
            config=config,
            dataset_id=dataset_id,
            dataframe=dataframe,
            security_label_info_params=security_label_info_params,
            batch_size=batch_size,
            is_async=is_async,
            is_compressed=is_compressed)

    def create_url_ingest_job(self, workspace_id: str, dataset_id: str, url_list, jwt: str) -> str:
        """This method will be used to start a job that ingests files to KDP

            :param str workspace_id: ID of KDP workspace data will be written to
            :param str dataset_id: ID of the KDP dataset where the data will be written
            :param list url_list: List of urls for each file to be ingested
            :param str jwt: JWT token

            :returns: Job ID

            :rtype: str
        """
        config = self.create_configuration(jwt)
        ingest_job_api = IngestJobApi(configuration=config)
        return ingest_job_api.create_url_ingest_job(workspace_id=workspace_id, dataset_id=dataset_id, url_list=url_list)

    # Query
    def post_lucene_query(self, dataset_id: str, jwt: str, expression: str = '', limit: int = 5, offset: int = 0):
        """This method will be used to query data in KDP datasets using the lucene syntax

            :param str dataset_id: ID of the KDP dataset where the data will queried
            :param str jwt: JWT token
            :param str expression: Lucene style query expression ex. name: John

            :returns: Records matching query expression

            :rtype: RecordBatch
        """
        query_api = QueryApi()
        config = self.create_configuration(jwt)
        return query_api.post_lucene_query(config, dataset_id=dataset_id, expression=expression, limit=limit,
                                           offset=offset)

    def post_document_lucene_query(self, dataset_id: str, jwt: str, expression: str = '', limit: int = 5, offset: int = 0):
        """This method will be used to query document data in KDP datasets using the lucene syntax

            :param str dataset_id: ID of the KDP dataset where the data will queried
            :param str jwt: JWT token
            :param str expression: Lucene style query expression ex. name: John
            :param int limit: max number of results in the response.
            :param int offset: how many records to skip before returning first record.

            :returns: QueryDocumentLuceneResponse object contains records matching query expression

            :rtype: QueryDocumentLuceneResponse
        """
        query_api = QueryApi()
        config = self.create_configuration(jwt)
        return query_api.post_document_lucene_query(config, dataset_id=dataset_id, expression=expression, limit=limit,
                                                    offset=offset)

    # READ
    def read_dataset_to_dictionary_list(self, dataset_id: str, jwt: str,
                                        starting_record_id: str = '', batch_size: int = 100000):
        """This method will read records from a dataset to a dictionary list

            :param str dataset_id: ID of the KDP dataset where the data will be read from
            :param str jwt: JWT token
            :param str starting_record_id: First record id to read
            :param int batch_size: Defaults to 100000

            :returns: Dictionary list of records

            :rtype: list
        """
        read_api = ReadApi()
        config = self.create_configuration(jwt)
        return read_api.read_dataset_to_dictionary_list(config, dataset_id, starting_record_id,
                                                        batch_size)

    def read_dataset_to_pandas_dataframe(self, dataset_id: str, jwt: str,
                                         starting_record_id: str = '', batch_size: int = 100000):
        """This method will read KDP dataset records into a pandas dataframe

            :param str dataset_id: ID of the KDP dataset where the data will be read from
            :param str jwt: JWT token
            :param str starting_record_id: First record id to read
            :param int batch_size: Defaults to 100000

            :returns: Pandas dataframe with KDP records

            :rtype: DataFrame
        """
        read_api = ReadApi()
        config = self.create_configuration(jwt)
        return read_api.read_dataset_to_pandas_dataframe(config, dataset_id, starting_record_id,
                                                         batch_size)

    def get_splits(self, dataset_id: str, jwt: str):
        """This method will get a list of splits from for the dataset

            :param str dataset_id: ID of the KDP dataset to get splits from
            :param str jwt: JWT token

            :returns: List of split points

            :rtype: SplitPoints
        """
        read_api = ReadApi()
        config = self.create_configuration(jwt)
        return read_api.get_splits(config=config, dataset_id=dataset_id)

    def read_batch(self, dataset_id: str, starting_record_id: str, ending_record_id: str,
                   exclude_starting_record_id: bool, batch_size: int, jwt: str):
        """This method will read a batch of records from a KDP dataset

            :param str dataset_id: ID of the KDP dataset that will be read from
            :param str starting_record_id: First record id to read
            :param str ending_record_id: Last record id to read
            :param bool exclude_starting_record_id: Whether to exclude starting record id
            :param int batch_size: Size of batch to read
            :param str jwt: JWT token

            :returns: List of records

            :rtype: RecordBatch
        """
        read_api = ReadApi()
        config = self.create_configuration(jwt)
        return read_api.read_batch(config=config, dataset_id=dataset_id, starting_record_id=starting_record_id,
                                   ending_record_id=ending_record_id,
                                   exclude_starting_record_id=exclude_starting_record_id,
                                   batch_size=batch_size)

    # dataset
    def create_dataset(self, name: str, workspace_id: str, jwt: str, description: str = '',
                       auto_create_indexes: bool = True, schema: str = '{}', search_any_field: bool = True,
                       record_count: int = 0):
        """This method will create a new KDP dataset

            :param str name: Name of dataset to create
            :param str workspace_id: Workspace that dataset will be created in
            :param str jwt: JWT token
            :param str description: Description of dataset
            :param bool auto_create_indexes: Whether to automatically index new data
            :param str schema: Schema of dataset
            :param bool search_any_field: Whether to search any field
            :param int record_count: Whether to search any field

            :returns: New dataset

            :rtype: Dataset
        """
        kdp_api = KdpApi()
        config = self.create_configuration(jwt)
        return kdp_api.create_dataset(config, name, workspace_id, description, auto_create_indexes, schema,
                                      search_any_field, record_count)

    def get_dataset(self, dataset_id, jwt):
        """This method will get a dataset by id

            :param str dataset_id: ID of dataset
            :param str jwt: JWT token

            :returns: Dataset

            :rtype: Dataset
        """
        kdp_api = KdpApi()
        config = self.create_configuration(jwt)
        return kdp_api.get_dataset(config, dataset_id)

    def patch_dataset(self, dataset_id, payload, jwt):
        """This method will update fields in a dataset

            :param str dataset_id: ID of dataset
            :param PatchDataset payload: Payload with the fields to update
            :param str jwt: JWT token

            :returns: Dataset

            :rtype: Dataset
        """
        kdp_api = KdpApi()
        config = self.create_configuration(jwt)
        return kdp_api.patch_dataset(config, dataset_id, payload)

    def clear_dataset(self, dataset_id, jwt):
        """This method will clear the dataset.

            :param str dataset_id: ID of dataset
            :param str jwt: JWT token

            :returns: clear dataset job

            :rtype: Job
        """
        config = self.create_configuration(jwt)
        write_api = StorageApi()
        return write_api.clear_dataset(config=config, dataset_id=dataset_id)

    # workspace
    def get_workspace(self, workspace_id, jwt):
        """This method will get a workspace by id

            :param str workspace_id: ID of workspace
            :param str jwt: JWT token

            :returns: Workspace

            :rtype: Workspace
        """
        kdp_api = KdpApi()
        config = self.create_configuration(jwt)
        return kdp_api.get_workspace(config, workspace_id)

    def create_workspace(self, name, jwt):
        """This method will create a new KDP workspace

            :param str name: Name of workspace to create
            :param str jwt: JWT token

            :returns: New workspace

            :rtype: Workspace
        """
        kdp_api = KdpApi()
        config = self.create_configuration(jwt)
        return kdp_api.create_workspace(config, name)

    def delete_workspace(self, workspace_id, jwt):
        """This method will delete a workspace by id

            :param str workspace_id: ID of workspace
            :param str jwt: JWT token

            :returns: Deleted workspace

            :rtype: Workspace
        """
        kdp_api = KdpApi()
        config = self.create_configuration(jwt)
        return kdp_api.delete_workspace(config, workspace_id)

    # indexes
    def get_indexes(self, dataset_id: str, jwt: str, limit: int = 10):
        """This method will get indexes for a dataset

            :param str dataset_id: ID of dataset
            :param str jwt: JWT token
            :param int limit: Limit number of results returned (default 10)

            :returns: Paginator with indexes

            :rtype: IndexPaginator
        """
        kdp_api = KdpApi()
        config = self.create_configuration(jwt)
        return kdp_api.get_indexes(config, dataset_id, limit)

    # modify index
    def modify_indexes(self, dataset_id: str, create: list, remove: list,
                       autoCreateIndexes: bool, searchAnyField: bool, jwt: str) -> object:
        """This method will modify existing indexes on a dataset

            :param str dataset_id: ID of dataset
            :param list create: List of indexes to create
            :param list remove: List of indexes to delete
            :param bool autoCreateIndexes: Whether to automatically create indexes when data is written
            :param bool searchAnyField: Whether to automatically search any field
            :param str jwt: JWT token

            :returns: Job ID

            :rtype: str
       """
        config = self.create_configuration(jwt)
        index_management_api = IndexManagementApi(configuration=config)
        return index_management_api.modify_indexes(dataset_id=dataset_id, create=create, remove=remove,
                                                   autoCreateIndexes=autoCreateIndexes, searchAnyField=searchAnyField)

    # Jobs
    def get_jobs(self, dataset_id: str, jwt: str, **kwargs):
        """This method will get a list of all jobs for a dataset

            :param str dataset_id: ID of dataset
            :param str jwt: JWT token
            :param kwargs:
                See below
            :Keyword Args:
                workspace_id (str): workspaceId. [optional]
                limit (int): Number of results to return. [optional]
                skip (int): Number of results to skip. [optional]
                sort ({str: (bool, date, datetime, dict, float, int, list, str, none_type)}): Property to sort results. [optional]
                filter ({str: (bool, date, datetime, dict, float, int, list, str, none_type)}): Query parameters to filter. [optional]
                _return_http_data_only (bool): response data without head status
                    code and headers. Default is True.
                _preload_content (bool): if False, the urllib3.HTTPResponse object
                    will be returned without reading/decoding response data.
                    Default is True.
                _request_timeout (int/float/tuple): timeout setting for this request. If
                    one number provided, it will be total request timeout. It can also
                    be a pair (tuple) of (connection, read) timeouts.
                    Default is None.
                _check_input_type (bool): specifies if type checking
                    should be done one the data sent to the server.
                    Default is True.
                _check_return_type (bool): specifies if type checking
                    should be done one the data received from the server.
                    Default is True.
                _spec_property_naming (bool): True if the variable names in the input data
                    are serialized names, as specified in the OpenAPI document.
                    False if the variable names in the input data
                    are pythonic names, e.g. snake case (default)
                _content_type (str/None): force body content-type.
                    Default is None and content-type will be predicted by allowed
                    content-types and body.
                _host_index (int/None): specifies the index of the server
                    that we want to use.
                    Default is read from the configuration.

            :returns: A paginator with a list of jobs

            :rtype: JobPaginator
        """
        kdp_api = KdpApi()
        config = self.create_configuration(jwt)
        return kdp_api.get_jobs(config, dataset_id, **kwargs)

    # Upload
    def upload(self, dataset_id: str, file_config: object, jwt: str):
        """This method will upload a file to KDP

            :param str dataset_id: ID of dataset that file will be uploaded to
            :param object file_config: JSON containing filename and path ex. { "filename": "test.csv", "path": "/path/to/file" }
            :param str jwt: JWT token

        """
        config = self.create_configuration(jwt)
        upload_api = UploadApi(configuration=config)
        return upload_api.upload(dataset_id=dataset_id, file_config=file_config)

    # User
    def delete_user(self, user_id: str, jwt: str):
        """This method will delete a user by id

            :param str user_id: ID of user
            :param str jwt: JWT token

            :returns: Deleted user

            :rtype: User
        """
        kdp_api = KdpApi()
        config = self.create_configuration(jwt)
        return kdp_api.delete_user(config, user_id)

    # audit log configs
    def get_audit_log_configs(self, jwt: str, keep_forever: bool = None, workspace_id: str = None,
                              limit: int = 10, skip: int = 0, sort: object = None, filter: object = None) -> AuditLogConfigurationPaginator:
        """This method returns a AuditLogConfigurationPaginator object which contains list of AuditLogConfiguration objects.

            :param Configuration config: Connection configuration
            :param bool keep_forever: filter on keepForever flag.
            :param jwt: Auth: Json Web Token
            :param str workspace_id: filter on workspace ID.
            :param int limit: max number of results in the response.
            :param int skip: how many records to skip before returning first record.
            :param object sort: sorting configuration
            :param object filter: additional filtering configuration
            :returns: AuditLogConfigurationPaginator object

            :rtype: AuditLogConfigurationPaginator
        """
        config = self.create_configuration(jwt)
        audit_log_configs_api = AuditLogConfigsApi(configuration=config)
        return audit_log_configs_api.get_audit_log_configs(config=config, keep_forever=keep_forever, workspace_id=workspace_id,
                                                           limit=limit, skip=skip, sort=sort, filter=filter)

    def patch_audit_log_configs(self, jwt: str, id: str, keep_forever: bool, age_in_days: int) -> AuditLogConfiguration:
        """This method updates AuditLogConfiguration object.

            :param Configuration config: Connection configuration
            :param jwt: Authentication: Json Web Token
            :param str id: audit log config id
            :param bool keep_forever: keepForever flag.
            :param int age_in_days: number of days to keep the records if keep_forever flag is false.
            :returns: AuditLogConfiguration object after the update.

            :rtype: AuditLogConfiguration
        """
        config = self.create_configuration(jwt)
        audit_log_configs_api = AuditLogConfigsApi(configuration=config)
        return audit_log_configs_api.patch_audit_log_configs(config=config, id=id, keep_forever=keep_forever, age_in_days=age_in_days);

    # audit log
    def post_audit_log_query(self, jwt: str, dataset_id: str, expression: str, limit: int = 5, offset: int = 0) -> AuditLogPaginator:
        """This method will be used to query data in KDP datasets using the lucene syntax

            :param jwt: Authentication: Json Web Token
            :param str dataset_id: audit log dataset id
            :param str expression: Lucene style query expression ex. name: John
            :param int limit: max number of results in the response.
            :param int offset: how many records to skip before returning first record.
            :returns: AuditLogPaginator object which contains audit log records matching query expression

            :rtype: AuditLogPaginator
        """
        config = self.create_configuration(jwt)
        audit_log_api = AuditLogApi(configuration=config)
        return audit_log_api.post_audit_log_query(config=config, dataset_id=dataset_id, expression=expression, limit=limit, offset=offset)
