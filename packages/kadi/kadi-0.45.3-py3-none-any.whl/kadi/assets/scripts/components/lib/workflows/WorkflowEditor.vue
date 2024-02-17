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
  <div ref="container">
    <confirm-dialog ref="dialog"></confirm-dialog>
    <div v-if="toolsEndpoint">
      <div class="modal" tabindex="-1" ref="toolDialog">
        <div class="modal-dialog modal-dialog-centered modal-xl">
          <div class="modal-content">
            <div class="modal-header">
              <strong class="modal-title">Add tools</strong>
              <button type="button" class="close" data-dismiss="modal">
                <i class="fa-solid fa-xmark fa-xs"></i>
              </button>
            </div>
            <div class="modal-body">
              <dynamic-pagination placeholder="No tools."
                                  filter-placeholder="Filter by filename or record identifier"
                                  :endpoint="toolsEndpoint"
                                  :per-page="5"
                                  :enable-filter="true">
                <template #default="props">
                  <ul class="list-group" v-if="props.total > 0">
                    <li class="list-group-item bg-light py-2">
                      <div class="row">
                        <div class="col-lg-5">Tool</div>
                        <div class="col-lg-5">File</div>
                      </div>
                    </li>
                    <li class="list-group-item py-2" v-for="item in props.items" :key="item.id">
                      <div class="row align-items-center">
                        <div class="col-lg-5 mb-2 mb-lg-0">
                          <div v-if="item.tool">
                            <strong>{{ item.tool.name }}</strong>
                            <small>[{{ item.tool.type }}]</small>
                            <span v-if="item.tool.version">
                              <br>
                              Version {{ item.tool.version }}
                            </span>
                          </div>
                          <div v-else>
                            <em class="text-muted">Invalid tool description.</em>
                          </div>
                        </div>
                        <div class="col-lg-5 mb-2 mb-lg-0">
                          <strong>{{ item.file }}</strong>
                          <br>
                          @{{ item.record }}
                        </div>
                        <div class="col-lg-2 d-lg-flex justify-content-end">
                          <div>
                            <button type="button"
                                    class="btn btn-light btn-sm"
                                    :disabled="!item.tool"
                                    @click="addTool(item.tool)">
                              <i class="fa-solid fa-plus"></i>
                            </button>
                          </div>
                        </div>
                      </div>
                    </li>
                  </ul>
                </template>
              </dynamic-pagination>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="card toolbar" ref="toolbar">
      <div class="card-body px-1 py-0">
        <button type="button" title="Reset view" :class="toolbarBtnClasses" @click="resetView">
          <i class="fa-solid fa-eye"></i>
        </button>
        <button type="button" title="Toggle fullscreen" :class="toolbarBtnClasses" @click="toggleFullscreen">
          <i class="fa-solid fa-expand"></i>
        </button>
        <button type="button" title="Reset editor" :class="toolbarBtnClasses" v-if="editable" @click="resetEditor">
          <i class="fa-solid fa-broom"></i>
        </button>
      </div>
    </div>
    <div class="card editor-container" :class="{'bg-light': !editable}" ref="editorContainer">
      <div ref="editor"></div>
    </div>
    <slot :editor="editor"></slot>
  </div>
</template>

<style scoped>
.editor-container {
  border: 1px solid #ced4da;
  border-radius: 0px;
}

.toolbar {
  border-bottom-left-radius: 0px;
  border-bottom-right-radius: 0px;
  border-color: #ced4da;
  margin-bottom: -1px;
}
</style>

<script>
import 'regenerator-runtime';

import AreaPlugin from 'rete-area-plugin';
import ConnectionPlugin from 'rete-connection-plugin';
import ContextMenuPlugin from 'rete-context-menu-plugin';
import VueRenderPlugin from 'rete-vue-render-plugin';

import WorkflowEditor from 'scripts/lib/workflows/editor';
import {ToolComponent} from 'scripts/lib/workflows/components/core';
import VueMenu from 'scripts/components/lib/workflows/view/Menu.vue';

import annotationComponents from 'scripts/lib/workflows/components/annotation-components';
import controlComponents from 'scripts/lib/workflows/components/control-components';
import fileIoComponents from 'scripts/lib/workflows/components/file-io-components';
import miscComponents from 'scripts/lib/workflows/components/misc-components';
import sourceComponents from 'scripts/lib/workflows/components/source-components';
import userInputComponents from 'scripts/lib/workflows/components/user-input-components';
import userOutputComponents from 'scripts/lib/workflows/components/user-output-components';

import 'styles/workflows/workflow-editor.scss';

