<!-- Copyright 2021 Karlsruhe Institute of Technology
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
  <card-deck :items="resources" :max-cards="2">
    <template #default="props">
      <div class="card-header py-1" v-if="props.item.pretty_type">
        <strong>{{ props.item.pretty_type }}</strong>
      </div>
      <div class="card-body py-3">
        <a class="text-default stretched-link" :href="props.item._links.view">
          <span class="badge badge-primary badge-mt-plus font-weight-normal float-right ml-3" v-if="props.item.type">
            <!-- Check whether we are dealing with a template or a record. -->
            <span v-if="props.item.data">{{ kadi.utils.capitalize(props.item.type) }}</span>
            <span v-else>{{ kadi.utils.truncate(props.item.type, 25) }}</span>
          </span>
          <img class="img-max-75 img-thumbnail float-right ml-2"
               :src="props.item._links.image"
               v-if="props.item._links.image">
          <div v-trim-ws>
            <small>
              <resource-visibility :visibility="props.item.visibility"></resource-visibility>
            </small>
            <strong class="wb-break-word ml-2">{{ props.item.title }}</strong>
            <br>
            @{{ props.item.identifier }}
          </div>
          <div class="mt-2">
            <span class="text-muted" v-if="props.item.plain_description">
              {{ kadi.utils.truncate(props.item.plain_description, 150) }}
            </span>
            <em class="text-muted" v-else>{{ $t('No description.') }}</em>
          </div>
        </a>
      </div>
      <div class="card-footer py-1">
        <small class="text-muted">
          {{ $t('Last modified') }} <from-now :timestamp="props.item.last_modified"></from-now>
        </small>
      </div>
    </template>
  </card-deck>
</template>

<script>
export default {
  props: {
    resources: Array,
  },
};
</script>
