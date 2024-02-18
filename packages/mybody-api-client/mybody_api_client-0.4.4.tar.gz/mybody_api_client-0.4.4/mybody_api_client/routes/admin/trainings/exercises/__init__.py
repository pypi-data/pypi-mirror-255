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


class AdminTrainingExerciseRoute(BaseRoute):
    prefix = '/exercises'

    async def get(self, id_: int):
        return await self.request(
            type_=RequestTypes.GET,
            prefix='/get',
            parameters={
                'id': id_,
            },
            response_key='training_exercise',
        )

    async def get_list(self, training_id: int):
        return await self.request(
            type_=RequestTypes.GET,
            prefix='/list/get',
            parameters={
                'training_id': training_id,
            },
            response_key='training_exercises',
        )

    async def create(
            self,
            training_id: int,
            exercise_id: int,
            priority: int,
            value: int,
            rest: int,
    ):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/create',
            parameters={
                'training_id': training_id,
                'exercise_id': exercise_id,
                'priority': priority,
                'value': value,
                'rest': rest,
            },
            response_key='id',
        )

    async def update(
            self,
            id_: int,
            exercise_id: int = None,
            priority: int = None,
            value: int = None,
            rest: int = None,
    ):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/update',
            parameters={
                'id': id_,
                'exercise_id': exercise_id,
                'priority': priority,
                'value': value,
                'rest': rest,
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
