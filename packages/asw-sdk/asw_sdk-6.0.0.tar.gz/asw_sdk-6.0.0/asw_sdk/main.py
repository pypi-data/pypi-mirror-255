import base64
import importlib
import json
import ssl
import traceback
from enum import Enum
from http.cookies import SimpleCookie
from urllib import parse, request
import threading
import logging
from pyspark.sql import SparkSession

log = logging.getLogger()


class WebClient:

    def __init__(self, ts_cli_token):
        self._host_name = None
        self._refresh_token = None
        self._session_code = None
        self._auth_token = ""
        self._ts_cli_token = ts_cli_token

    def get_refresh_token(self):
        token_obj = json.loads(base64.b64decode(self._ts_cli_token).decode("utf-8"))
        self._host_name = token_obj["hostName"]
        self._refresh_token = token_obj["refreshToken"]

    def refresh_token(self):
        self.get_refresh_token()
        url = self._host_name + "/orgs/auth/refresh"
        headers = {'refresh': self._refresh_token}
        req = request.Request(url, headers=headers)
        response = request.urlopen(req, context=disable_ssl_verification_and_get_context())
        authorization_token = response.getheader('Set-Cookie')
        if authorization_token:
            authorization_token = SimpleCookie(authorization_token)['auth'].value
        self._auth_token = authorization_token

    def get_entity(self, endpoint, params=None, headers=None, set_headers=True):
        if set_headers:
            self.refresh_token()
            headers['Cookie'] = 'auth="' + self._auth_token + '"'
            url = self._host_name + endpoint
        else:
            url = endpoint

        if params:
            url += '?' + parse.urlencode(params)

        print(url)
        try:
            req = request.Request(url, headers=headers)
            response = request.urlopen(req, context=disable_ssl_verification_and_get_context())
            if response.status == 200:
                return json.loads(response.read().decode("utf-8"))
            else:
                raise Exception(f"HTTP Error: {response.status}")
        except Exception as e:
            raise Exception(f"An HTTP error occurred: {e}")

    def post_entity(self, endpoint, params=None, json_data=None, headers=None):
        self.refresh_token()
        headers['Cookie'] = 'auth="' + self._auth_token + '"'
        headers['Content-Type'] = 'application/json'
        url = self._host_name + endpoint

        if params:
            url += '?' + parse.urlencode(params)

        print(url)
        try:
            data = json.dumps(json_data).encode("utf-8")
            req = request.Request(url, data=data, headers=headers, method="POST")
            response = request.urlopen(req, context=disable_ssl_verification_and_get_context())
            if response.status == 200:
                return json.loads(response.read().decode("utf-8"))
            else:
                raise Exception(f"HTTP Error: {response.status}")
        except Exception as e:
            raise Exception(f"An HTTP error occurred: {e}")


class Status(Enum):
    EXECUTION_ERROR = 1800
    EXECUTION_INFO = 1900
    EXECUTION_COMPLETED = 2000


class ExecutionMode(Enum):
    LOCAL = 100
    PROXY = 200


def disable_ssl_verification_and_get_context():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.verify_mode = ssl.CERT_NONE
    return context


