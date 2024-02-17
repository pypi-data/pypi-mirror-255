from enum import Enum

import dictdiffer
from typing import Optional

from pydantic import BaseModel


class Operate(BaseModel):
    add: Optional[dict] = None
    remove: Optional[dict] = None
    change: Optional[dict] = None

    @classmethod
    async def generate_operate(cls, original: dict = None, compare: dict = None):
        if original:
            original = await cls.remove_ignore_field(original)
        else:
            original = {}

        if compare:
            compare = await cls.remove_ignore_field(compare)
        else:
            compare = {}

        diff_result = {'add': {}, 'remove': {}, 'change': {}}
        for diff in list(dictdiffer.diff(original, compare)):
            diff = (list(diff))
            if diff[0] == 'add' or diff[0] == 'remove':
                diff[2] = list(diff[2])
                for j in range(0, len(diff[2])):
                    diff[2][j] = list(diff[2][j])
            if diff[1] == 'change':
                diff[2] = list(diff[2])

            if diff[0] == 'change':
                diff_result['change'][diff[1]] = {'orig': diff[2][0], 'new': diff[2][1]}

            if diff[0] == 'add' or diff[0] == 'remove':
                for j in range(0, len(diff[2])):
                    diff_result[diff[0]][diff[2][j][0]] = diff[2][j][1]

        return Operate(**diff_result)

    @classmethod
    async def remove_ignore_field(cls, model_dict: dict):
        return {k: v for k, v in model_dict.items() if k not in ['create_time', 'update_time']}


class OperatorTypeEnum(str, Enum):
    SYSTEM = "SYSTEM"
    USER = "USER"
    CUSTOMER = "CUSTOMER"
