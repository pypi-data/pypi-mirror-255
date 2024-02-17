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
    <confirm-dialog ref="dialog"></confirm-dialog>
    <grid-item class="d-flex flex-column"
               :key="panel.i"
               :x="panel.x"
               :y="panel.y"
               :w="panel.w"
               :h="panel.h"
               :i="panel.i"
               :is-draggable="editable"
               :is-resizable="editable"
               @resize="() => isResizing = true"
               @resized="() => isResizing = false">

      <div class="d-flex justify-content-between">
        <div class="flex-grow-1">
          <div class="h5 mb-0 font-weight-bold">
            {{ panel.title }}
          </div>
          <div class="text-muted" v-if="panel.subtitle">
            {{ panel.subtitle }}
          </div>
        </div>
        <div v-if="editable" class="flex-shrink-0">
          <span class="dashboard-panel-action"
                @click="$emit('show-panel-settings', panel)">
            <i class="fa-solid fa-gear"></i>
          </span>
          <span class="dashboard-panel-action ml-2" @click="removePanel">
            <i class="fa-solid fa-xmark"></i>
          </span>
        </div>
      </div>

      <div v-if="panel.viewComponent" class="w-100 h-100 overflow-hidden">
        <component :is="panel.viewComponent" :settings="panel.settings"></component>
      </div>

      <div class="info user-select-none" v-if="isResizing">
        {{ panel.w }}x{{ panel.h }}
      </div>
    </grid-item>
  </div>
</template>

<style lang="scss" scoped>
.dashboard-panel-action {
  color: #95a5a6;

  &:hover {
    color: black;
    cursor: pointer;
  }
}

.info {
  bottom: 0;
  position: absolute;
  right: -3em;
}

.vue-grid-item {
  touch-action: none;

  &:not(.vue-grid-placeholder) {
    background-color: white;
    border: 1px solid #ced4da;
    border-radius: 0.5rem;
    padding: 0.5rem;
  }

  &.vue-draggable-dragging {
    opacity: 0.5;
  }
}
</style>

<script>
import VueGridLayout from 'vue-grid-layout';
import DashboardMarkdownPanel from 'DashboardMarkdownPanel.vue';

export default {
  components: {
    GridItem: VueGridLayout.GridItem,
    DashboardMarkdownPanel,
  },
  data() {
    return {
      isResizing: false,
    };
  },
  props: {
    editable: Boolean,
    panel: Object,
  },
  methods: {
    async removePanel() {
      const input = await this.$refs.dialog.open($t('Are you sure you want to remove this panel?'));

      if (input.status) {
        this.$emit('remove-panel', this.panel);
      }
    },
  },
};
</script>
