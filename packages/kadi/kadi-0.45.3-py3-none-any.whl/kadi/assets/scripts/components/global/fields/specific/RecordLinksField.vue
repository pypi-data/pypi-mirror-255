<!-- Copyright 2023 Karlsruhe Institute of Technology
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
    <div class="form-group">
      <div class="row align-items-end">
        <div class="col-sm-6">
          <label class="form-control-label">{{ field.label }}</label>
        </div>
        <div class="col-sm-6 d-sm-flex justify-content-end mb-2">
          <button type="button"
                  class="btn btn-sm btn-light"
                  :class="{'toggle-active': showPreview}"
                  @click="showPreview = !showPreview">
            <i class="fa-solid fa-eye"></i> {{ $t('Link preview') }}
          </button>
        </div>
      </div>
      <div class="card">
        <div class="card-body p-2">
          <div v-for="(link, index) in links" :key="link.id">
            <div class="card bg-light mb-1" v-if="showPreview">
              <div class="card-body py-1 px-2">
                <div class="row align-items-center">
                  <div class="col-md-4">
                    <small>
                      <span v-if="currentRecordIdentifier">
                        @{{ kadi.utils.truncate(currentRecordIdentifier, 25) }}
                      </span>
                      <em v-else>{{ $t('New record') }}</em>
                    </small>
                  </div>
                  <div class="col-md-4 d-md-flex justify-content-center">
                    <span>
                      <i class="fa-solid fa-arrow-left-long fa-lg mr-2" v-if="link.direction === 'in'"></i>
                      <small>{{ kadi.utils.truncate(link.name || '', 20) }}</small>
                      <i class="fa-solid fa-arrow-right-long fa-lg ml-2" v-if="link.direction === 'out'"></i>
                    </span>
                  </div>
                  <div class="col-md-4 d-md-flex justify-content-end">
                    <small>
                      <span v-if="link.record">{{ kadi.utils.truncate(link.record[1], 25) }}</span>
                      <em v-else>{{ $t('Linked record') }}</em>
                    </small>
                  </div>
                </div>
              </div>
            </div>
            <div class="form-row" :class="{'mb-3' : index < links.length - 1 && !link.editTerm}">
              <div class="col-md-3 mb-1 mb-md-0">
                <div class="input-group input-group-sm">
                  <div class="input-group-prepend">
                    <span class="input-group-text">{{ $t('Direction') }}</span>
                  </div>
                  <select class="custom-select" v-model="link.direction">
                    <option v-for="direction in directions" :key="direction[0]" :value="direction[0]">
                      {{ direction[1] }}
                    </option>
                  </select>
                </div>
              </div>
              <div class="col-md-4 mb-1 mb-md-0">
                <div class="input-group input-group-sm">
                  <div class="input-group-prepend">
                    <span class="input-group-text">{{ $t('Record') }}</span>
                  </div>
                  <dynamic-selection container-classes="select2-single-sm"
                                     :class="{'has-error': getErrors(index, 'record').length > 0}"
                                     :endpoint="recordsEndpoint"
                                     :initial-values="getInitialRecord(link)"
                                     :placeholder="$t('Search for records')"
                                     @select="selectRecord(link, $event)"
                                     @unselect="link.record = null">
                  </dynamic-selection>
                </div>
                <div class="invalid-feedback" v-for="error in getErrors(index, 'record')" :key="error">{{ error }}</div>
              </div>
              <div class="col-md-3 mb-1 mb-md-0">
                <div class="input-group input-group-sm">
                  <div class="input-group-prepend">
                    <span class="input-group-text">{{ $t('Name') }}</span>
                  </div>
                  <dynamic-selection container-classes="select2-single-sm"
                                     :class="{'has-error': getErrors(index, 'name').length > 0}"
                                     :endpoint="namesEndpoint"
                                     :initial-values="getInitialName(link)"
                                     :placeholder="$t('Enter or search for a name')"
                                     :max-input-length="field.validation.max.name"
                                     :tags="true"
                                     @select="selectName(link, $event)"
                                     @unselect="link.name = null">
                  </dynamic-selection>
                  <div class="input-group-append">
                    <button type="button"
                            class="input-group-text btn btn-light"
                            :class="{'toggle-active': link.editTerm}"
                            :title="$t('Toggle term IRI')"
                            @click="link.editTerm = !link.editTerm">
                      <i class="fa-solid fa-link"></i>
                    </button>
                  </div>
                </div>
                <div class="invalid-feedback" v-for="error in getErrors(index, 'name')" :key="error">{{ error }}</div>
              </div>
              <div class="col-md-2">
                <div class="btn-group btn-group-sm w-100">
                  <button type="button" class="btn btn-light" :title="$t('Add link')" @click="addLink(null, index)">
                    <i class="fa-solid fa-plus"></i>
                  </button>
                  <button type="button"
                          class="btn btn-light"
                          :title="$t('Remove link')"
                          @click="removeLink(index)"
                          v-if="links.length > 1">
                    <i class="fa-solid fa-xmark"></i>
                  </button>
                </div>
              </div>
            </div>
            <div class="mt-1" :class="{'mb-3' : index < links.length - 1}" v-show="link.editTerm">
              <div class="input-group input-group-sm">
                <div class="input-group-prepend">
                  <span class="input-group-text">{{ $t('Term IRI') }}</span>
                </div>
                <input class="form-control"
                       :class="{'has-error': getErrors(index, 'term').length > 0}"
                       v-model.trim="link.term">
                <div class="input-group-append" v-if="termsEndpoint">
                  <button type="button" class="btn btn-light" @click="showTermSearch(link)">
                    <i class="fa-solid fa-search"></i> {{ $t('Find term') }}
                  </button>
                </div>
              </div>
              <div class="invalid-feedback" v-for="error in getErrors(index, 'term')" :key="error">{{ error }}</div>
              <small class="form-text text-muted" v-if="getErrors(index, 'term').length === 0">
                {{ $t('An IRI specifying an existing term that the link should represent.') }}
              </small>
            </div>
          </div>
        </div>
      </div>
      <small class="form-text text-muted">{{ field.description }}</small>
      <input type="hidden" :name="field.name" :value="serializedLinks">
    </div>
    <term-search :endpoint="termsEndpoint" @select-term="selectTerm" ref="termSearch" v-if="termsEndpoint">
    </term-search>
  </div>
