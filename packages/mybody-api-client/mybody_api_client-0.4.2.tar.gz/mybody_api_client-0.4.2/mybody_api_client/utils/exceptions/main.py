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


from .base import ApiException


class ModelDoesNotExist(ApiException):
    code = 1000
    message = '{model} with {id_type} "{id_value}" does not exist'


class NotEnoughPermissions(ApiException):
    code = 1001
    message = 'Not enough permissions to execute'


class NoRequiredParameters(ApiException):
    code = 1002
    message = 'One of the following parameters must be filled in: {parameters}'


class ModelAlreadyExist(ApiException):
    code = 1003
    message = '{model} with {id_type} "{id_value}" already exist'
