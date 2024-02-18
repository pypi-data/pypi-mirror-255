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


class AdminAccountServiceRoute(BaseRoute):
    prefix = '/services'

    async def create(
            self,
            account_id: int,
            service: str,
            answers: str,
    ):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/create',
            parameters={
                'account_id': account_id,
                'service': service,
                'answers': answers,
            },
            response_key='id',
        )

    async def update(
            self,
            id_: int,
            answers: str,
            state: str,
            datetime_from: str,
            datetime_to: str,
    ):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/update',
            parameters={
                'id_': id_,
                'answers': answers,
                'state': state,
                'datetime_from': datetime_from,
                'datetime_to': datetime_to,
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
                'id_': id_,
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
            response_key='account_service',
        )

    async def get_list(
            self,
            account_id: int = None,
    ):
        return await self.request(
            type_=RequestTypes.GET,
            prefix='/list/get',
            parameters={
                'account_id': account_id,
            },
            response_key='account_services',
        )