</template>

<script>
export default {
  data() {
    return {
      directions: [['out', $t('Outgoing')], ['in', $t('Incoming')]],
      links: [],
      showPreview: false,
      currentLink: null,
    };
  },
  props: {
    field: Object,
    recordsEndpoint: String,
    namesEndpoint: String,
    termsEndpoint: {
      type: String,
      default: null,
    },
    currentRecordIdentifier: {
      type: String,
      default: null,
    },
  },
  computed: {
    serializedLinks() {
      const links = [];

      for (const link of this.links) {
        if (link.record !== null || link.name !== null) {
          links.push({
            record: link.record !== null ? link.record[0] : null,
            name: link.name,
            term: link.term || null,
            direction: link.direction,
          });
        }
      }

      return JSON.stringify(links);
    },
  },
  methods: {
    getInitialRecord(link) {
      return link.record === null ? [] : [link.record];
    },
    getInitialName(link) {
      return link.name === null ? [] : [[link.name, link.name]];
    },
    getErrors(index, name) {
      const errors = this.field.errors[index];

      if (errors) {
        return errors[name] || [];
      }

      return [];
    },
    selectRecord(link, record) {
      link.record = [record.id, record.text];
      this.selectValue();
    },
    selectName(link, name) {
      link.name = name.id;
      this.selectValue();
    },
    selectValue() {
      // Automatically add a new link input if the last one is not empty.
      const lastLink = this.links[this.links.length - 1];

      if (lastLink.record !== null && lastLink.name !== null) {
        this.addLink();
      }

      // Dispatch a custom 'change' event as well.
      this.$el.dispatchEvent(new Event('change', {bubbles: true}));
    },
    addLink(link = null, index = null) {
      const newLink = {
        id: kadi.utils.randomAlnum(),
        record: null,
        name: null,
        term: '',
        direction: this.directions[0][0],
        editTerm: false,
      };

      if (link !== null) {
        // Copy a given link.
        Object.assign(newLink, link);
      } else {
        // Try to copy the direction of the previous link.
        const prevIndex = index === null ? this.links.length - 1 : index;
        const prevLink = this.links[prevIndex];

        if (prevLink) {
          newLink.direction = prevLink.direction;
        }
      }

      kadi.utils.addToArray(this.links, newLink, index);
    },
    removeLink(index) {
      this.links.splice(index, 1);
    },
    showTermSearch(link) {
      this.currentLink = link;
      this.$refs.termSearch.showDialog(link.name || '');
    },
    selectTerm(term) {
      this.currentLink.term = term;
      // Dispatch a custom 'change' event as well.
      this.$el.dispatchEvent(new Event('change', {bubbles: true}));
    },
  },
  mounted() {
    for (const link of this.field.data) {
      this.addLink(link);
    }

    if (this.links.length === 0) {
      this.addLink();
    } else {
      for (const [index, link] of this.links.entries()) {
        if (this.getErrors(index, 'term').length > 0) {
          link.editTerm = true;
        }
      }
    }
  },
};
</script>
