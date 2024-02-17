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
  <div>
    <div class="row">
      <div class="col-md-6 mb-2 mb-md-0">
        <button type="button" class="btn btn-sm btn-light" :disabled="!showDiff" @click="toggleComparison">
          <i class="fa-solid fa-repeat"></i>
          <span v-if="compareLatest_">{{ $t('Compare to previous revision') }}</span>
          <span v-else>{{ $t('Compare to current state') }}</span>
        </button>
      </div>
      <div class="col-md-6 d-md-flex justify-content-end">
        <div>
          <button type="button" class="btn btn-sm btn-light" @click="toggleDiff">
            <span v-if="showDiff">
              <i class="fa-solid fa-eye"></i> {{ $t('Show current revision') }}
            </span>
            <span v-else>
              <i class="fa-solid fa-code-compare"></i> {{ $t('Show changes') }}
            </span>
          </button>
        </div>
      </div>
    </div>
    <hr>
    <div v-if="!loading">
      <div class="row mb-2">
        <span class="col-md-3">{{ $t('Persistent ID') }}</span>
        <span class="col-md-9">{{ revision.id }}</span>
      </div>
      <!-- If we don't have a link to the object itself, we probably don't care about the ID anyways. -->
      <div class="row mb-2" v-if="revision._links.view_object">
        <span class="col-md-3">{{ $t('Object ID') }}</span>
        <a class="col-md-9" :href="revision._links.view_object">
          <strong>{{ revision.object_id }}</strong>
        </a>
      </div>
      <div class="row mb-2">
        <span class="col-md-3">{{ $t('User') }}</span>
        <span class="col-md-9">
          <identity-popover :user="revision.user" v-if="revision.user"></identity-popover>
          <em class="text-muted" v-else>{{ $t('No user.') }}</em>
        </span>
      </div>
      <div class="row">
        <span class="col-md-3">{{ $t('Timestamp') }}</span>
        <div class="col-md-9">
          <local-timestamp :timestamp="revision.timestamp"></local-timestamp>
          <br>
          <small class="text-muted">
            (<from-now :timestamp="revision.timestamp"></from-now>)
          </small>
        </div>
      </div>
      <hr>
      <div v-if="showDiff">
        <div class="card bg-light mb-3">
          <div class="card-body py-2">
            <i class="fa-solid fa-circle-info"></i>
            <small>
              <strong v-if="compareLatest_">{{ $t('Comparing to current state') }}</strong>
              <strong v-else>{{ $t('Comparing to previous revision') }}</strong>
            </small>
          </div>
        </div>
      </div>
      <em class="text-muted" v-if="showDiff && !hasDiff()">{{ $t('No changes.') }}</em>
      <div v-for="(value, prop) in revision.data" :key="prop">
        <div v-if="!showDiff || hasDiff(prop)">
          <div class="row mt-3">
            <div class="col-md-3">
              <strong>{{ revisionProp(prop) }}</strong>
            </div>
            <div class="col-md-9">
              <clipboard-button class="btn-sm float-right py-0 m-1 ml-2"
                                :content="revisionClipboardValue(value)"
                                v-if="!showDiff">
              </clipboard-button>
              <div class="bg-light rounded p-2">
                <pre class="mb-0 py-2" v-if="showDiff"><!--
               --><div v-for="(part, partIndex) in getDiff(prop)"
                       :class="{'font-italic': part.value === null}"
                       :key="partIndex"><!--
                 --><span class="mb-0 diff-add" v-if="part.added">{{ revisionValue(part.value) }}</span><!--
                 --><span class="mb-0 diff-delete" v-else-if="part.removed">{{ revisionValue(part.value) }}</span><!--
                 --><span class="mb-0" v-else>{{ revisionValue(part.value) }}</span><!--
               --></div><!--
             --></pre>
                <div v-else>
                  <pre class="mb-0 py-2" :class="{'font-italic': value === null}">{{ revisionValue(value) }}</pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <i class="fa-solid fa-circle-notch fa-spin" v-if="loading"></i>
  </div>
</template>

<style scoped>
pre {
  font-size: 90%;
}

.diff-add {
  color: #009933;
}

.diff-delete {
  color: #ff0000;
}
</style>

<script>
import {diffJson} from 'diff';

export default {
  data() {
    return {
      revision: null,
      loading: true,
      showDiff: true,
      compareLatest_: this.compareLatest,
    };
  },
  props: {
    endpoint: String,
    latestRevision: Number,
    compareLatest: {
      type: Boolean,
      default: false,
    },
  },
  methods: {
    revisionProp(prop) {
      return kadi.utils.capitalize(prop).split('_').join(' ');
    },
    revisionValue(value) {
      return value === null ? 'null' : value;
    },
    revisionClipboardValue(value) {
      if (typeof value === 'string') {
        return value;
      }

      return JSON.stringify(value, null, 2);
    },
    hasDiff(prop = null) {
      if (prop === null) {
        return Object.keys(this.revision.diff).length > 0;
      }

      return Boolean(this.revision.diff[prop]);
    },
    getDiff(prop) {
      const diff = this.revision.diff[prop];

      if (diff) {
        // As the null values are converted into strings when using 'diffJson', we handle these cases separately instead
        // in order to visualize null values differently in the DOM.
        if (diff.prev === null) {
          return [{removed: true, value: null}, {added: true, value: diff.new}];
        } else if (diff.new === null) {
          return [{removed: true, value: diff.prev}, {added: true, value: null}];
        }

        return diffJson(diff.prev, diff.new);
      }

      return [{value: this.revision.data[prop]}];
    },
    async loadRevision() {
      this.loading = true;

      const config = {};

      if (this.compareLatest_ && this.latestRevision) {
        config.params = {revision: this.latestRevision};
      }

      try {
        const response = await axios.get(this.endpoint, config);

        this.revision = response.data;
        this.loading = false;
      } catch (error) {
        kadi.base.flashDanger($t('Error loading revision.'), {request: error.request});
      }
    },
    toggleComparison() {
      this.compareLatest_ = !this.compareLatest_;
      this.loadRevision();
    },
    toggleDiff() {
      this.showDiff = !this.showDiff;
    },
  },
  mounted() {
    this.loadRevision();
  },
};
</script>
