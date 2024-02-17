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
  <div>
    <div class="row align-items-center" :class="{'mb-2': showToolbar}" v-if="!nestedType">
      <div class="col-lg-6 mb-2 mb-lg-0">
        <slot></slot>
      </div>
      <div class="col-lg-6 d-lg-flex justify-content-end" v-if="showToolbar">
        <div class="btn-group btn-group-sm">
          <button type="button"
                  class="btn btn-light"
                  :title="$t('Collapse all')"
                  @click="collapseExtras(true)"
                  v-if="hasNestedType">
            <i class="fa-regular fa-lg fa-square-minus"></i>
          </button>
          <button type="button"
                  class="btn btn-light"
                  :title="$t('Expand all')"
                  @click="collapseExtras(false)"
                  v-if="hasNestedType">
            <i class="fa-regular fa-lg fa-square-plus"></i>
          </button>
          <button type="button"
                  class="btn btn-light"
                  @click="hideNullValues_ = !hideNullValues_"
                  v-if="hasNullValues">
            <span v-if="hideNullValues_">
              <i class="fa-solid fa-eye"></i> {{ $t('Show null values') }}
            </span>
            <span v-else>
              <i class="fa-solid fa-eye-slash"></i> {{ $t('Hide null values') }}
            </span>
          </button>
        </div>
      </div>
    </div>
    <ul class="list-group" :class="{'mb-2': depth > 0}">
      <li class="list-group-item extra py-1 pl-3 pr-0"
          :class="{'odd': depth % 2 == 1, 'nested': depth > 0}"
          v-for="(extra, index) in filteredExtras"
          :key="extra.id">
        <div class="row align-items-center"
             :class="{'mb-1': kadi.utils.isNestedType(extra.type) && extra.value.length > 0 && !extra.isCollapsed}">
          <!-- Key. -->
          <div class="col-md-4">
            <span v-if="!kadi.utils.isNestedType(extra.type)">{{ extra.key || `(${index + 1})` }}</span>
            <collapse-item show-icon-class=""
                           hide-icon-class=""
                           :id="extra.id"
                           :is-collapsed="extra.isCollapsed"
                           @collapse="extra.isCollapsed = $event"
                           v-if="kadi.utils.isNestedType(extra.type)">
              <strong>{{ extra.key || `(${index + 1})` }}</strong>
            </collapse-item>
          </div>
          <!-- Value and unit. -->
          <div class="col-md-5">
            <div v-if="!kadi.utils.isNestedType(extra.type)">
              <span v-if="extra.value === null">
                <em>null</em>
              </span>
              <span v-else>
                <span v-if="extra.type !== 'date'">{{ getExtraValue(extra) }}</span>
                <local-timestamp :timestamp="extra.value" v-else></local-timestamp>
              </span>
              <span class="text-muted">{{ extra.unit }}</span>
            </div>
            <collapse-item show-icon-class=""
                           hide-icon-class=""
                           :id="extra.id"
                           :is-collapsed="extra.isCollapsed"
                           @collapse="extra.isCollapsed = $event"
                           v-if="kadi.utils.isNestedType(extra.type) && extra.isCollapsed && extra.value.length > 0">
              <strong>[...]</strong>
            </collapse-item>
          </div>
          <!-- Type. -->
          <div class="col-md-2 d-md-flex justify-content-end">
            <small class="text-muted mr-3">{{ kadi.utils.capitalize(kadi.utils.prettyTypeName(extra.type)) }}</small>
          </div>
          <!-- Edit link and additional information toggle. -->
          <div class="col-md-1 d-md-flex justify-content-end">
            <button type="button"
                    class="float-md-right mr-3 mr-md-0"
                    :title="$t('Toggle additional information')"
                    :class="toggleClasses"
                    @click="extra.showDetails = !extra.showDetails"
                    v-if="extra.description || extra.term || extra.validation">
              <i class="fa-solid fa-angle-up" v-if="extra.showDetails"></i>
              <i class="fa-solid fa-angle-down" v-else></i>
              <span class="d-md-none">{{ $t('Toggle additional information') }}</span>
              <br>
            </button>
            <a :title="$t('Edit extra')"
               :class="toggleClasses"
               :href="getEditLink(extra, index)"
               v-if="editEndpoint">
              <i class="fa-solid fa-pencil"></i>
              <span class="d-md-none">{{ $t('Edit extra') }}</span>
            </a>
          </div>
        </div>
        <div v-if="extra.showDetails">
          <div class="card card-body bg-light py-1 px-2 my-1 mr-3">
            <div v-if="extra.description">
              <div class="row my-2 my-sm-0">
                <small class="col-sm-4">
                  <em>{{ $t('Description') }}</em>
                </small>
                <small class="col-sm-8">
                  <span class="ws-pre-wrap">{{ extra.description }}</span>
                </small>
              </div>
            </div>
            <div v-if="extra.term">
              <hr class="my-1" v-if="extra.description">
              <div class="row my-2 my-sm-0">
                <small class="col-sm-4">
                  <em>{{ $t('Term IRI') }}</em>
                </small>
                <small class="col-sm-8">
                  <a class="text-primary" target="_blank" rel="noopener noreferrer" :href="extra.term">
                    <i class="fa-solid fa-arrow-up-right-from-square mr-1"></i>
                    <strong>{{ extra.term }}</strong>
                  </a>
                </small>
              </div>
            </div>
            <div v-if="extra.validation">
              <hr class="my-1" v-if="extra.description || extra.term">
              <div class="row my-2 my-sm-0" v-for="(value, key) in extra.validation" :key="key">
                <small class="col-sm-4">
                  <em>{{ $t('Validation') }} ({{ validationKeys[key] || key }})</em>
                </small>
                <small class="col-sm-8">{{ getValidationValue(extra, key, value) }}</small>
              </div>
            </div>
          </div>
        </div>
        <div v-if="kadi.utils.isNestedType(extra.type) && extra.value.length > 0">
          <div :id="extra.id">
            <extras-viewer :extras="extra.value"
                           :edit-endpoint="editEndpoint"
                           :nested-type="extra.type"
                           :nested-keys="[...nestedKeys, extra.key || index]"
                           :hide-null-values="hideNullValues_"
                           :depth="depth + 1">
            </extras-viewer>
          </div>
        </div>
      </li>
    </ul>
  </div>
