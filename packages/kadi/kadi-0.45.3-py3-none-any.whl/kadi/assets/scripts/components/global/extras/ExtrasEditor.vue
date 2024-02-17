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
  <div tabindex="-1" ref="editor">
    <div class="form-row align-items-center">
      <div class="col-md-3 mb-2 mb-md-0">
        <collapse-item class="text-default" :id="id">{{ label }}</collapse-item>
      </div>
      <div class="col-md-9 d-md-flex justify-content-end">
        <div class="btn-group btn-group-sm mr-1 mr-md-2">
          <button type="button"
                  class="btn btn-light"
                  tabindex="-1"
                  :title="`${$t('Undo')} (${$t('Ctrl')}+Z)`"
                  :disabled="treeView || !undoable"
                  @click="undo">
            <i class="fa-solid fa-rotate-left"></i>
          </button>
          <button type="button"
                  class="btn btn-light"
                  tabindex="-1"
                  :title="`${$t('Redo')} (${$t('Ctrl')}+Y)`"
                  :disabled="treeView || !redoable"
                  @click="redo">
            <i class="fa-solid fa-rotate-right"></i>
          </button>
          <button type="button"
                  class="btn btn-light"
                  tabindex="-1"
                  :title="$t('Paste extras')"
                  :disabled="treeView"
                  @click="showPasteDialog"
                  v-if="editingMode_">
            <i class="fa-solid fa-paste"></i>
          </button>
          <button type="button"
                  class="btn btn-light"
                  tabindex="-1"
                  :title="$t('Reset editor')"
                  :disabled="treeView"
                  @click="resetEditor"
                  v-if="editingMode_">
            <i class="fa-solid fa-rotate"></i>
          </button>
          <button type="button"
                  class="btn btn-light"
                  tabindex="-1"
                  :title="`${$t('Toggle mode')} (${$t('Ctrl')}+M)`"
                  :disabled="treeView"
                  @click="editingMode_ = !editingMode_">
            <span v-if="!editingMode_">{{ $t('Editing mode') }}</span>
            <span v-else>{{ $t('Simple mode') }}</span>
          </button>
        </div>
        <button type="button"
                class="btn btn-sm btn-light"
                tabindex="-1"
                :title="`${$t('Toggle view')} (${$t('Ctrl')}+E)`"
                @click="treeView = !treeView">
          <span v-if="treeView">
            <i class="fa-solid fa-pencil"></i> {{ $t('Editor view') }}
          </span>
          <span v-else>
            <i class="fa-solid fa-bars-staggered"></i> {{ $t('Tree view') }}
          </span>
        </button>
      </div>
    </div>
    <div :id="id" class="mt-2">
      <div class="pt-1" v-show="!treeView">
        <extras-editor-items :extras="extras"
                             :template-endpoint="templateEndpoint"
                             :enable-term-search="Boolean(termsEndpoint)"
                             :editing-mode="editingMode_"
                             @show-term-search="showTermSearch($event)"
                             @save-checkpoint="saveCheckpoint"
                             ref="extras">
          <div class="form-row align-items-center mt-2" v-if="templateEndpoint">
            <div class="offset-md-5 col-md-7 offset-xl-7 col-xl-5">
              <dynamic-selection container-classes="select2-single-sm"
                                 :placeholder="$t('Select a template')"
                                 :endpoint="templateEndpoint"
                                 :reset-on-select="true"
                                 @select="selectTemplate">
              </dynamic-selection>
            </div>
          </div>
        </extras-editor-items>
      </div>
      <div class="pt-1" v-show="treeView">
        <div class="card text-break overflow-auto">
          <div class="card-body py-1">
            <extras-editor-tree-view :extras="extras" @focus-extra="focusExtra"></extras-editor-tree-view>
          </div>
        </div>
      </div>
    </div>
    <input type="hidden" :name="name" :value="serializedExtras">
    <term-search :endpoint="termsEndpoint" @select-term="selectTerm" ref="termSearch" v-if="termsEndpoint">
    </term-search>
    <div class="modal" tabindex="-1" ref="pasteDialog" @change.stop>
      <div class="modal-dialog modal-dialog-centered modal-xl">
        <div class="modal-content">
          <div class="modal-header">
            <strong class="modal-title">{{ $t('Add extras as JSON') }}</strong>
            <button type="button" class="close" data-dismiss="modal">
              <i class="fa-solid fa-xmark fa-xs"></i>
            </button>
          </div>
          <div class="modal-body">
            <textarea class="form-control form-control-sm paste-area"
                      spellcheck="false"
                      rows="20"
                      :class="{'has-error': pastedExtrasError}"
                      v-model.trim="pastedExtras">
            </textarea>
            <div class="invalid-feedback" v-if="pastedExtrasError">{{ pastedExtrasError }}</div>
            <div class="row mt-2">
              <div class="col-6">
                <button type="button" class="btn btn-sm btn-primary" :disabled="!pastedExtras" @click="pasteExtras">
                  {{ $t('Add extras') }}
                </button>
              </div>
              <div class="col-6 d-flex justify-content-end">
                <button type="button" class="btn btn-sm btn-light" :disabled="!pastedExtras" @click="formatExtras">
                  {{ $t('Format JSON') }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.paste-area {
  font-family: monospace, monospace;
  font-size: 10pt;
}
</style>

<script>
import undoRedoMixin from 'scripts/components/mixins/undo-redo-mixin';

export default {
  mixins: [undoRedoMixin],
  data() {
    return {
      extras: [],
      numInitialFields: 3,
      currentExtra: null,
      pastedExtras: '',
      pastedExtrasError: '',
      treeView: false,
      editingMode_: this.editingMode,
    };
  },
  props: {
    id: {
      type: String,
      default: 'extras-editor',
    },
    name: {
      type: String,
      default: 'extras-editor',
    },
    label: {
      type: String,
      default: 'Extra metadata',
    },
    initialValues: {
      type: Array,
      default: () => [],
    },
    editExtraKeys: {
      type: Array,
      default: () => [],
    },
    templateEndpoint: {
      type: String,
      default: null,
    },
    termsEndpoint: {
      type: String,
      default: null,
    },
    editingMode: {
      type: Boolean,
      default: true,
    },
  },
  computed: {
    serializedExtras() {
      return JSON.stringify(this.serializeExtras(this.extras));
    },
  },
  methods: {
    serializeExtras(extras, nestedType = null) {
      const newExtras = [];

      for (const extra of extras) {
        if (this.extraIsEmpty(extra, nestedType)) {
          continue;
        }

        const newExtra = {
          type: extra.type.value,
          value: extra.value.value,
        };

        if (nestedType !== 'list') {
          newExtra.key = extra.key.value;
        }
        if (['int', 'float'].includes(newExtra.type)) {
          newExtra.unit = extra.unit.value;
        }

        for (const prop of ['description', 'term', 'validation']) {
          if (extra[prop].value) {
            newExtra[prop] = extra[prop].value;
          }
        }

        if (kadi.utils.isNestedType(newExtra.type)) {
          newExtra.value = this.serializeExtras(newExtra.value, newExtra.type);
        }

        newExtras.push(newExtra);
      }

      return newExtras;
    },
    extraIsEmpty(extra, nestedType = null) {
      if (nestedType === 'list') {
        return false;
      }

      for (const prop of ['key', 'value', 'unit', 'description', 'term', 'validation']) {
        if (extra[prop].value !== null) {
          return false;
        }
      }

      return true;
    },
    removeEmptyExtras() {
      this.extras.slice().forEach((extra) => {
        if (this.extraIsEmpty(extra)) {
          this.$refs.extras.removeExtra(extra, false);
        }
      });
    },
    initializeFields() {
      for (let i = 0; i < this.numInitialFields; i++) {
        this.$refs.extras.addExtra(null, null, false, false);
      }
    },
    showPasteDialog() {
      $(this.$refs.pasteDialog).modal();
    },
    pasteExtras() {
      let extras = null;

      try {
        extras = JSON.parse(this.pastedExtras);
      } catch {
        this.pastedExtrasError = $t('Invalid JSON data.');
        return;
      }

      try {
        if (!kadi.utils.isArray(extras)) {
          throw new Error();
        }

        this.$refs.extras.addExtras(extras, false);
        this.removeEmptyExtras();
      } catch {
        this.pastedExtrasError = $t('Invalid extras format.');
        return;
      }

      this.saveCheckpoint();

      this.pastedExtras = '';
      this.pastedExtrasError = '';
      $(this.$refs.pasteDialog).modal('hide');
    },
    formatExtras() {
      try {
        const extras = JSON.parse(this.pastedExtras);
        this.pastedExtras = JSON.stringify(extras, null, 2);
        this.pastedExtrasError = '';
      } catch {
        this.pastedExtrasError = $t('Invalid JSON data.');
      }
    },
    resetEditor() {
      const reset = () => {
        this.$refs.extras.removeExtras(false);
        this.initializeFields();
        this.saveCheckpoint();
      };

      // Only reset the editor if it is not in initial state already.
      if (this.extras.length === this.numInitialFields) {
        for (const extra of this.extras) {
          if (!this.extraIsEmpty(extra)) {
            reset();
            return;
          }
        }
      } else {
        reset();
      }
    },
    async selectTemplate(template) {
      const extras = await this.$refs.extras.loadTemplate(template.endpoint);
      this.removeEmptyExtras();
      this.$refs.extras.addExtras(extras);
    },
    focusExtra(extra) {
      this.treeView = false;
      this.$refs.extras.focusExtra(extra);
    },
    showTermSearch(extra) {
      this.currentExtra = extra;
      this.$refs.termSearch.showDialog(extra.key.value || '');
    },
    selectTerm(term) {
      this.currentExtra.term.value = term;
      this.saveCheckpoint();
    },
    keydownHandler(e) {
      if (e.ctrlKey) {
        switch (e.key) {
        case 'z':
          e.preventDefault();
          // Aside from keeping focus, this also forces a change event in case the shortcut is pressed while an input
          // field is still being edited. This in turn triggers the checkpoint creation before the undo function is
          // actually called.
          this.$refs.editor.focus();
          this.undo();
          break;
        case 'y':
          e.preventDefault();
          this.$refs.editor.focus();
          this.redo();
          break;
        case 'm':
          e.preventDefault();
          this.editingMode_ = !this.editingMode_;
          this.$refs.editor.focus();
          break;
        case 'e':
          e.preventDefault();
          this.treeView = !this.treeView;
          this.$refs.editor.focus();
          break;
        default:
        }
      }
    },
    getCheckpointData(triggerChange = true) {
      if (triggerChange) {
        // If applicable, dispatch a custom 'change' event as well every time a checkpoint is created.
        this.$el.dispatchEvent(new Event('change', {bubbles: true}));
      }

      const checkpointData = [];
      // Save a deep copy of the extra metadata.
      this.extras.forEach((extra) => checkpointData.push(this.$refs.extras.newExtra(extra)));
      return checkpointData;
    },
    restoreCheckpointData(data) {
      this.$refs.extras.removeExtras(false);
      this.$refs.extras.addExtras(data, false);
    },
  },
  mounted() {
    if (this.initialValues.length > 0) {
      this.$refs.extras.addExtras(this.initialValues, false);
    } else {
      this.initializeFields();
    }

    this.saveCheckpoint(false);

    if (this.editExtraKeys.length > 0) {
      let extra = null;
      let previousType = null;
      let currentExtras = this.extras;

      for (const key of this.editExtraKeys) {
        // Try to use the key as an index instead for list values.
        if (previousType === 'list') {
          const index = Number.parseInt(key, 10);
          if (window.isNaN(index) || index < 0 || index >= currentExtras.length) {
            break;
          }
          extra = currentExtras[index];
        } else {
          const result = currentExtras.find((extra) => extra.key.value === key);
          if (!result) {
            break;
          }
          extra = result;
        }

        previousType = extra.type.value;
        currentExtras = extra.value.value;

        // In case we can't continue with any nested values, just break out of the loop, even if not all keys were
        // processed yet.
        if (!kadi.utils.isArray(currentExtras)) {
          break;
        }
      }

      if (extra) {
        this.focusExtra(extra);
      }
    }

    this.$el.addEventListener('keydown', this.keydownHandler);
  },
  beforeDestroy() {
    $(this.$refs.pasteDialog).modal('dispose');
  },
};
</script>
