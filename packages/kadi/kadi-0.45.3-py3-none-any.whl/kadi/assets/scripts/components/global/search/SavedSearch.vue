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
    <confirm-dialog ref="dialog"></confirm-dialog>
    <div class="card bg-light">
      <div class="card-header py-2" v-if="currentSearch">
        <div class="form-row align-items-center" v-if="state !== 'edit'">
          <div class="col-8">
            <tooltip-item class="mr-1" :title="$t('Unsaved changes')" v-if="unsavedChanges">
              <i class="fa-solid fa-triangle-exclamation"></i>
            </tooltip-item>
            {{ $t('Current search:') }}
            <strong>{{ currentSearch.name }}</strong>
          </div>
          <div class="col-4 d-flex justify-content-end">
            <div class="btn-group btn-group-sm">
              <button type="button"
                      class="btn btn-light fixed-btn"
                      :title="$t('Edit search')"
                      :disabled="deleting"
                      @click="startEditing">
                <i class="fa-solid fa-pencil"></i>
              </button>
              <button type="button"
                      class="btn btn-danger fixed-btn"
                      :title="$t('Remove search')"
                      :disabled="deleting"
                      @click="removeSearch">
                <i class="fa-solid fa-trash"></i>
              </button>
            </div>
          </div>
        </div>
        <div class="input-group input-group-sm" v-else>
          <input class="form-control" v-model.trim="editSearchName">
          <div class="input-group-append">
            <button type="button" class="btn btn-light fixed-btn" :title="$t('Cancel')" @click="finishEditing">
              <i class="fa-solid fa-xmark"></i>
            </button>
            <button type="button"
                    class="btn btn-light fixed-btn"
                    :title="$t('Save')"
                    :disabled="!editSearchName"
                    @click="editSearch">
              <i class="fa-solid fa-floppy-disk"></i>
            </button>
          </div>
        </div>
      </div>
      <div class="card-body py-3">
        <div class="form-row" v-if="state !== 'save'">
          <div class="col-9">
            <dynamic-selection container-classes="select2-single-sm"
                               :endpoint="selectEndpoint"
                               :request-params="{object: objectType}"
                               :placeholder="$t('Select a saved search')"
                               :reset-on-select="true"
                               @select="loadSearch($event.id)">
            </dynamic-selection>
          </div>
          <div class="col-3">
            <button type="button"
                    class="btn btn-sm btn-block btn-light"
                    :title="$t('New search')"
                    :disabled="deleting"
                    @click="state = 'save'">
              <i class="fa-solid fa-plus"></i>
            </button>
          </div>
        </div>
        <div class="input-group input-group-sm" v-else>
          <input class="form-control" :placeholder="$t('Name')" v-model.trim="newSearchName">
          <div class="input-group-append">
            <button type="button" class="btn btn-light fixed-btn" :title="$t('Cancel')" @click="finishSaving">
              <i class="fa-solid fa-xmark"></i>
            </button>
            <button type="button"
                    class="btn btn-light fixed-btn"
                    :title="$t('Save')"
                    :disabled="!newSearchName"
                    @click="saveSearch">
              <i class="fa-solid fa-floppy-disk"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.fixed-btn {
  width: 35px;
}
</style>

<script>
export default {
  data() {
    return {
      currentSearch: null,
      unsavedChanges: false,
      newSearchName: '',
      editSearchName: '',
      state: null,
      deleting: false,
    };
  },
  props: {
    objectType: String,
    selectEndpoint: String,
    createEndpoint: String,
    loadBaseEndpoint: String,
    savedSearchParam: {
      type: String,
      default: 'saved_search',
    },
    ignoredParams: {
      type: Array,
      default: () => ['page'],
    },
  },
  watch: {
    currentSearch() {
      let url = null;

      if (this.currentSearch) {
        url = kadi.utils.setSearchParam(this.savedSearchParam, this.currentSearch.id);
      } else {
        url = kadi.utils.removeSearchParam(this.savedSearchParam);
      }

      kadi.utils.replaceState(url);
    },
  },
  methods: {
    onReplaceState() {
      if (this.currentSearch) {
        const savedParams = new URLSearchParams(this.currentSearch.query_string);
        savedParams.sort();

        const currentParams = new URLSearchParams(this.getQueryString());
        currentParams.sort();

        this.unsavedChanges = savedParams.toString() !== currentParams.toString();
      } else {
        this.unsavedChanges = false;
      }
    },
    getQueryString() {
      const searchParams = new URLSearchParams(window.location.search);
      const ignoredParams = [...this.ignoredParams, this.savedSearchParam];

      for (const param of ignoredParams) {
        searchParams.delete(param);
      }

      return searchParams.toString();
    },
    finishSaving() {
      this.state = null;
      this.newSearchName = '';
    },
    startEditing() {
      this.state = 'edit';
      this.editSearchName = this.currentSearch.name;
    },
    finishEditing() {
      this.state = null;
      this.editSearchName = '';
    },
    async saveSearch() {
      const data = {
        name: this.newSearchName,
        object: this.objectType,
        query_string: this.getQueryString(),
      };

      try {
        const response = await axios.post(this.createEndpoint, data);

        this.currentSearch = response.data;
        kadi.base.flashSuccess($t('Search saved successfully.'));
      } catch (error) {
        kadi.base.flashDanger($t('Error saving search.'), {request: error.request});
      } finally {
        this.finishSaving();
      }
    },
    async editSearch() {
      const queryString = this.getQueryString();

      // Check if there is anything to actually save.
      if (this.editSearchName === this.currentSearch.name && queryString === this.currentSearch.query_string) {
        this.finishEditing();
        return;
      }

      const data = {
        name: this.editSearchName,
        query_string: queryString,
      };

      try {
        const response = await axios.patch(this.currentSearch._actions.edit, data);

        this.currentSearch = response.data;
        kadi.base.flashSuccess($t('Search updated successfully.'));
      } catch (error) {
        kadi.base.flashDanger($t('Error updating search.'), {request: error.request});
      } finally {
        this.finishEditing();
      }
    },
    async removeSearch() {
      const input = await this.$refs.dialog.open($t('Are you sure you want to remove this search?'));

      if (!input.status) {
        return;
      }

      this.state = null;
      this.deleting = true;

      try {
        await axios.delete(this.currentSearch._actions.remove);

        this.currentSearch = null;
        kadi.base.flashSuccess($t('Search deleted successfully.'));
      } catch (error) {
        kadi.base.flashDanger($t('Error removing search.'), {request: error.request});
      } finally {
        this.deleting = false;
      }
    },
    async loadSearch(id, refreshPage = true) {
      const errorMsg = $t('Error loading saved search.');

      try {
        const response = await axios.get(`${this.loadBaseEndpoint}/${id}`);
        const data = response.data;

        if (data.object !== this.objectType) {
          kadi.base.flashDanger(errorMsg);
        } else {
          if (refreshPage) {
            window.location.href = data._links.view;
          } else {
            this.currentSearch = data;
          }
        }
      } catch (error) {
        kadi.base.flashDanger(errorMsg, {request: error.request});
      }
    },
  },
  mounted() {
    window.addEventListener('replacestate', this.onReplaceState);

    const id = kadi.utils.getSearchParam(this.savedSearchParam);

    if (id) {
      this.loadSearch(id, false);
    }
  },
  beforeDestroy() {
    window.removeEventListener('replacestate', this.onReplaceState);
  },
};
</script>
