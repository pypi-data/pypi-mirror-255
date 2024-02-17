<!-- Copyright 2022 Karlsruhe Institute of Technology
   -
   - Licensed under the Apache License, Version 2.0 (the "License");
   - you may not use this file except in compliance with the License.
   - You may obtain a copy of the License at
   -
   -     http://www.apache.org/licenses/LICENSE-2.0
   -
   - Unless required by applicable law or agreed to in writing, software
   - distributed under the License is distributed on an "AS IS" BASIS,
   - WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   - See the License for the specific language governing permissions and
   - limitations under the License. -->

<template>
  <markdown-editor :id="id"
                   :name="id"
                   :rows="16"
                   :initial-value="settings.input"
                   :link-endpoint="endpoints.link"
                   :image-endpoint="endpoints.image"
                   @input="onInput">
  </markdown-editor>
</template>

<script>
import dashboardSettingsMixin from 'scripts/components/mixins/dashboard-settings-mixin';

export default {
  mixins: [dashboardSettingsMixin],
  methods: {
    onInput(input) {
      this.settings_ = {input};
    },
  },
};
</script>
