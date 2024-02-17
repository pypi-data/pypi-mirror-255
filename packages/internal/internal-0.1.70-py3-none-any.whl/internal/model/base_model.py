from datetime import datetime
from enum import Enum
from typing import List, Tuple

import pymongo
from fastapi import FastAPI
from beanie import Document
from pydantic import Field

from ..const import DEF_PAGE_SIZE, DEF_PAGE_NO


class InternalBaseDocument(Document):
    create_time: datetime = Field(default_factory=datetime.utcnow)
    update_time: datetime = Field(default_factory=datetime.utcnow)

    @classmethod
    async def get_pagination_list(cls, app: FastAPI, query: list = None, sort: List[Tuple] = None,
                                  page_size: int = DEF_PAGE_SIZE, page_no: int = DEF_PAGE_NO, ignore_cache: bool = False,
                                  fetch_links: bool = False):
        if not query:
            final_query = []
        else:
            final_query = query

        if not sort:
            final_sort = [(cls.id, pymongo.ASCENDING)]
        else:
            final_sort = []
            for temp_sort in sort:
                if temp_sort[1] == OrderTypeEnum.ASC:
                    final_sort.append((temp_sort[0], pymongo.ASCENDING))
                elif temp_sort[1] == OrderTypeEnum.DESC:
                    final_sort.append((temp_sort[0], pymongo.DESCENDING))
                else:
                    print(f"order type value error: temp_sort:{temp_sort}")
                    continue

        total_num = await cls.find(*final_query, ignore_cache=ignore_cache, fetch_links=fetch_links).sort(
            *final_sort).count()
        if total_num == 0:
            page_data = []
        else:
            page_data = await cls.find(*final_query, ignore_cache=ignore_cache, fetch_links=fetch_links).sort(
                *final_sort).limit(page_size).skip((page_no - 1) * page_size).to_list()

        return page_no, page_size, total_num, page_data


class OrderTypeEnum(str, Enum):
    ASC = "ASC"
    DESC = "DESC"
