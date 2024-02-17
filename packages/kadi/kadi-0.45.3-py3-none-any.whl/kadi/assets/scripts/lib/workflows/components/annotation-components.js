/* Copyright 2022 Karlsruhe Institute of Technology
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License. */

import {BuiltinComponent} from 'core';
import VueNote from 'scripts/components/lib/workflows/view/Note.vue';

/** Class for the note component, which uses a separate Vue component for its node and has no inputs or outputs. */
class NoteComponent extends BuiltinComponent {
  constructor() {
    super('Note', 'note', 'Annotation');
    this.data.component = VueNote;
  }

  builder(node) {
    super.builder(node);

    if (!node.data.text) {
      node.data.text = '';
    }
  }

  fromFlow(flowNode) {
    const node = super.fromFlow(flowNode);
    node.data.text = flowNode.model.text;
    return node;
  }

  toFlow(node) {
    const flowNode = super.toFlow(node);
    flowNode.model.text = node.data.text;

    // Omit the execution profile.
    delete flowNode.model.executionProfile;

    return flowNode;
  }
}

export default [new NoteComponent()];
