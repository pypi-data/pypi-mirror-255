import kdp_api
import logging
import gzip
import json
import urllib3
from urllib3.util import Timeout
from pprint import pprint
from kdp_api.api import write_api
from kdp_api.models import WriteBatchResponse
from kdp_api.models import BatchWriteRequest
from kdp_api.models import SecurityLabelInfoParams
from kdp_api.configuration import Configuration
from pandas import DataFrame

class WriteApi(object):
    def __init__(self, configuration: Configuration=None):
        self.configuration = configuration
        host=self.configuration.host.replace('https://', '')

        self.http = urllib3.HTTPSConnectionPool(host, port=443, cert_reqs='CERT_NONE', assert_hostname=False,
        timeout=Timeout(connect=2.0, read=60.0))


    def batch_write(self, config, dataset_id: str, dataframe: DataFrame, batch_size: int, is_async: bool = True):
        """This method will be used to write batches of data to KDP

            :param Configuration config: Connection configuration
            :param str dataset_id: ID of the KDP dataset where the data will be written
            :param DataFrame dataframe: Data to write to KDP
            :param int batch_size: Defaults to 100
            :param bool is_async: Defaults to True

            :returns: Set of partitions data was written to

            :rtype: set
        """
        with kdp_api.ApiClient(config) as api_client:

            # Create an instance of the API class
            api_instance = write_api.WriteApi(api_client)

            partitions_set = set()

            try:
                # Convert dataframe into dict. The result is an array of json.
                json_record_array = dataframe.to_dict(orient='records')

                for i in range(0, len(json_record_array), batch_size):

                    batch = json_record_array[i:i + batch_size]

                    write_batch_response: WriteBatchResponse = api_instance.post_write_id(
                        dataset_id=dataset_id,
                        json_record=batch,
                        is_async=is_async
                    )

                    partitions_set.update(write_batch_response.partitions)

                return partitions_set

            except kdp_api.ApiException as e:
                pprint("Exception : %s\n" % e)

    def batch_write_v2_compressed(self,
            dataset_id: str,
            data: list,
            security_label_info_params: SecurityLabelInfoParams = None,
            is_async: bool = True) -> object:
        """This method will be used to write batches of data to KDP assuming request payload is gzip-compressed.

            :param str dataset_id: ID of the KDP dataset where the data will be written
            :param list data: Data to write to KDP
            :param SecurityLabelInfoParams security_label_info_params: Security Label Parser Parameter configuration
            :param bool is_async: Is the request async. Defaults to True

            :returns: Set of partitions data was written to

            :rtype: set
        """

        request = {
            'records': data
        }


        params = security_label_info_params.to_dict()

        if security_label_info_params is not None:
            # required attributes
            request['securityLabelInfo'] = {
                'parserClassName': security_label_info_params.parser_class_name,
                'fields': security_label_info_params.fields
            }

            if 'label_handling_policy' in params:
                request['securityLabelInfo']['labelHandlingPolicy'] = params['label_handling_policy']

            if 'replacementString' in params:
                request['securityLabelInfo']['replacementString'] = params['replacementString']



        json_bytes = json.dumps(request).encode('utf-8')
        compressed = gzip.compress(json_bytes)

        url = self.configuration.host + "/v2/write/" + dataset_id + '?isAsync=' + str(is_async)

        logging.debug(f'request url = {url}')
        logging.debug('request payload (before compression): %s' % json_bytes)

        result: urllib3.response.HTTPResponse = self.http.request(
            'POST',
            url,
            body=compressed,
            headers={
                'Content-Encoding': 'gzip',
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.configuration.access_token
                }
            )

        if result.status == 200:
            return json.loads(result.data)
        else:
            logging.error('unexpected response code returned. status: %s, reason: %s, message: %s' %
                (result.status, result.reason, result.msg))
            raise Exception('Failed to post to batch-write')


    def batch_write_v2(self, config,
            dataset_id: str,
            dataframe: DataFrame,
            security_label_info_params: SecurityLabelInfoParams = None,
            batch_size: int = 100,
            is_async: bool = True,
            is_compressed: bool = False):
        """This method will be used to write batches of data to KDP

            :param Configuration config: Connection configuration
            :param str dataset_id: ID of the KDP dataset where the data will be written
            :param DataFrame dataframe: Data to write to KDP
            :param SecurityLabelInfoParams security_label_info_params: Security Label Parser Parameter configuration
            :param int batch_size: Defaults to 100
            :param bool is_async: Is the request async. Defaults to True
            :param bool is_compressed:  If true, gzip-compress the request payload. Defaults to False

            :returns: Set of partitions data was written to

            :rtype: set
        """
        with kdp_api.ApiClient(configuration=config) as api_client:

            # Create an instance of the API class
            api_instance = write_api.WriteApi(api_client)

            partitions_set = set()

            try:
                # Convert dataframe into dict. The result is an array of json.
                json_record_array = dataframe.to_dict(orient='records')

                for i in range(0, len(json_record_array), batch_size):

                    batch = json_record_array[i:i + batch_size]

                    # Handle compression case, see https://github.com/OpenAPITools/openapi-generator/issues/4165
                    if is_compressed:
                        write_batch_response: object = self.batch_write_v2_compressed(
                            dataset_id=dataset_id,
                            data=batch,
                            security_label_info_params=security_label_info_params,
                            is_async=is_async)

                        partitions_set.update(write_batch_response['partitions'])
                    else:
                        request:BatchWriteRequest = BatchWriteRequest(records=batch, security_label_info=security_label_info_params)

                        write_batch_response: WriteBatchResponse = api_instance.post_v2_write_id(
                            dataset_id=dataset_id,
                            batch_write_request=request,
                            is_async=is_async
                        )

                        partitions_set.update(write_batch_response.partitions)

                return partitions_set

            except kdp_api.ApiException as e:
                pprint("Exception : %s\n" % e)
