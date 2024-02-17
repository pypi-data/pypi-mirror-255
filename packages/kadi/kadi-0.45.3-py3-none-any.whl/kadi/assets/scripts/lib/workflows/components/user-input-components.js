/* Copyright 2021 Karlsruhe Institute of Technology
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

const type = 'user-input';
const menu = 'User Input';

const userInputText = new BuiltinComponent(
  'UserInputText',
  type,
  menu,
  [commonInputs.dep, {key: 'prompt'}, {key: 'default'}, {key: 'multiline', socket: sockets.bool}],
  [commonOutputs.dep, {key: 'value', multi: true}],
);

const userInputInteger = new BuiltinComponent(
  'UserInputInteger',
  type,
  menu,
  [commonInputs.dep, {key: 'prompt'}, {key: 'default', socket: sockets.int}],
  [commonOutputs.dep, {key: 'value', multi: true, socket: sockets.int}],
);

const userInputFloat = new BuiltinComponent(
  'UserInputFloat',
  type,
  menu,
  [commonInputs.dep, {key: 'prompt'}, {key: 'default', socket: sockets.float}],
  [commonOutputs.dep, {key: 'value', multi: true, socket: sockets.float}],
);

const userInputBool = new BuiltinComponent(
  'UserInputBool',
  type,
  menu,
  [commonInputs.dep, {key: 'prompt'}, {key: 'default', socket: sockets.bool}],
  [commonOutputs.dep, {key: 'value', multi: true, socket: sockets.bool}],
);

const userInputFile = new BuiltinComponent(
  'UserInputFile',
  type,
  menu,
  [commonInputs.dep, {key: 'prompt'}, {key: 'default'}],
  [commonOutputs.dep, {key: 'value', multi: true}],
);

const userInputSelect = new BuiltinComponent(
  'UserInputSelect',
  type,
  menu,
  [commonInputs.dep, {key: 'prompt'}, {key: 'values'}, {key: 'default'}, {key: 'delimiter', title: 'Delimiter [,]'}],
  [commonOutputs.dep, {key: 'value', multi: true}],
);

const userInputSelectBoundingBox = new BuiltinComponent(
  'UserInputSelectBoundingBox',
  type,
  menu,
  [commonInputs.dep, {key: 'prompt'}, {key: 'imagePath', title: 'Image Path'}],
  [
    commonOutputs.dep,
    {key: 'x', socket: sockets.int, multi: true},
    {key: 'y', socket: sockets.int, multi: true},
    {key: 'width', socket: sockets.int, multi: true},
    {key: 'height', socket: sockets.int, multi: true},
  ],
);

const userInputPeriodicTable = new BuiltinComponent(
  'UserInputPeriodicTable',
  type,
  menu,
  [commonInputs.dep, {key: 'prompt'}, {key: 'default'}],
  [commonOutputs.dep, {key: 'selectedElements', title: 'Selected Elements', multi: true}],
);

const userInputForm = new BuiltinComponent(
  'UserInputForm',
  type,
  menu,
  [commonInputs.dep, {key: 'jsonFile', title: 'JSON File'}],
  [commonOutputs.dep, {key: 'jsonString', title: 'JSON String', multi: true}],
);

// Deprecated in favor of 'UserInputSelectBoundingBox'.
const userInputCropImages = new BuiltinComponent(
  'UserInputCropImages',
  type,
  null,
  [commonInputs.dep, {key: 'prompt'}, {key: 'imagePath', title: 'Image Path'}],
  [commonOutputs.dep, {key: 'cropInfo', title: 'Crop Info', multi: true}],
  {validationState: 'warning', validationMessage: 'Deprecated in favor of "UserInputSelectBoundingBox".'},
);

/** Choose component that supports dynamic option inputs. */
class ChooseComponent extends BuiltinComponent {
  constructor() {
    super(
      'UserInputChoose',
      type,
      menu,
      [commonInputs.dep, {key: 'prompt'}, {key: 'default', socket: sockets.int}],
      [commonOutputs.dep, {key: 'selected', socket: sockets.int, multi: true}, {key: 'value', multi: true}],
    );
  }

  builder(node) {
    super.builder(node);

    node.meta.prevOptions = 0;

    const optionsControl = new PortControl('options', 'Options');
    node.addControl(optionsControl);

    this.editor.on('controlchanged', (control) => {
      if (control !== optionsControl) {
        return;
      }

      const options = node.data.options;

      if (options > node.meta.prevOptions) {
        for (let i = node.meta.prevOptions; i < options; i++) {
          node.addInput(new Rete.Input(`option${i}`, `Option ${i + 1}`, sockets.str));
        }
      } else {
        for (let i = options; i < node.meta.prevOptions; i++) {
          const input = node.inputs.get(`option${i}`);
          // Reverse loop since we are removing the connections as we loop.
          for (let j = input.connections.length - 1; j >= 0; j--) {
            this.editor.removeConnection(input.connections[j]);
          }
          node.removeInput(input);
        }
      }

      node.vueContext.$forceUpdate();
      node.meta.prevOptions = options;
    });
  }

  fromFlow(flowNode) {
    const node = super.fromFlow(flowNode);
    node.data.options = flowNode.model.nOptions;

    for (let i = 0; i < node.data.options; i++) {
      node.inputs.set(`option${i}`, {connections: []});
    }

    return node;
  }

  toFlow(node) {
    const flowNode = super.toFlow(node);
    flowNode.model.nOptions = node.data.options;
    return flowNode;
  }
}

export default [
  userInputText,
  userInputInteger,
  userInputFloat,
  userInputBool,
  userInputFile,
  userInputSelect,
  userInputSelectBoundingBox,
  userInputPeriodicTable,
  userInputForm,
  userInputCropImages,
  new ChooseComponent(),
];
