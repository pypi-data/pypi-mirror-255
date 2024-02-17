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
  <div class="modal" tabindex="-1" ref="modalDialog">
    <div class="modal-dialog modal-dialog-centered modal-xl">
      <div class="modal-content">
        <div class="modal-header">
          <strong class="modal-title">{{ $t('Edit dashboard panel') }}</strong>
          <button type="button" class="close" data-dismiss="modal">
            <i class="fa-solid fa-xmark fa-xs"></i>
          </button>
        </div>
        <div class="modal-body">
          <div v-if="panel_">
            <form>
              <div class="form-group">
                <label>{{ $t('Title') }}</label>
                <input class="form-control" v-model="panel_.title">
              </div>
              <div class="form-group">
                <label>{{ $t('Subtitle') }}</label>
                <input class="form-control" v-model="panel_.subtitle">
              </div>
            </form>

            <div v-if="panel_.settingsComponent">
              <hr>
              <component :is="panel_.settingsComponent"
                         :id="panel_.i"
                         :settings="panel_.settings"
                         :endpoints="endpoints"
                         @settings-updated="onSettingsUpdated">
              </component>
            </div>
          </div>
        </div>
        <div class="modal-footer d-block">
          <button type="button" class="btn btn-primary" data-dismiss="modal" @click="$emit('panel-updated', panel_)">
            {{ $t('Apply') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import DashboardMarkdownSettings from 'DashboardMarkdownSettings.vue';

export default {
  components: {
    DashboardMarkdownSettings,
  },
  data() {
    return {
      panel_: {},
    };
  },
  props: {
    panel: Object,
    endpoints: Object,
  },
  watch: {
    panel() {
      this.panel_ = kadi.utils.deepClone(this.panel);
    },
  },
  methods: {
    show() {
      $(this.$refs.modalDialog).modal();
    },
    onSettingsUpdated(newSettings) {
      this.panel_.settings = newSettings;
    },
  },
  beforeDestroy() {
    $(this.$refs.modalDialog).modal('dispose');
  },
};
</script>
