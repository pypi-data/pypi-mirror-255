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


from mybody_api_client.utils import BaseRoute
from .accounts import AdminAccountRoute
from .articles import AdminArticleRoute
from .countries import AdminCountryRoute
from .currencies import AdminCurrencyRoute
from .exercises import AdminExerciseRoute
from .images import AdminImageRoute
from .languages import AdminLanguageRoute
from .meals import AdminMealRoute
from .permissions import AdminPermissionRoute
from .products import AdminProductRoute
from .roles import AdminRoleRoute
from .services import AdminServiceRoute
from .texts import AdminTextRoute
from .timezones import AdminTimezoneRoute
from .trainings import AdminTrainingRoute


class AdminRoute(BaseRoute):
    prefix = '/admin'

    accounts = AdminAccountRoute()
    articles = AdminArticleRoute()
    countries = AdminCountryRoute()
    currencies = AdminCurrencyRoute()
    exercises = AdminExerciseRoute()
    images = AdminImageRoute()
    languages = AdminLanguageRoute()
    meals = AdminMealRoute()
    permissions = AdminPermissionRoute()
    products = AdminProductRoute()
    roles = AdminRoleRoute()
    services = AdminServiceRoute()
    texts = AdminTextRoute()
    timezones = AdminTimezoneRoute()
    trainings = AdminTrainingRoute()
