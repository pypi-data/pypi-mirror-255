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
    <popover-toggle trigger="hover" toggle-class="" placement="top">
      <template #toggle>
        <a :href="user._links.view"
           :target="openInNewTab ? '_blank' : false"
           :rel="openInNewTab ? 'noopener noreferrer' : false">
          <slot :user="user">
            <strong>{{ user.displayname }}</strong>
          </slot>
        </a>
      </template>
      <template #content>
        <span class="row">
          <span class="col-4" v-if="user._links.image">
            <img class="img-max-75 img-thumbnail" :src="user._links.image">
          </span>
          <span :class="{'col-8': user._links.image, 'col-12': !user._links.image}">
            <strong>{{ user.displayname }}</strong>
            <br>
            <p>@{{ user.identity.username }}</p>
            <span class="text-muted">{{ $t('Account type:') }} {{ user.identity.identity_name }}</span>
          </span>
        </span>
      </template>
    </popover-toggle>
  </span>
</template>

<script>
export default {
  props: {
    user: Object,
    openInNewTab: {
      type: Boolean,
      default: false,
    },
  },
};
</script>
