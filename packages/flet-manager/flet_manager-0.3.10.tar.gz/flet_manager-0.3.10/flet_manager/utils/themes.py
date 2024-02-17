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


from flet_core import Theme


light_default = Theme(
    color_scheme_seed='#1d1d1d',
)
dark_default = Theme(
    color_scheme_seed='#ffffff',
)


class Themes:
    light: Theme
    dark: Theme

    def __init__(self, light: Theme = light_default, dark: Theme = dark_default):
        self.light = light
        self.dark = dark

    def get(self):
        return self.light, self.dark
