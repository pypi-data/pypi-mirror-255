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


class AdminTrainingReportRoute(BaseRoute):
    prefix = '/reports'

    async def create(self, training_id: int, comment: str):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/create',
            parameters={
                'training_id': training_id,
                'comment': comment,
            },
            response_key='id',
        )

    async def delete(self, id_: int):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/delete',
            parameters={
                'id': id_,
            },
        )

    async def get(self, id_: int):
        return await self.request(
            type_=RequestTypes.GET,
            prefix='/get',
            parameters={
                'id': id_,
            },
            response_key='training_report',
        )

    async def get_list(self):
        return await self.request(
            type_=RequestTypes.GET,
            prefix='/list/get',
            response_key='training_reports',
        )
