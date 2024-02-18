import strangeworks
from strangeworks.core.client.resource import Resource
import requests


def upload_input_file(filename: str, resource_slug: str):
    data = {
        "object_name": filename,
    }
    
    resource = strangeworks.resources(slug=resource_slug)[0]

    results = strangeworks.execute(
        res=resource,
        payload=data,
        endpoint="upload",
    )

    response = results["results"]

    try:
        with open(filename, "rb") as f:
            files = {"file": (filename, f)}
            http_response = requests.post(response["url"], data=response["fields"], files=files)

            return http_response

    except Exception as error:
        return {"status_code": 400, "content": {"message": "Exception occurred during upload", "error": f"{error}"}}
