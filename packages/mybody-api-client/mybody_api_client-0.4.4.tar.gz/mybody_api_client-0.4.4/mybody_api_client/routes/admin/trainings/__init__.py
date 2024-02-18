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


from mybody_api_client.routes.admin.trainings.exercises import AdminTrainingExerciseRoute
from mybody_api_client.routes.admin.trainings.reports import AdminTrainingReportRoute
from mybody_api_client.utils import BaseRoute, RequestTypes


class AdminTrainingRoute(BaseRoute):
    prefix = '/trainings'

    exercises = AdminTrainingExerciseRoute()
    reports = AdminTrainingReportRoute()

    async def get(self, id_: int):
        return await self.request(
            type_=RequestTypes.GET,
            prefix='/get',
            parameters={
                'id': id_,
            },
            response_key='training',
        )

    async def get_list(self, account_service_id: int, date: str = None):
        parameters = {'account_service_id': account_service_id}
        if date is not None:
            parameters['date'] = date
        return await self.request(
            type_=RequestTypes.GET,
            prefix='/list/get',
            parameters=parameters,
            response_key='trainings',
        )

    async def get_list_all(self):
        return await self.request(
            type_=RequestTypes.GET,
            prefix='/list/get/all',
            response_key='trainings',
        )

    async def create(self, account_service_id: int, date: str, article_id: int = None):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/create',
            parameters={
                'account_service_id': account_service_id,
                'date': date,
                'article_id': article_id,
            },
            response_key='id',
        )

    async def update(self, id_: int, date: str = None, article_id: int = None):
        parameters = {
            'id': id_,
            'article_id': article_id,
        }
        if date:
            parameters['date'] = date
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/update',
            parameters={
                'id': id_,
                'date': date,
                'article_id': article_id,
            },
        )

    async def delete(self, id_: int):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/delete',
            parameters={
                'id': id_,
            },
        )


