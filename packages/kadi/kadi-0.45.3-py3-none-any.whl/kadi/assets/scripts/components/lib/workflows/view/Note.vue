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
  <div class="node" :class="selected()" :title="node.name">
    <textarea class="content form-control"
              spellcheck="false"
              v-model="text"
              @pointerdown.stop
              ref="textarea">
    </textarea>
  </div>
</template>

<style lang="scss" scoped>
$bg-note: #f5ec9a;

.node {
  background: rgba($bg-note, 0.85);
  border: 2px solid $bg-note;
  cursor: pointer;
  padding-top: 30px;
  width: 350px;

  &:hover, &.selected {
    background: rgba(darken($bg-note, 10%), 0.85);
  }

  .content {
    background: rgba(lighten($bg-note, 15%), 0.85);
    border: 0;
    border-radius: 0;
    box-shadow: none;
    color: black;
    height: 35px;
    min-height: 35px;
    overflow: hidden;
    padding: 5px;
    resize: none;
  }
}
</style>

<script>
import VueRenderPlugin from 'rete-vue-render-plugin';

export default {
  mixins: [VueRenderPlugin.mixin],
  data() {
    return {
      text: this.node.data.text,
    };
  },
  watch: {
    text() {
      this.node.data.text = this.text;
      this.editor.trigger('unsavedchanges');

      // Wait until the new text is actually rendered.
      this.$nextTick(() => {
        const textarea = this.$refs.textarea;
        // Set the height to 0 first to determine the ideal height based on the scroll height.
        textarea.style.height = '0';
        textarea.style.height = `${textarea.scrollHeight}px`;
      });
    },
  },
};
</script>
