#
# (c) 2023, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
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


from inspect import getfullargspec

from flet_core import Text, View

from flet_manager.utils import Client


class BaseView(View):
    route: str = '/'
    title: str = 'View'
    client: Client
    params: dict

    def __init__(self, **kwargs):
        self.params = {}

        params_parent = {}
        params_required = getfullargspec(super().__init__).args

        for key, value in kwargs.items():
            if key in params_required:
                params_parent[key] = value
            self.params[key] = value

        super().__init__(
            **params_parent,
            route=self.route,
        )

    async def build(self):
        self.controls = []

    async def restart(self):
        await self.build()
        await self.update_async()
        await self.on_load()
        await self.update_async()

    async def on_load(self):
        pass
