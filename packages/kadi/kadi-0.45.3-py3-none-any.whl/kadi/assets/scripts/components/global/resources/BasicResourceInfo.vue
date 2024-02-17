<!-- Copyright 2020 Karlsruhe Institute of Technology
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
  <span v-trim-ws>
    <span class="badge badge-primary badge-mt-plus font-weight-normal float-right ml-3"
          v-if="resource.type && showType">
      <!-- Check whether we are dealing with a template or a record. -->
      <span v-if="resource.data">{{ kadi.utils.capitalize(resource.type) }}</span>
      <span v-else>{{ kadi.utils.truncate(resource.type, 25) }}</span>
    </span>
    <small>
      <resource-visibility :visibility="resource.visibility"></resource-visibility>
    </small>
    <strong class="wb-break-word ml-2">{{ resource.title }}</strong>
    <br>
    <small>@{{ resource.identifier }}</small>
    <span v-if="showDescription">
      <br>
      <small class="text-muted" v-if="resource.plain_description">
        {{ kadi.utils.truncate(resource.plain_description, 100) }}
      </small>
      <small class="text-muted" v-else>
        <em>{{ $t('No description.') }}</em>
      </small>
    </span>
  </span>
</template>

<script>
export default {
  props: {
    resource: Object,
    showType: {
      type: Boolean,
      default: true,
    },
    showDescription: {
      type: Boolean,
      default: true,
    },
  },
};
</script>
