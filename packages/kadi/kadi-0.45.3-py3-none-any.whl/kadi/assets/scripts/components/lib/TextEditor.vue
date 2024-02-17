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
    <div class="bg-white" ref="container">
      <div class="card toolbar" ref="toolbar">
        <div class="card-body px-1 py-0">
          <button type="button"
                  class="btn btn-link text-primary my-1"
                  :title="$t('Toggle fullscreen')"
                  @click="toggleFullscreen">
            <i class="fa-solid fa-expand"></i>
          </button>
          <button type="button"
                  class="btn btn-sm btn-link text-primary border m-1"
                  :title="$t('Newlines')"
                  @click="changeNewline">
            <strong v-if="newline === 'unix'">Unix/Mac (LF)</strong>
            <strong v-else>Windows (CR LF)</strong>
          </button>
          <button type="button"
                  class="btn btn-sm btn-link text-primary border m-1"
                  :title="$t('Indentation')"
                  @click="changeIndentation">
            <strong v-if="indentation === 'space'">{{ $t('Spaces') }}</strong>
            <strong v-else>{{ $t('Tabs') }}</strong>
          </button>
        </div>
      </div>
      <div class="editor" ref="editor"></div>
      <div class="card bg-light footer">
        <small class="text-muted">{{ $t('Note that text files are always handled using UTF-8 encoding.') }}</small>
      </div>
    </div>
    <slot :document="editor ? editor.state.doc : null" :newline="newline"></slot>
  </div>
</template>

<style scoped>
.editor {
  border: 1px solid #ced4da;
  font-size: 10pt;
  height: 55vh;
}

.footer {
  border-color: #ced4da;
  border-top-left-radius: 0px;
  border-top-right-radius: 0px;
  margin-top: -1px;
  padding: 2px 10px 2px 10px;
}

.toolbar {
  border-bottom-left-radius: 0px;
  border-bottom-right-radius: 0px;
  border-color: #ced4da;
  margin-bottom: -1px;
}
</style>

<script>
import {defaultKeymap, history, historyKeymap, indentLess, indentMore} from '@codemirror/commands';
import {indentUnit} from '@codemirror/language';
import {Compartment, EditorState} from '@codemirror/state';
import {
  EditorView,
  gutter,
  highlightActiveLine,
  highlightActiveLineGutter,
  highlightWhitespace,
  keymap,
  lineNumbers,
} from '@codemirror/view';
import {detectNewlineGraceful} from 'detect-newline';
import detectIndent from 'detect-indent';

export default {
  data() {
    return {
      editor: null,
      indentCompartment: null,
      newline: 'unix',
      indentation: 'space',
      unsavedChanges_: false,
    };
  },
  props: {
    textUrl: {
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
  watch: {
    textUrl() {
      this.loadTextFile(this.textUrl);
    },
    unsavedChanges() {
      this.unsavedChanges_ = this.unsavedChanges;
    },
    unsavedChanges_() {
      this.$emit('unsaved-changes', this.unsavedChanges_);
    },
    isRendered() {
      this.resizeView();
    },
  },
  methods: {
    toggleFullscreen() {
      kadi.utils.toggleFullscreen(this.$refs.container);
    },
    resizeView() {
      if (!this.isRendered) {
        return;
      }

      const toolbar = this.$refs.toolbar;
      const container = this.$refs.editor;

      if (kadi.utils.isFullscreen()) {
        const toolbarHeight = Math.round(toolbar.getBoundingClientRect().height);

        this.$refs.editor.style.height = `calc(100vh - ${toolbarHeight - 1}px)`;
        toolbar.style.borderTopLeftRadius = toolbar.style.borderTopRightRadius = '0';
      } else {
        const containerWidth = Math.round(container.getBoundingClientRect().width);
        const containerHeight = Math.round(window.innerHeight / window.innerWidth * containerWidth);

        this.$refs.editor.style.height = `${containerHeight}px`;
        toolbar.style.borderTopLeftRadius = toolbar.style.borderTopRightRadius = '0.25rem';
      }
    },
    createEditorState(text = '') {
      const tabBinding = {
        key: 'Tab',
        run: (command) => {
          const selection = command.state.selection.ranges[0];

          // Insert spaces/tabs when no text is selected, indent otherwise.
          if (selection.to === selection.from) {
            const indentation = this.indentation === 'space' ? '  ' : '\t';
            command.dispatch(command.state.replaceSelection(indentation));
          } else {
            indentMore(command);
          }

          return true;
        },
        shift(command) {
          indentLess(command);
          return true;
        },
      };

      const onUpdate = (update) => {
        if (update.docChanged) {
          this.unsavedChanges_ = true;
        }
      };

      // Using a Compartment for the indentation is required to reconfigure it on the fly.
      this.indentCompartment = new Compartment();

      return EditorState.create({
        doc: text,
        extensions: [
          this.indentCompartment.of(indentUnit.of(this.getIndentation())),
          EditorView.updateListener.of(onUpdate),
          gutter(),
          highlightActiveLine(),
          highlightActiveLineGutter(),
          highlightWhitespace(),
          history(),
          keymap.of([tabBinding, ...defaultKeymap, ...historyKeymap]),
          lineNumbers(),
        ],
      });
    },
    getIndentation() {
      return this.indentation === 'space' ? '  ' : '\t';
    },
    changeIndentation() {
      if (this.indentation === 'space') {
        this.indentation = 'tab';
      } else {
        this.indentation = 'space';
      }

      this.unsavedChanges_ = true;

      // Reconfigure the actual indentation the editor uses.
      this.editor.dispatch({
        effects: this.indentCompartment.reconfigure(indentUnit.of(this.getIndentation())),
      });
    },
    changeNewline() {
      if (this.newline === 'unix') {
        this.newline = 'windows';
      } else {
        this.newline = 'unix';
      }

      this.unsavedChanges_ = true;
    },
    async loadTextFile(url) {
      try {
        const config = {responseType: 'text', transformResponse: [(data) => data]};
        const response = await axios.get(url, config);

        this.indentation = detectIndent(response.data).type || 'space';

        if (detectNewlineGraceful(response.data) === '\n') {
          this.newline = 'unix';
        } else {
          this.newline = 'windows';
        }

        // Replace all Windows-style newlines, as we always use Unix-style newlines internally.
        const text = response.data.replaceAll('\r\n', '\n');
        // Set a new editor state to reset the history.
        this.editor.setState(this.createEditorState(text));
        this.unsavedChanges_ = false;
      } catch (error) {
        kadi.base.flashDanger($t('Error loading text file.'), {request: error.request});
      }
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
    this.editor = new EditorView({
      state: this.createEditorState(),
      parent: this.$refs.editor,
    });

    this.resizeView();

    if (this.textUrl) {
      this.loadTextFile(this.textUrl);
    }

    window.addEventListener('resize', this.resizeView);
    window.addEventListener('beforeunload', this.beforeUnload);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.resizeView);
    window.removeEventListener('beforeunload', this.beforeUnload);

    this.editor.destroy();
  },
};
</script>
