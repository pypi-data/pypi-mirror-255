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

    <dashboard-panel-settings ref="panelSettings"
                              :panel="editedPanel"
                              :endpoints="endpoints"
                              @panel-updated="onPanelUpdated">
    </dashboard-panel-settings>

    <div v-if="!inEditMode" class="row">
      <div class="col-lg-8 mb-2 mb-lg-0">
        <button type="button" class="btn btn-sm btn-primary" :disabled="!isEditable" @click="newDashboard">
          <i class="fa-solid fa-plus"></i> {{ $t('New') }}
        </button>
        <button type="button"
                class="btn btn-sm btn-light"
                :disabled="!isEditable"
                v-if="selectedDashboardFile"
                @click="enterEditMode">
          <i class="fa-solid fa-pencil"></i> {{ $t('Edit') }}
        </button>
        <button type="button"
                class="btn btn-sm btn-danger"
                :disabled="!isEditable"
                v-if="selectedDashboardFile"
                @click="deleteDashboard">
          <i class="fa-solid fa-trash"></i> {{ $t('Delete') }}
        </button>
      </div>

      <div class="col-lg-4 d-flex align-items-center">
        <dynamic-selection container-classes="select2-single-sm"
                           :placeholder="$t('Select a dashboard')"
                           :endpoint="selectEndpoint"
                           :reset-on-select="true"
                           @select="selectDashboard">
        </dynamic-selection>
      </div>
    </div>

    <div class="row" v-if="inEditMode">
      <div class="col-md-10 mb-2 mb-md-0">
        <button type="button" class="btn btn-sm btn-primary" @click="saveDashboard" :disabled="!unsavedChanges_">
          <i class="fa-solid fa-floppy-disk"></i> {{ $t('Save') }}
        </button>
        <button type="button" class="btn btn-sm btn-light" @click="cancelEditMode">
          <i class="fa-solid fa-ban"></i> {{ $t('Cancel') }}
        </button>
        <div class="input-group input-group-sm d-sm-inline-flex w-auto mt-2 mt-sm-0">
          <div class="input-group-prepend">
            <span class="input-group-text">{{ $t('Name') }}</span>
          </div>
          <input class="form-control" v-model="activeDashboard.name">
        </div>
      </div>

      <div class="col-md-2 d-md-flex justify-content-end">
        <div class="dropdown">
          <button type="button" class="btn btn-sm btn-light dropdown-toggle" data-toggle="dropdown">
            {{ $t('Add panel') }}
          </button>
          <div class="dropdown-menu">
            <a v-for="(availablePanel, i) in availablePanels"
               :key="i"
               class="dropdown-item"
               href="#"
               @click="addPanel(availablePanel)">
              {{ availablePanel.name }}
            </a>
          </div>
        </div>
      </div>
    </div>

    <hr>

    <em v-if="state === 'empty'" class="text-muted">{{ $t('No dashboard selected.') }}</em>
    <i v-else-if="state === 'loading'" class="fa-solid fa-circle-notch fa-spin"></i>
    <div v-else-if="state === 'loaded'">
      <grid-layout class="dashboard-content"
                   :class="{'grid-lines': inEditMode}"
                   :layout.sync="activeDashboard.panels"
                   :col-num="12"
                   :row-height="50"
                   :is-draggable="true"
                   :is-resizable="true"
                   :is-mirrored="false"
                   :vertical-compact="false"
                   :prevent-collision="true"
                   :margin="[0, 0]"
                   :use-css-transforms="true">
        <dashboard-panel v-for="panel in activeDashboard.panels"
                         :key="panel.i"
                         :panel="panel"
                         :editable="inEditMode"
                         @show-panel-settings="showPanelSettings"
                         @remove-panel="removePanel">
        </dashboard-panel>
      </grid-layout>
    </div>
  </div>
</template>

<style lang="scss" scoped>
$col-num: 12;
$row-height: 50px;

.dashboard-content {
  min-height: $row-height * 4;
}

