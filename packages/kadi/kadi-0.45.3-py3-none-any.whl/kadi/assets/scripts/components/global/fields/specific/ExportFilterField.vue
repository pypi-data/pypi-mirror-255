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
  <div class="form-group">
    <label class="form-control-label">{{ field.label }}</label>
    <resource-export-filter :resource-type="resourceType"
                            :export-type="exportType"
                            :extras="extras"
                            :allow-extras-propagation="allowExtrasPropagation"
                            :default-user-filter="defaultUserFilter"
                            @filter="filter = $event">
    </resource-export-filter>
    <small class="form-text text-muted">{{ field.description }}</small>
    <input type="hidden" :name="field.name" :value="JSON.stringify(filter)">
  </div>
</template>

<script>
export default {
  data() {
    return {
      filter: {},
    };
  },
  props: {
    field: Object,
    resourceType: String,
    exportType: {
      type: String,
      default: null,
    },
    extras: {
      type: Array,
      default: () => [],
    },
    allowExtrasPropagation: {
      type: Boolean,
      default: true,
    },
    defaultUserFilter: {
      type: Boolean,
      default: false,
    },
  },
};
</script>
