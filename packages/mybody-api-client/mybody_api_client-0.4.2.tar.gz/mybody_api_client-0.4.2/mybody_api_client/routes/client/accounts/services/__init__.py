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


class ClientAccountServiceRoute(BaseRoute):
    prefix = '/services'

    async def get(self, id_: int):
        return await self.request(
            type_=RequestTypes.GET,
            prefix='/get',
            parameters={
                'id': id_,
            },
            response_key='account_service',
        )

    async def get_list(self):
        return await self.request(
            type_=RequestTypes.GET,
            prefix='/list/get',
            response_key='account_services',
        )

    async def create(self, service: str, answers: str):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/create',
            parameters={
                'service': service,
                'answers': answers,
            },
            response_key='id',
        )

