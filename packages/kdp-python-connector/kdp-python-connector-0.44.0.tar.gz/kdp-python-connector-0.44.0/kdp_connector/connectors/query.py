import kdp_api
from kdp_api.api import read_and_query_api
from kdp_api.model.query_document_lucene_response import QueryDocumentLuceneResponse

class QueryApi(object):

    def post_lucene_query(self, config, dataset_id: str, expression: str, limit: int = 5, offset: int = 0):
        """This method will be used to query data in KDP datasets using the lucene syntax

            :param Configuration config: Connection configuration
            :param str dataset_id: ID of the KDP dataset where the data will queried
            :param str expression: Lucene style query expression ex. name: John

            :returns: Records matching query expression

            :rtype: RecordBatch
        """
        with kdp_api.ApiClient(config) as api_client:
            api_instance = read_and_query_api.ReadAndQueryApi(api_client)

            query = {}
            query['datasetId'] = dataset_id
            query['expression'] = expression
            query['limit'] = limit
            query['offset'] = offset

            return api_instance.post_lucene_query(lucene_query_request=query)


    def post_document_lucene_query(self, config, dataset_id: str, expression: str, limit: int = 5, offset: int = 0) -> QueryDocumentLuceneResponse:
        """This method will be used to query document data in KDP datasets using the lucene syntax

            :param Configuration config: Connection configuration
            :param str dataset_id: ID of the KDP dataset where the data will queried
            :param str expression: Lucene style query expression ex. name: John
            :param int limit: max number of results in the response.
            :param int offset: how many records to skip before returning first record.
            :returns: QueryDocumentLuceneResponse object contains records matching query expression

            :rtype: QueryDocumentLuceneResponse
        """
        with kdp_api.ApiClient(config) as api_client:
            api_instance = read_and_query_api.ReadAndQueryApi(api_client)

            query = {}
            query['datasetId'] = dataset_id
            query['expression'] = expression
            query['limit'] = limit
            query['offset'] = offset

            return api_instance.post_lucene_query_document(query_document_lucene_request=query)