.grid-lines {
  background-image:
    repeating-linear-gradient(#ccc 0 1px, transparent 1px 100%),
    repeating-linear-gradient(90deg, #ccc 0 1px, transparent 1px 100%);
  background-size: calc(100% / $col-num) $row-height;
  border-bottom: 1px solid #ccc;
  border-right: 1px solid #ccc;
}

::v-deep .vue-grid-item.vue-grid-placeholder {
  background: green !important;
  border-radius: 0.5rem;
}
</style>

<script>
import VueGridLayout from 'vue-grid-layout';

import {Upload, UploadProvider} from 'scripts/lib/uploads.js';
import DashboardPanel from 'scripts/components/lib/dashboards/DashboardPanel.vue';
import DashboardPanelSettings from 'scripts/components/lib/dashboards/DashboardPanelSettings.vue';

export default {
  components: {
    GridLayout: VueGridLayout.GridLayout,
    DashboardPanel,
    DashboardPanelSettings,
  },
  data() {
    return {
      activeDashboard: {
        name: 'dashboard',
        panels: [],
      },
      editModeDashboard: {
        name: 'dashboard',
        panels: [],
      },
      editedPanel: null,
      state: 'empty',
      inEditMode: false,
      uploadProvider: null,
      selectedDashboardFile: null,
      availablePanels: [
        {
          'name': 'Markdown',
          'viewComponent': 'DashboardMarkdownPanel',
          'settingsComponent': 'DashboardMarkdownSettings',
        },
      ],
      unsavedChanges_: false,
    };
  },
  props: {
    selectEndpoint: String,
    uploadEndpoint: String,
    linkEndpoint: String,
    imageEndpoint: String,
    unsavedChanges: {
      type: Boolean,
      default: false,
    },
  },
  watch: {
    uploadEndpoint() {
      this.initUploadProvider();
    },
    unsavedChanges() {
      this.unsavedChanges_ = this.unsavedChanges;
    },
    unsavedChanges_() {
      this.$emit('unsaved-changes', this.unsavedChanges_);
    },
    activeDashboard: {
      handler() {
        this.unsavedChanges_ = true && this.inEditMode;
      },
      deep: true,
    },
  },
  computed: {
    isEditable() {
      return this.uploadProvider !== null;
    },
    endpoints() {
      return {
        image: this.imageEndpoint,
        link: this.linkEndpoint,
      };
    },
  },
  methods: {
    initUploadProvider() {
      if (!this.uploadEndpoint) {
        return;
      }

      this.uploadProvider = new UploadProvider(this.uploadEndpoint, this.onUploadReplace, this.onUploadSuccess);
    },
    addPanel(selectedPanel) {
      // Always add panel manually at the end. The lib would place it at the first free spot which could destroy the
      // existing layout.
      const maxY = Math.max(0, ...this.activeDashboard.panels.map((panel) => panel.y + panel.h));
      const item = {
        x: 0,
        y: maxY,
        w: 4,
        h: 4,
        i: kadi.utils.randomAlnum(),
        title: $t('Title'),
        subtitle: $t('Subtitle'),
        settings: {},
        viewComponent: selectedPanel.viewComponent,
        settingsComponent: selectedPanel.settingsComponent,
      };

      this.activeDashboard.panels.push(item);
    },
    removePanel(selectedPanel) {
      const index = this.activeDashboard.panels.indexOf(selectedPanel);

      if (index > -1) {
        this.activeDashboard.panels.splice(index, 1);
      }
    },
    findPanel(i) {
      return this.activeDashboard.panels.find((item) => item.i === i);
    },
    enterEditMode() {
      this.inEditMode = true;
      this.editModeDashboard = kadi.utils.deepClone(this.activeDashboard);

      // Switch references so that we see the copy of the original dashboard.
      [this.activeDashboard, this.editModeDashboard] = [this.editModeDashboard, this.activeDashboard];

      this.$nextTick(() => this.unsavedChanges_ = false);
    },
    cancelEditMode() {
      // Switch back to the original (unchanged) dashboard.
      [this.activeDashboard, this.editModeDashboard] = [this.editModeDashboard, this.activeDashboard];
      this.editModeDashboard.panels = [];

      this.leaveEditMode();

      // New dashboard is not saved and canceled.
      if (!this.selectedDashboardFile) {
        this.state = 'empty';
      }
    },
    leaveEditMode() {
      this.inEditMode = false;
      this.editedPanel = null;
    },
    newDashboard() {
      this.selectedDashboardFile = null;

      this.initDashboard({
        name: `dashboard_${kadi.utils.randomAlnum(10)}`,
        panels: [],
      });
      this.enterEditMode();
    },
    initDashboard(dashboard) {
      this.resetDashboard();

      this.activeDashboard = dashboard;
      this.state = 'loaded';
    },
    resetDashboard() {
      this.leaveEditMode();

      this.activeDashboard = {
        name: 'dashboard',
        panels: [],
      };
      this.editModeDashboard = {
        name: 'dashboard',
        panels: [],
      };
      this.state = 'empty';
    },
    saveDashboard() {
      if (!this.isEditable || !this.activeDashboard.name) {
        kadi.base.flashDanger($t('Error saving dashboard.'));
        return;
      }

      const file = new File([JSON.stringify(this.activeDashboard, null, 2)], `${this.activeDashboard.name}.json`);
      const upload = new Upload(file.name, file.size, 'local', file);

      this.uploadProvider.upload(upload);
    },
    async loadDashboard(endpoint) {
      this.state = 'loading';

      try {
        const response = await axios.get(endpoint);
        this.initDashboard(response.data);
      } catch (error) {
        kadi.base.flashDanger($t('Error loading dashboard.'), {request: error.request});
      }
    },
    async deleteDashboard() {
      if (!this.selectedDashboardFile) {
        return;
      }

      const input = await this.$refs.dialog.open($t('Are you sure you want to delete this dashboard?'));

      if (!input.status) {
        return;
      }

      try {
        await axios.delete(this.selectedDashboardFile.deleteEndpoint);

        kadi.base.flashSuccess($t('Dashboard deleted successfully.'), {scrollTo: false});

        this.resetDashboard();
        this.selectDashboard(null);
      } catch (error) {
        kadi.base.flashDanger($t('Error deleting dashboard.'), {request: error.request});
      }
    },
    selectDashboard(file) {
      if (file) {
        this.selectedDashboardFile = {
          downloadEndpoint: file.download_endpoint,
          deleteEndpoint: file.delete_endpoint,
        };
        this.loadDashboard(this.selectedDashboardFile.downloadEndpoint);
      } else {
        this.selectedDashboardFile = null;
      }
    },
    showPanelSettings(panel) {
      this.editedPanel = panel;
      this.$refs.panelSettings.show();
    },
    onPanelUpdated(editedPanel) {
      const panel = this.findPanel(editedPanel.i);

      panel.title = editedPanel.title;
      panel.subtitle = editedPanel.subtitle;
      panel.settings = editedPanel.settings;
    },
    async onUploadReplace(upload) {
      const msg = $t(
        'A file with the name "{{filename}}" already exists in the current record. Do you want to replace it?',
        {filename: upload.name},
      );

      const input = await this.$refs.dialog.open(msg);
      return input.status;
    },
    onUploadSuccess(upload, file) {
      this.selectedDashboardFile = {
        downloadEndpoint: file._links.download,
        deleteEndpoint: file._actions.delete,
      };

      this.unsavedChanges_ = false;
      this.leaveEditMode();

      kadi.base.flashSuccess($t('Dashboard saved successfully.'), {scrollTo: false});
    },
    beforeUnload(e) {
      if (this.unsavedChanges_) {
        e.preventDefault();
        return '';
      }
      return null;
    },
  },
  mounted() {
    const sortByName = (a, b) => (a.name.toLowerCase() > b.name.toLowerCase() ? 1 : -1);

    if (kadi.globals.environment === 'development') {
      this.availablePanels.push({
        'name': 'Empty Panel',
        'viewComponent': null,
        'settingsComponent': null,
      });
    }

    // Sort the list of available panels in ascending order for better UX.
    this.availablePanels.sort(sortByName);
    this.initUploadProvider();

    window.addEventListener('beforeunload', this.beforeUnload);
  },
  beforeDestroy() {
    this.editor.destroy();
    window.removeEventListener('beforeunload', this.beforeUnload);
  },
};
</script>
