import json
import httpx

from fastapi import status
from fastapi.responses import JSONResponse
from beanie import Document, Link


async def async_response(data=None, message=None, code=None, page_no=None, total_num=None, page_size=None,
                         status_code=status.HTTP_200_OK):
    def _serialize(data):
        if issubclass(data, Document):
            link_field_list = []
            for field_name in data.__annotations__:
                field_type = getattr(data, field_name)
                if isinstance(field_type, Link):
                    link_field_list.append(field_name)

            data = json.loads(data.model_dump_json(exclude="password"))
            if link_field_list:
                for field_name in link_field_list:
                    if isinstance(data[field_name], dict) and "id" in data[field_name].keys():
                        data[field_name] = data[field_name]["id"]
        return data

    if isinstance(data, httpx.Response):
        return JSONResponse(status_code=data.status_code, content=data.json())

    ret = {}
    if isinstance(data, list):
        data = [_serialize(d) for d in data]
    else:
        data = _serialize(data)

    ret['code'] = code or "ok"

    ret['message'] = message or "success"

    if page_no and total_num and page_size:
        ret['data'] = {
            'page_no': page_no,
            'page_size': page_size,
            'total_num': total_num,
            'page_data': data
        }
    else:
        ret['data'] = data

    return JSONResponse(status_code=status_code, content=ret)
