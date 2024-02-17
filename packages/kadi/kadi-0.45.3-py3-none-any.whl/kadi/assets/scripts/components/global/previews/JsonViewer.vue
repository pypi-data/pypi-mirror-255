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
  <div>
    <div class="mb-2" v-if="encoding && !isNested">
      <small class="text-muted">{{ $t('Detected encoding:') }} {{ encoding.toUpperCase() }}</small>
    </div>
    <div :class="{'card bg-light max-vh-75 overflow-auto px-3 py-2': !isNested}">
      <div v-if="isNestedValue(data)">
        <div v-for="(item, index_or_key) in data" :key="item.id">
          <div v-if="isNestedValue(item.value)">
            <collapse-item :id="item.id">
              <strong>
                <pre class="d-inline">{{ index_or_key }}:</pre>
              </strong>
            </collapse-item>
            <pre class="d-inline" v-if="kadi.utils.isArray(item.value) && item.value.length === 0">[]</pre>
            <pre class="d-inline"
                 v-else-if="kadi.utils.isObject(item.value) && Object.keys(item.value).length === 0">{}</pre>
            <json-viewer class="ml-4" :id="item.id" :json="item.value" :is-nested="true" v-else></json-viewer>
          </div>
          <div v-else>
            <strong>
              <pre class="d-inline">{{ index_or_key }}:</pre>
            </strong>
            <pre class="d-inline text-muted" v-if="item.value === null">null</pre>
            <pre class="d-inline" v-else>{{ JSON.stringify(item.value) }}</pre>
          </div>
        </div>
      </div>
      <div v-if="!isNestedValue(data)">
        <pre class="d-inline text-muted" v-if="data === null">null</pre>
        <pre class="d-inline" v-else>{{ JSON.stringify(data) }}</pre>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      data: null,
    };
  },
  props: {
    json: null,
    encoding: {
      type: String,
      default: null,
    },
    isNested: {
      type: Boolean,
      default: false,
    },
  },
  methods: {
    isNestedValue(value) {
      return kadi.utils.isArray(value) || kadi.utils.isObject(value);
    },
  },
  mounted() {
    if (kadi.utils.isArray(this.json)) {
      this.data = [];

      this.json.forEach((value) => {
        this.data.push({id: kadi.utils.randomAlnum(), value});
      });
    } else if (kadi.utils.isObject(this.json)) {
      this.data = {};

      for (const [key, value] of Object.entries(this.json)) {
        this.data[key] = {id: kadi.utils.randomAlnum(), value};
      }
    } else {
      this.data = this.json;
    }
  },
};
</script>
