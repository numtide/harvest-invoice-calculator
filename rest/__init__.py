import json
import urllib.request
from typing import Any, Dict, Optional


def http_request(
    url: str,
    method: str = "GET",
    headers: Dict[str, str] = {},
    data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    body = None
    if data:
        body = json.dumps(data).encode("ascii")
    headers = headers.copy()
    headers["User-Agent"] = "Numtide invoice generator"
    req = urllib.request.Request(url, headers=headers, method=method, data=body)
    resp = urllib.request.urlopen(req)
    return json.load(resp)