</template>

<style lang="scss" scoped>
.extra {
  margin-right: -1px;

  &.nested {
    border-bottom-right-radius: 0;
    border-top-right-radius: 0;
  }

  &.odd {
    background-color: #f2f2f2;
  }
}
</style>

<script>
export default {
  data() {
    return {
      extras_: this.extras,
      hasNullValues: false,
      hideNullValues_: this.hideNullValues,
      validationKeys: {
        required: $t('Required'),
        options: $t('Options'),
        range: $t('Range'),
      },
    };
  },
  props: {
    extras: Array,
    editEndpoint: {
      type: String,
      default: null,
    },
    editQueryParam: {
      type: String,
      default: 'key',
    },
    showToolbar: {
      type: Boolean,
      default: true,
    },
    // Can also be used to detect whether we are in a nested context at all.
    nestedType: {
      type: String,
      default: null,
    },
    nestedKeys: {
      type: Array,
      default: () => [],
    },
    hideNullValues: {
      type: Boolean,
      default: false,
    },
    depth: {
      type: Number,
      default: 0,
    },
  },
  computed: {
    toggleClasses() {
      return 'btn btn-sm text-primary py-0 px-0 px-md-2 mx-1';
    },
    hasNestedType() {
      for (const extra of this.extras_) {
        if (kadi.utils.isNestedType(extra.type)) {
          return true;
        }
      }
      return false;
    },
    filteredExtras() {
      const extras = [];

      for (const extra of this.extras_) {
        if (!extra.isNull || !this.hideNullValues_) {
          extras.push(extra);
        }
      }

      return extras;
    },
  },
  watch: {
    hideNullValues() {
      this.hideNullValues_ = this.hideNullValues;
    },
  },
  methods: {
    visitExtras(extras, callback) {
      extras.forEach((extra) => {
        callback(extra);

        if (kadi.utils.isNestedType(extra.type)) {
          this.visitExtras(extra.value, callback);
        }
      });
    },
    collapseExtras(collapse) {
      this.visitExtras(this.extras_, (extra) => extra.isCollapsed = collapse);
    },
    getExtraValue(extra) {
      if (['int', 'float'].includes(extra.type)) {
        return kadi.utils.toExponentional(extra.value);
      }

      return extra.value;
    },
    getValidationValue(extra, key, value) {
      if (key === 'required') {
        return $t('Yes');
      }

      if (key === 'options') {
        const options = [];

        for (const option of value) {
          if (extra.type === 'str') {
            options.push(`"${option}"`);
          } else {
            options.push(kadi.utils.toExponentional(option));
          }
        }

        return options.join(', ');
      }

      if (key === 'range') {
        const ranges = [];

        if (value.min !== null) {
          ranges.push(`\u2265 ${kadi.utils.toExponentional(value.min)}`);
        }
        if (value.max !== null) {
          ranges.push(`\u2264 ${kadi.utils.toExponentional(value.max)}`);
        }

        return ranges.join(', ');
      }

      return value;
    },
    getEditLink(extra, index) {
      const url = new URL(this.editEndpoint);
      const searchParams = new URLSearchParams(url.search);

      for (const key of this.nestedKeys) {
        searchParams.append(this.editQueryParam, key);
      }
      searchParams.append(this.editQueryParam, extra.key || index);

      url.search = searchParams;
      return url.toString();
    },
    isNull(extra) {
      if (kadi.utils.isNestedType(extra.type)) {
        for (const _extra of extra.value) {
          if (!this.isNull(_extra)) {
            return false;
          }
        }
        return true;
      }

      return extra.value === null;
    },
  },
  created() {
    if (!this.nestedType) {
      this.visitExtras(this.extras_, (extra) => {
        extra.id = kadi.utils.randomAlnum();
        extra.isNull = this.isNull(extra);

        if (extra.isNull && !this.hasNullValues) {
          this.hasNullValues = true;
        }

        this.$set(extra, 'showDetails', false);
        this.$set(extra, 'isCollapsed', false);
      });
    }
  },
};
</script>
