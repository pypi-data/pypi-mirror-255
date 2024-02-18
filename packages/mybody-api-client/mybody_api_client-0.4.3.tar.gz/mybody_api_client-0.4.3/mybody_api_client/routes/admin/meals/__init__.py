#
# (c) 2024, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


from mybody_api_client.utils import BaseRoute, RequestTypes
from .products import AdminMealProductRoute
from .reports import AdminMealReportRoute


class AdminMealRoute(BaseRoute):
    prefix = '/meals'

    products = AdminMealProductRoute()
    reports = AdminMealReportRoute()

    async def create(
            self,
            account_service_id: int,
            date: str,
            type_: str,
            fats: int,
            proteins: int,
            carbohydrates: int,
    ):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/create',
            parameters={
                'account_service_id': account_service_id,
                'date': date,
                'type': type_,
                'fats': fats,
                'proteins': proteins,
                'carbohydrates': carbohydrates,
            },
            response_key='id',
        )

    async def update(
            self,
            id_: int,
            date: str = None,
            type_: str = None,
            fats: int = None,
            proteins: int = None,
            carbohydrates: int = None,
    ):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/update',
            parameters={
                'id': id_,
                'date': date,
                'type': type_,
                'fats': fats,
                'proteins': proteins,
                'carbohydrates': carbohydrates,
            },
        )

    async def delete(
            self,
            id_: int,
    ):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/delete',
            parameters={
                'id': id_,
            },
        )

    async def get(
            self,
            id_: int,
    ):
        return await self.request(
            type_=RequestTypes.GET,
            prefix='/get',
            parameters={
                'id': id_,
            },
            response_key='meal',
        )

    async def get_list(
            self,
            account_service_id: int,
            date: str = None,
    ):
        parameters = {
            'account_service_id': account_service_id,
        }
        if date:
            parameters['date'] = date
        return await self.request(
            type_=RequestTypes.GET,
            prefix='/list/get',
            parameters=parameters,
            response_key='meals',
        )

    async def get_list_all(self):
        return await self.request(
            type_=RequestTypes.GET,
            prefix='/list/get/all',
            response_key='meals',
        )
