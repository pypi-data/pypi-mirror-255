/* Copyright 2023 Karlsruhe Institute of Technology
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

/** Mixin to add common functionality to workflow control Vue components. */
export default {
  props: {
    ikey: String,
    getData: Function,
    putData: Function,
  },
  data() {
    return {
      value: null,
    };
  },
  watch: {
    value() {
      this.convertValue();
      this.putData(this.ikey, this.value);

      this.$emit('change-value');
    },
  },
  methods: {
    // Convenience method for updating a value from the outside.
    updateValue(value) {
      this.value = value;
    },
    convertValue() {
      // Can be overridden for custom conversion and validation logic.
    },
  },
  /* eslint-disable no-undefined */
  mounted() {
    this.value = this.getData(this.ikey);

    if (this.value === undefined) {
      if (this.defaultValue !== undefined) {
        this.value = this.defaultValue;
      } else {
        this.value = null;
      }
    }

    this.putData(this.ikey, this.value);
  },
  /* eslint-enable no-undefined */
};
