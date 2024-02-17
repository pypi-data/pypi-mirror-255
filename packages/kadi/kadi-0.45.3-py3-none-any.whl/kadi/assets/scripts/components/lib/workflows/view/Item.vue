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

<style lang="scss" scoped>
@import 'styles/workflows/workflow-editor.scss';

.item {
  width: $context-menu-width;

  &.hasSubitems:after {
    content: '>';
    opacity: 0.6;
    position: absolute;
    right: 5px;
    top: 5px;
  }

  .subitems {
    border: 1px solid $context-menu-accent-color;
    left: 100%;
    max-height: 155px;
    overflow-x: hidden;
    overflow-y: auto;
    position: absolute;
    top: 0;

    .item {
      border: 0;
      border-radius: 0;
    }
  }
}
</style>

<script>
import {Item} from 'rete-context-menu-plugin';

export default {
  extends: Item,
  name: 'Item',
  methods: {
    onClick(e) {
      e.stopPropagation();

      if (this.item.onClick) {
        this.item.onClick(this.args);
      }
      if (!this.item.keepOpen) {
        this.$root.$emit('hide');
      }
    },
  },
};
</script>
