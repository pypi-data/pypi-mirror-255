from rest import net
from rest import helpers as rh
import requests
REQ_TIMEOUT = 15.0


def REQUEST(task):
    method = task.fname.upper()
    url = task.data.url
    params = None
    if "?" in url:
        url, params = net.parse_params(url)
    try:
        resp = net.REQUEST(method, url, params=params,
                           data=task.data.data, raw_response=True,
                           verify=False, timeout=REQ_TIMEOUT)
        task.log(resp.text)
        return resp.status_code == 200
    except requests.Timeout:
        task.log("request timed out", kind="error")
    except Exception as err:
        task.log_exception(err)
    return False
