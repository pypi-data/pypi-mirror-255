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

import Rete from 'rete';

import {sockets, commonInputs, commonOutputs, BuiltinComponent} from 'core';
import PortControl from 'scripts/lib/workflows/controls/port-control';
import FormatControl from 'scripts/lib/workflows/controls/format-control';

/** Format string component that supports dynamic format inputs and a custom format string. */
class FormatStringComponent extends BuiltinComponent {
  constructor() {
    super(
      'FormatString',
      'misc',
      'Miscellaneous',
      [commonInputs.dep],
      [commonOutputs.dep, {key: 'formattedString', title: 'Formatted String', multi: true}],
    );
  }

  builder(node) {
    super.builder(node);

    node.meta.prevInputs = 0;

    const inputsControl = new PortControl('inputs', 'Inputs');
    const formatControl = new FormatControl('format', 'Format');

    node.addControl(inputsControl);
    node.addControl(formatControl);

    this.editor.on('controlchanged', (control) => {
      if (control !== inputsControl) {
        return;
      }

      const inputs = node.data.inputs;

      if (inputs > node.meta.prevInputs) {
        for (let i = node.meta.prevInputs; i < inputs; i++) {
          node.addInput(new Rete.Input(`input${i}`, `%${i}`, sockets.str));
        }
      } else {
        for (let i = inputs; i < node.meta.prevInputs; i++) {
          const input = node.inputs.get(`input${i}`);
          // Reverse loop since we are removing the connections as we loop.
          for (let j = input.connections.length - 1; j >= 0; j--) {
            this.editor.removeConnection(input.connections[j]);
          }
          node.removeInput(input);
        }
      }

      // Determine the default format string based on the number of inputs.
      const placeholders = [];
      for (let i = 0; i < inputs; i++) {
        placeholders.push(`%${i}`);
      }
      const formatString = `[${placeholders.join(', ')}]`;

      // Update the default format string of the control.
      formatControl.vueContext.updateDefaultFormat(formatString);

      // Update the current format string of the control if it is empty.
      if (!node.data.format) {
        formatControl.vueContext.updateValue(formatString);
      }

      node.vueContext.$forceUpdate();
      node.meta.prevInputs = inputs;
    });
  }

  fromFlow(flowNode) {
    const node = super.fromFlow(flowNode);

    node.data.inputs = flowNode.model.nInputs;
    node.data.format = flowNode.model.value;

    for (let i = 0; i < node.data.inputs; i++) {
      node.inputs.set(`input${i}`, {connections: []});
    }

    return node;
  }

  toFlow(node) {
    const flowNode = super.toFlow(node);

    flowNode.model.nInputs = node.data.inputs;
    flowNode.model.value = node.data.format;

    return flowNode;
  }
}

export default [new FormatStringComponent()];
