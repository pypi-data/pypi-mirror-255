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
  <div class="modal" tabindex="-1" ref="modalDialog" @change.stop>
    <div class="modal-dialog modal-dialog-centered modal-xl">
      <div class="modal-content">
        <div class="modal-header">
          <strong class="modal-title">{{ $t('Find term') }}</strong>
          <button type="button" class="close" data-dismiss="modal">
            <i class="fa-solid fa-xmark fa-xs"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="input-group input-group-sm mb-3">
            <input id="query-input" class="form-control" :placeholder="$t('Search for terms')" v-model="query">
            <clear-button input-id="query-input" :input="query" @clear-input="query = ''"></clear-button>
          </div>
          <dynamic-pagination :endpoint="endpoint"
                              :placeholder="$t('No terms.')"
                              :per-page="5"
                              :args="{query}"
                              v-if="initialized">
            <template #default="props">
              <div v-if="props.total > 0">
                <ul class="list-group">
                  <li class="list-group-item py-2" v-for="item in props.items" :key="item.id">
                    <div class="row align-items-center">
                      <div class="col-lg-10 mb-2 mb-lg-0">
                        <div v-html="item.body"></div>
                      </div>
                      <div class="col-lg-2 d-lg-flex justify-content-end">
                        <button type="button"
                                class="btn btn-sm btn-light"
                                data-dismiss="modal"
                                @click="addTerm(item.term)">
                          {{ $t('Select term') }}
                        </button>
                      </div>
                    </div>
                  </li>
                </ul>
                <small class="text-muted">
                  <i class="fa-solid fa-circle-info"></i>
                  {{ $t('Note that these results are provided by an external terminology service.') }}
                </small>
              </div>
            </template>
          </dynamic-pagination>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      query: '',
      initialized: false,
    };
  },
  props: {
    endpoint: String,
  },
  methods: {
    showDialog(initialQuery = '') {
      this.query = initialQuery;
      this.initialized = true;
      $(this.$refs.modalDialog).modal();
    },
    addTerm(term) {
      this.$emit('select-term', term);
    },
  },
  beforeDestroy() {
    $(this.$refs.modalDialog).modal('dispose');
  },
};
</script>