def log_status(message, status, mode=ExecutionMode.PROXY):
    if status == Status.EXECUTION_INFO.value:
        message = message or 'Execution Info'

    if status == Status.EXECUTION_ERROR.value:
        message = message or 'Execution failed'

    if status == Status.EXECUTION_COMPLETED.value:
        message = message or 'Execution completed'

    if mode == ExecutionMode.LOCAL:
        print(f'Execution mode selected is LOCAL. Not posting data to filter-progress-logs, printing it instead.')
        print(f'{message}')
        return

    ts_cli_token = 'eyJob3N0TmFtZSI6Imh0dHBzOi8vc2Fua2V0MTk5NC5hbHBoYS5sb2NhbDo5OTk4IiwicmVmcmVzaFRva2VuIjoiZXlKamRIa2lPaUpLVjFRaUxDSmxibU1pT2lKQk1qVTJSME5OSWl3aVlXeG5Jam9pVWxOQkxVOUJSVkFpZlEuZE1VSFg5Z29TM3VGWkUxc3RLemI4Wl94TUNzQVVkdk14dU1wM1lTcm5Ed3psdUpxRGFvNEltWkhvTXFROXk2bnZ2N2VuWTVQdHJGNmg3amNkVFVDUUdlSEp5UkdQTHhaZ0ZGSDlhRmhkeUdEWHlRcHlsQVA0WV9TMlpNZmxYY3gwQXdHZ0xRclNnMzZvU1VTamkxVXZucEI1SUF5UkJtNnp3TUZJX2dYYkFxZDQyc0NOejg3ckhnWXZDSlVCMlBhZTJPOENxLVNoMkYwNmNCamRHR3BUSnh6YjdwQ01NTWpHNmVHQ3FrV2ZILXZHSWpyVGN5QWUxZEN2V2FSWk1IRHZINFJhX3RxZWgtdnprWE9EaHBaOWw5bFdqd3VMQXpWZEE2ZlRxZFV0Y29WWXU2cC1CajhHOG1NUmx4WFNMY0tydHN0OXQ3QzBRM0dmZUVVYWVtS1FBLmc0ZXlmdURGOGtVODdLZ1cuMUNwcExfNnZ5YUlORXFLaDAyc0tnYng1RUxRNWN2NzA4WG5TUDR2bzFzXzg0X0ZjLUw5bllsZlRUeU9BSFBoOWRqTW5uUC05ek9manNSRFZCQkxKWnR3STVnTTZYRU5rdTlsZ2JUYXdGQkxKYWZyaHM1Q2dqMm9XMXQydlVzOXBIZVhFQm9EakR1aWhQNFN6UEdTeUxHUnMxRDhwdkJvWVBvcDdKRmtfa3BQNlhYeHhleHl3dExKQ1NvTFV5a0lzZ0xDaTJmZmFRQnBqUGp0Yl9pejFMU3phZDNyZkJseWtLaHE3WHRSbll4YkJMbTlSb2NTd0doMktfVVk0VEJseUlTUjJQaG9YNlNhTU4xMzJ1RC1aWlVYbU1oS290YWg4dFlnazZvTmw5UEtiNV84UERNSzRhNE93LW1kQjRQR0dPS01taEF4ZTRsNFNEV1lBTWtacUtZVTNiUlljU29fbVJTcDBHTm9UWnRLTjAwM3lfTVY3dEpmS3lOWjBXeGxMTXJJZ2VrTElTMEpjdklsOVp0RlVYOUJSeVJrRW9KdTBhS1dWSzZRUG1OUkxxaXhjcW03Q1NHWmhNZFg0MjhyUGloNnI5TEFsSV82NmRXM3JNdkpDOURYNzVLVXJDbG9Dc3pnSnQzVVg1NjZqcHhkT1ZPRGktSVZJUExNbkFCUW5KYWZHTGlOSjR5TVJDanFWWXNtWFRaRFllY2x2Y0dQa2tFZkRzaTVzdW9jRWR1djdaYmlwZ1BPSjM5QnFiU3BMUy11QzdzSTg3MHhfcjU4akNBWWJsLUp5c1VGWjRQdl9McFJ6YVc0U0J6UlgwaUd5Uzk1NVdNd2hSNzB1YnJPQTRCcFI2OHh1TklYdWprUTdBa09CRlBfR01fWFl3bmxCNTktNE5wSzU1alBVbjU1bUI3UEV2MmVsczJzMlM3T3k2YVNqWVlycEc1WmRtR2tnOUw4dWxmajBJUm5hX0VJUU0tZ2dnMFBQVzNUWWlSb1JnaHNzc3E4S3pHbHpDZGUwN0swa2hmdktoYXprZjRLQWZHVEZHNGZJQmpfVGdQdFQyVS1XcWdpWkhRRXlYaGNkaUhZdWVDM2k4SWlabDZFZkI0R09XQkpBMTNsX3FUMzE0LUV2ekNxRkFvZUdVYzZFRFZJckxKMHRoUjZ0X0VSXzM3OG5YRDZvTVRnWFpUM1I5Y2NqS1l0VjlVeVJzX1dtRllxc1pra0I4TVByVHVwNDFCNkVxMS1lbjJWNU5zaXZOS01zRnNmMEVqa0F2M1B4TDBSUUZsN1lSTmdiSEVZS1FGcFBFcUNYTndtS3BNSHlqekhuLTVsRkhob3czbmRjMXVEMlo3Vk9ybE5heVdBTDdrZnRReEZUM1dYUmtQWXItOEJ5TXFQa01qUjdJdm0wd0I4TnBZY3NxWmRvYnpnV0FxX3kzQ1pIWmJEU2VfbzkxdWVwZDUzdVhYNlRFOXM1Y2d3RllTNFpMMTJneEFXN0VEbWs5bFViRzBCekRONEdLS0lCZG5RanlEOWZVcFpfWEZaRWxJbHpiMElTdFFvS25uSGpUM0xtRUFCR0JNZGR4NGFLMU1uU3ZOOGFieFJuU2NHWDloWUUxbGw2VTlDZUl6RFk4MXNBZjlzcV9LRWV2N3RSQkQ0TkZfeTBiNklKQ0hQeEVILVhWb2xvNDlzT3Zoa1NEcEFCLXpzVjVsRVozTEpnLWRwek8tTHpGeGV6OU5rUDFoc2I4bTk5VWpYZXgxRldiSUJVMTNlRUdkYmdQS1VRQlZCNklVdmFWZDM5LkVGMV9ncWoxeTBFd0d5aHF3SWo4cHciLCJ3c0hvc3ROYW1lIjoid3NzOi8vc2Fua2V0MTk5NC53cy5hbHBoYS5sb2NhbDo5OTk4L3dzIn0='
    app_code = 'exec'
    session_code = 'zpss_1_1_55'
    path = 'job-stream/external-filter-progress'
    body_as_string = '''{"displayMessage":null,"filterId":18,"filterName":"SageMakerMapping","filterProgressStatusValue":-12345,"id":null,"jobId":null,"logDate":"2024-01-03T20:43:04.491179-05:00","messageError":"#message#","operationsKey":"630874185"}'''
    message = message.replace('"', "'")
    body_as_string = body_as_string.replace('#message#', message)
    body_as_string = body_as_string.replace('-12345', str(status))
    print('printing body as string')
    print(body_as_string)
    body_as_json = json.loads(body_as_string)
    endpoint = f'/{app_code}/{session_code}/{path}'
    web_client = WebClient(ts_cli_token)
    web_client.post_entity(endpoint=endpoint, json_data=body_as_json, headers={})

    if status == Status.EXECUTION_ERROR.value:
        raise Exception(message)


