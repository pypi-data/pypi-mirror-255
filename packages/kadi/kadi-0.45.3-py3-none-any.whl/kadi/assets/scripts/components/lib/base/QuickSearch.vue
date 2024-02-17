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
  <div class="dropdown" :id="`dropdown-${id}`" :class="{'active': dropdownActive}">
    <div class="input-group input-group-sm responsive-width" @click="showDropdown">
      <div class="input-group-prepend">
        <button type="button" class="btn toggle-btn" :title="$t('Toggle search mode')" @click.stop="toggleSearchMode">
          <i class="fa-solid fa-magnifying-glass fa-sm" v-if="searchByQuery"></i>
          <i class="fa-solid fa-hashtag fa-sm" v-else></i>
        </button>
      </div>
      <input class="form-control custom-input"
             :placeholder="searchByQuery ? $t('Quick search') : $t('Find persistent ID')"
             v-model.trim="input"
             ref="input">
      <div class="input-group-append" v-if="input">
        <button type="button"
                class="btn btn-sm clear-btn"
                :class="{'dropdown-active': dropdownActive}"
                @click.stop="clearInput">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>
    </div>
    <div class="dropdown-menu responsive-width" :class="{'d-block': dropdownActive}">
      <div v-if="initialized">
        <div class="px-2 my-1" v-if="items.length === 0">
          <strong class="font-identifier text-muted">{{ $t('No results.') }}</strong>
        </div>
        <div v-for="(item, index) in items" :key="item._links.view" v-else>
          <a class="dropdown-item text-default p-2" :href="item._links.view">
            <span class="badge badge-light border border-muted font-weight-normal mb-2 d-xl-none">
              {{ item.pretty_type }}
            </span>
            <div class="d-flex justify-content-between">
              <strong class="font-title wb-break-word">{{ kadi.utils.truncate(item.title, 50) }}</strong>
              <div class="d-none d-xl-block">
                <span class="badge badge-light border border-muted font-weight-normal ml-3">
                  {{ item.pretty_type }}
                </span>
              </div>
            </div>
            <span class="font-identifier">@{{ item.identifier }}</span>
            <br>
            <span class="text-muted font-timestamp">
              {{ $t('Last modified') }} <from-now :timestamp="item.last_modified"></from-now>
            </span>
          </a>
          <div class="dropdown-divider m-0" v-if="index < items.length - 1"></div>
        </div>
      </div>
      <i class="fa-solid fa-circle-notch fa-spin p-2" v-if="!initialized"></i>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.clear-btn {
  background-color: #1a252f;
  border: none;
  color: #7b8a8b;
  padding-right: 0.75rem !important;
  transition: none;

  &:focus {
    box-shadow: none;
  }

  &:hover {
    color: white;
  }

  &.dropdown-active {
    &:hover {
      color: black;
    }
  }
}

.custom-input {
  background-color: #1a252f;
  border: none;
  border-left: 1px solid #2c3e50;
  box-shadow: none;
  -webkit-appearance: none;
}

.dropdown.active {
  .custom-input, .clear-btn {
    background-color: white !important;
  }
}

.dropdown-item {
  white-space: normal;
  word-break: break-all;

  &:focus, &:hover {
    background-color: #ecf0f1;
  }
}

.dropdown-menu {
  margin-top: 1.25rem;
  padding-bottom: 2px;
  padding-top: 2px;
}

.font-identifier {
  font-size: 90%;
}

.font-timestamp {
  font-size: 80%;
}

.font-title {
  font-size: 95%;
}

.responsive-width {
  width: 225px;

  @media (min-width: 1200px) {
    width: 350px;
  }
}

.toggle-btn {
  background-color: #1a252f;
  color: white;
  transition: none;
  width: 35px;

  &:focus {
    box-shadow: none;
  }

  &:hover {
    color: #7b8a8b;
  }
}
</style>

<script>
export default {
  data() {
    return {
      id: kadi.utils.randomAlnum(),
      input: '',
      items: [],
      searchByQuery: true,
      dropdownActive: false,
      initialized: false,
      searchTimeoutHandle: null,
    };
  },
  props: {
    endpoint: String,
  },
  watch: {
    input() {
      if (!this.searchByQuery) {
        this.convertInput();
      }

      this.search();
    },
  },
  methods: {
    outsideClickHandler(event) {
      if (event.target.closest(`#dropdown-${this.id}`) === null) {
        this.dropdownActive = false;
      }
    },
    showDropdown() {
      if (!this.dropdownActive) {
        this.dropdownActive = true;

        if (!this.initialized) {
          this.search();
        }
      }
    },
    toggleSearchMode() {
      this.searchByQuery = !this.searchByQuery;
      this.dropdownActive = true;
      this.$refs.input.focus();

      if (!this.searchByQuery) {
        this.convertInput();
      }

      this.search();
    },
    clearInput() {
      this.input = '';
      this.dropdownActive = true;
      this.$refs.input.focus();
    },
    convertInput() {
      let input = Number.parseInt(this.input, 10);

      if (!input || input < 1) {
        input = '';
      }

      this.input = input;
    },
    search() {
      window.clearTimeout(this.searchTimeoutHandle);

      const _search = async() => {
        try {
          const params = {[this.searchByQuery ? 'query' : 'id']: this.input};
          const response = await axios.get(this.endpoint, {params});

          this.items = response.data;
          this.initialized = true;
        } catch (error) {
          kadi.base.flashDanger($t('Error loading search results.'), {request: error.request});
        }
      };

      this.searchTimeoutHandle = window.setTimeout(_search, 300);
    },
  },
  mounted() {
    document.addEventListener('click', this.outsideClickHandler);
  },
  beforeDestroy() {
    document.removeEventListener('click', this.outsideClickHandler);
  },
};
</script>