export default {
  data() {
    return {
      version: 'kadi@0.1.0',
      editor: null,
      area: null,
      unsavedChanges_: false,
      menuItems: {},
      currX: 0,
      currY: 0,
    };
  },
  props: {
    editable: {
      type: Boolean,
      default: true,
    },
    workflowUrl: {
      type: String,
      default: null,
    },
    toolsEndpoint: {
      type: String,
      default: null,
    },
    unsavedChanges: {
      type: Boolean,
      default: false,
    },
    isRendered: {
      type: Boolean,
      default: true,
    },
  },
  computed: {
    toolbarBtnClasses() {
      return 'btn btn-link text-primary my-1';
    },
  },
  watch: {
    workflowUrl() {
      this.loadWorkflow(this.workflowUrl);
    },
    unsavedChanges() {
      this.unsavedChanges_ = this.unsavedChanges;
    },
    unsavedChanges_() {
      this.$emit('unsaved-changes', this.unsavedChanges_);
    },
    isRendered() {
      this.resizeView(false);
    },
  },
  methods: {
    resetView() {
      this.area.zoomAt(this.editor);
    },
    toggleFullscreen() {
      kadi.utils.toggleFullscreen(this.$refs.container);
    },
    async resetEditor() {
      const input = await this.$refs.dialog.open('Are you sure you want to reset the editor?');

      if (!input.status) {
        return;
      }

      this.editor.clear();
      this.unsavedChanges_ = false;
    },
    resizeView(resetView = true) {
      if (!this.isRendered) {
        return;
      }

      const toolbar = this.$refs.toolbar;
      const editorContainer = this.$refs.editorContainer;

      if (kadi.utils.isFullscreen()) {
        const toolbarHeight = Math.round(toolbar.getBoundingClientRect().height);

        editorContainer.style.height = `calc(100vh - ${toolbarHeight - 1}px)`;
        toolbar.style.borderTopLeftRadius = toolbar.style.borderTopRightRadius = '0';
      } else {
        const containerWidth = Math.round(editorContainer.getBoundingClientRect().width);
        const containerHeight = Math.round(window.innerHeight / window.innerWidth * containerWidth);

        editorContainer.style.height = `${containerHeight}px`;
        toolbar.style.borderTopLeftRadius = toolbar.style.borderTopRightRadius = '0.25rem';
      }

      this.editor.view.resize();

      if (resetView) {
        this.resetView();
      }
    },
    async loadWorkflow(url) {
      try {
        const response = await axios.get(url);

        try {
          if (!await this.editor.fromFlow(response.data)) {
            kadi.base.flashWarning('Could not fully reconstruct workflow.');
          }
        } catch (error) {
          console.error(error);
          kadi.base.flashDanger('Error parsing workflow data.');
        } finally {
          this.resetView();
        }
      } catch (error) {
        kadi.base.flashDanger('Error loading workflow.', {request: error.request});
      }
    },
    addTool(tool) {
      const componentName = ToolComponent.nameFromTool(tool);

      // Register the tool node if it is missing.
      if (!this.editor.components.has(componentName)) {
        this.editor.register(new ToolComponent(tool));
      }

      this.addNode(this.editor.components.get(componentName));
    },
    async addNode(component) {
      const node = await component.createNode();

      node.position[0] = this.currX;
      node.position[1] = this.currY;

      this.editor.addNode(node);
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
    this.editor = new WorkflowEditor(this.version, this.$refs.editor);
    this.area = AreaPlugin;

    // Disable some events if the editor is not editable.
    if (!this.editable) {
      const clickHandler = (e) => {
        e.preventDefault();
        e.stopPropagation();
      };

      for (const event of ['click', 'dblclick', 'contextmenu']) {
        this.$refs.editorContainer.addEventListener(event, clickHandler, {capture: true});
      }

      const dragHandler = (e) => {
        // Always allow moving the viewport.
        if (e.target !== this.$refs.editor) {
          e.preventDefault();
          e.stopPropagation();
        }
      };

      for (const event of ['pointerdown', 'pointerup']) {
        this.$refs.editorContainer.addEventListener(event, dragHandler, {capture: true});
      }
    }

    // Register all plugins.
    this.editor.use(AreaPlugin, {snap: {size: 16, dynamic: true}});
    this.editor.use(ConnectionPlugin);
    this.editor.use(VueRenderPlugin);
    this.editor.use(ContextMenuPlugin, {
      vueComponent: VueMenu,
      searchBar: true,
      delay: 0,
      items: this.menuItems,
      allocate: () => null,
    });

    // Register all builtin components.
    [
      ...annotationComponents,
      ...controlComponents,
      ...fileIoComponents,
      ...sourceComponents,
      ...userInputComponents,
      ...userOutputComponents,
      ...miscComponents,
    ].forEach((c) => this.editor.register(c));

    // Setup the context menu with the tool selection and all previously registered components.
    if (this.toolsEndpoint) {
      this.menuItems['Select tools...'] = () => $(this.$refs.toolDialog).modal();
    }

    for (const component of this.editor.components.values()) {
      // Skip components that do not specify a menu item.
      if (!component.menu) {
        continue;
      }

      if (!this.menuItems[component.menu]) {
        this.menuItems[component.menu] = {};
      }
      this.menuItems[component.menu][component.name] = () => this.addNode(component);
    }

    if (kadi.globals.environment === 'development') {
      this.menuItems.Debug = {
        /* eslint-disable no-console */
        'Dump Flow': () => console.info(this.editor.toFlow()),
        'Dump JSON': () => console.info(this.editor.toJSON()),
        /* eslint-enable no-console */
      };
    }

    this.editor.on('showcontextmenu', ({e}) => {
      const area = this.editor.view.area;
      const rect = area.el.getBoundingClientRect();

      // Store the mouse position at the time the context menu was opened.
      this.currX = (e.clientX - rect.left) / area.transform.k;
      this.currY = (e.clientY - rect.top) / area.transform.k;
    });

    // Handle unsaved changes on all relevant events.
    const events = [
      'nodecreated',
      'noderemoved',
      'nodetranslated',
      'connectioncreated',
      'connectionremoved',
      'controlchanged',
      'unsavedchanges',
    ];
    this.editor.on(events.join(' '), () => {
      if (!this.editor.silent) {
        this.unsavedChanges_ = true;
      }
    });

    // Finish initializion.
    this.resizeView();

    if (this.workflowUrl) {
      this.loadWorkflow(this.workflowUrl);
    }

    window.addEventListener('resize', this.resizeView);
    window.addEventListener('beforeunload', this.beforeUnload);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.resizeView);
    window.removeEventListener('beforeunload', this.beforeUnload);

    $(this.$refs.toolDialog).modal('dispose');
  },
};
</script>