execution_status = {"alive": True}


def ping_status():
    while execution_status["alive"]:
        log_status(message="Heartbeat sent from entry_point.py", status=Status.EXECUTION_INFO.value)
        threading.Event().wait(5)


def execute_user_code(**user_kwargs):
    module_name = 'alpha_train'
    method_name = 'train_model'
    try:
        module = importlib.import_module(module_name)
        try:
            method = getattr(module, method_name)
            method(**user_kwargs)
        except Exception as e:
            log_status(message=f"Error: {e}", status=Status.EXECUTION_ERROR.value)
    except Exception as e:
        log_status(message=f"Error: {e}", status=Status.EXECUTION_ERROR.value)


def send_heartbeat():
    heartbeat_thread = threading.Thread(target=ping_status)
    heartbeat_thread.start()


if __name__ == "__main__":
    execution_mode = ExecutionMode.PROXY
    try:
        user_kwargs_str = '{"param1":"value1"}'
        user_kwargs = json.loads(user_kwargs_str)
        send_heartbeat()
        spark = (SparkSession
                 .builder
                 .config(map={"spark.driverEnv.PYTHON_CONFIG": "{    \"TOKEN\" : \"eyJraWQiOiJjek9XdmJhak00MklYekxXWDdrVjQzZEpaVVNMVzhoemtBWks5VHhuWUhRPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiJmNDNjMDJhZS0wOTMxLTRkYTctYmU3MC1hM2ZjZWNmODBhOGMiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV96TTlMYnBZQkQiLCJ2ZXJzaW9uIjoyLCJjbGllbnRfaWQiOiI1bGR2NDFoa282cDZna3ZicW5jZWJqMGZiZiIsIm9yaWdpbl9qdGkiOiI2YjczZmI1OC0yZjZjLTRjMmEtYWY0Yi1hYWJhZTY3OWJkNTgiLCJldmVudF9pZCI6IjYzNTJhMzM4LWVkODYtNDQzYi1iMGZmLTA2YjgxODZlNmFiYSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4gcGhvbmUgb3BlbmlkIGVtYWlsIiwiYXV0aF90aW1lIjoxNzA0MjY0MDU0LCJleHAiOjE3MDQzMzYxNTIsImlhdCI6MTcwNDMzMjU1MiwianRpIjoiZjRiNjJiZWMtNjk1NS00M2FlLTk1MjYtOGQ3ZGQ3ODAzNDRjIiwidXNlcm5hbWUiOiJzYW5rZXQifQ.IoU5Tx53WcDgMVa1dLKH7S-zcxz0F7sYV2cX_pBB7VWP1WD01SV4PTmrc1zNvmJjM4qEhIyqwz5mzzYOTzvqjtEkol7XP1ELZJwwpCFFbik1ORqqltkb2drd9DCBjWpt4osP7ynHynL9WFi-sHVhCMEci7uYzYc9OKhV9VC5x6zlZQVu20mErSMu8w0tLe-yzEt6U0R3OQ0Xqjri13xx4_nOWT1BFnzrsp8-NOB84rJzMt2Z_d4waUHncrOw-j_70gzWoyp-TUuX2FSrzhHupfGwjOnWUC9OcqN8gZPSnxkEoyelmYV5aWxEX2mkkzQFwzVYgC-iX6yPPlYWZRwSzw\",    \"nodes\" : {        \"2d2b3eb165df988e214c19854431d873\" : {            \"applicationDataTypeId\" : 120,            \"applicationGroupId\" : 2,            \"biTemporalProps\" : \"IntcbiAgICBcInN0YW5kYXJkXCIgOiB7XG4gICAgICAgIFwiMVwiIDoge1xuICAgICAgICAgICAgXCJkZWZhdWx0XCIgOiB7XG4gICAgICAgICAgICAgICAgXCJhc19vZl90c1wiIDogXCIyMDIzLTA2LTA1XCIsXG4gICAgICAgICAgICAgICAgXCJ2YWxpZF90c1wiIDogXCIyMDIzLTA2LTA1XCJcbiAgICAgICAgICAgIH1cbiAgICAgICAgfSxcbiAgICAgICAgXCIyXCIgOiB7XG4gICAgICAgICAgICBcImRlZmF1bHRcIiA6IHtcbiAgICAgICAgICAgICAgICBcImFzX29mX3RzXCIgOiBcIjIwMjQtMDEtMDJcIixcbiAgICAgICAgICAgICAgICBcInZhbGlkX3RzXCIgOiBcIjIwMjQtMDEtMTBcIlxuICAgICAgICAgICAgfVxuICAgICAgICB9XG4gICAgfVxufVxuIg==\",            \"cittaAgent\" : {                \"launcher\" : {                    \"pipelineConf\" : {                        \"filterName\" : \"SageMakerMapping\",                        \"mlCode\" : \"mlCode1\"                    }                }            },            \"currentlyExecutingJobId\" : null,            \"effectiveTimeLabel\" : \"standard\",            \"invokingAppInstanceId\" : 2,            \"sessionCode\" : \"zpss_1_1_55\"        }    }}", "spark.executorEnv.PYTHON_CONFIG": "{    \"TOKEN\" : \"eyJraWQiOiJjek9XdmJhak00MklYekxXWDdrVjQzZEpaVVNMVzhoemtBWks5VHhuWUhRPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiJmNDNjMDJhZS0wOTMxLTRkYTctYmU3MC1hM2ZjZWNmODBhOGMiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV96TTlMYnBZQkQiLCJ2ZXJzaW9uIjoyLCJjbGllbnRfaWQiOiI1bGR2NDFoa282cDZna3ZicW5jZWJqMGZiZiIsIm9yaWdpbl9qdGkiOiI2YjczZmI1OC0yZjZjLTRjMmEtYWY0Yi1hYWJhZTY3OWJkNTgiLCJldmVudF9pZCI6IjYzNTJhMzM4LWVkODYtNDQzYi1iMGZmLTA2YjgxODZlNmFiYSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4gcGhvbmUgb3BlbmlkIGVtYWlsIiwiYXV0aF90aW1lIjoxNzA0MjY0MDU0LCJleHAiOjE3MDQzMzYxNTIsImlhdCI6MTcwNDMzMjU1MiwianRpIjoiZjRiNjJiZWMtNjk1NS00M2FlLTk1MjYtOGQ3ZGQ3ODAzNDRjIiwidXNlcm5hbWUiOiJzYW5rZXQifQ.IoU5Tx53WcDgMVa1dLKH7S-zcxz0F7sYV2cX_pBB7VWP1WD01SV4PTmrc1zNvmJjM4qEhIyqwz5mzzYOTzvqjtEkol7XP1ELZJwwpCFFbik1ORqqltkb2drd9DCBjWpt4osP7ynHynL9WFi-sHVhCMEci7uYzYc9OKhV9VC5x6zlZQVu20mErSMu8w0tLe-yzEt6U0R3OQ0Xqjri13xx4_nOWT1BFnzrsp8-NOB84rJzMt2Z_d4waUHncrOw-j_70gzWoyp-TUuX2FSrzhHupfGwjOnWUC9OcqN8gZPSnxkEoyelmYV5aWxEX2mkkzQFwzVYgC-iX6yPPlYWZRwSzw\",    \"nodes\" : {        \"2d2b3eb165df988e214c19854431d873\" : {            \"applicationDataTypeId\" : 120,            \"applicationGroupId\" : 2,            \"biTemporalProps\" : \"IntcbiAgICBcInN0YW5kYXJkXCIgOiB7XG4gICAgICAgIFwiMVwiIDoge1xuICAgICAgICAgICAgXCJkZWZhdWx0XCIgOiB7XG4gICAgICAgICAgICAgICAgXCJhc19vZl90c1wiIDogXCIyMDIzLTA2LTA1XCIsXG4gICAgICAgICAgICAgICAgXCJ2YWxpZF90c1wiIDogXCIyMDIzLTA2LTA1XCJcbiAgICAgICAgICAgIH1cbiAgICAgICAgfSxcbiAgICAgICAgXCIyXCIgOiB7XG4gICAgICAgICAgICBcImRlZmF1bHRcIiA6IHtcbiAgICAgICAgICAgICAgICBcImFzX29mX3RzXCIgOiBcIjIwMjQtMDEtMDJcIixcbiAgICAgICAgICAgICAgICBcInZhbGlkX3RzXCIgOiBcIjIwMjQtMDEtMTBcIlxuICAgICAgICAgICAgfVxuICAgICAgICB9XG4gICAgfVxufVxuIg==\",            \"cittaAgent\" : {                \"launcher\" : {                    \"pipelineConf\" : {                        \"filterName\" : \"SageMakerMapping\",                        \"mlCode\" : \"mlCode1\"                    }                }            },            \"currentlyExecutingJobId\" : null,            \"effectiveTimeLabel\" : \"standard\",            \"invokingAppInstanceId\" : 2,            \"sessionCode\" : \"zpss_1_1_55\"        }    }}"})
                 .getOrCreate())
        execute_user_code(**user_kwargs)
        log_status(message="Execution Successful", status=Status.EXECUTION_INFO.value, mode=execution_mode)
    except Exception as e:
        print(f'Exception object is: {e}')
        print(e.__traceback__)
        traceback_str = "Execution failed with error: " + ''.join(traceback.format_tb(e.__traceback__))
        print(traceback_str)
        log_status(message=traceback_str, status=Status.EXECUTION_ERROR.value, mode=execution_mode)
    finally:
        execution_status["alive"] = False
        log_status(message="Execution completed", status=Status.EXECUTION_COMPLETED.value, mode=execution_mode)
