<!-- Copyright 2022 Karlsruhe Institute of Technology
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
  <div class="card" v-show="items.length > 0" v-if="kadi.globals.user_active">
    <div class="card-header border-bottom-0 py-1">
      <collapse-item class="text-default stretched-link"
                     :id="id"
                     :is-collapsed="collapsed"
                     @collapse="collapsed = $event">
        <strong>{{ $t('Recently visited') }}</strong>
      </collapse-item>
    </div>
    <div class="card-body items" :id="id">
      <div class="list-group list-group-flush">
        <div class="list-group-item list-group-item-action" v-for="item in items" :key="item.id">
          <a class="text-default stretched-link wb-break-word" :href="item.endpoint">
            <div class="d-flex justify-content-between">
              <strong class="font-title">{{ kadi.utils.truncate(item.title, 50) }}</strong>
              <div class="type">
                <span class="badge badge-light border border-muted font-weight-normal ml-3">
                  {{ itemTypes[item.type] || item.type }}
                </span>
              </div>
            </div>
            <span class="font-identifier">@{{ item.identifier }}</span>
            <br>
            <span class="text-muted font-timestamp">
              {{ $t('Last visited') }} <from-now :timestamp="item.timestamp"></from-now>
            </span>
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.font-identifier {
  font-size: 90%;
}

.font-timestamp {
  font-size: 80%;
}

.font-title {
  font-size: 95%;
}

.items {
  padding: 0 0 1px 0;
}

.type {
  @media (min-width: 1200px) and (max-width: 1500px) {
    display: none;
  }
}
</style>

<script>
export default {
  data() {
    return {
      items: [],
      itemsStorageKey: 'recently_visited_items',
      collapseStorageKey: 'recently_visited_collapse',
      id: kadi.utils.randomAlnum(),
      collapsed: null,
      initialized: false,
      itemTypes: {
        record: $t('Record'),
        collection: $t('Collection'),
        template: $t('Template'),
        group: $t('Group'),
      },
    };
  },
  props: {
    maxItems: {
      type: Number,
      default: 5,
    },
  },
  watch: {
    collapsed() {
      if (this.collapsed) {
        window.localStorage.setItem(this.collapseStorageKey, 'true');
      } else {
        window.localStorage.removeItem(this.collapseStorageKey);
      }
    },
  },
  methods: {
    addItem(type, title, identifier, endpoint, timestamp = null) {
      const item = {
        id: kadi.utils.randomAlnum(),
        timestamp: timestamp || new Date().toISOString(),
        type,
        title,
        identifier,
        endpoint,
      };

      // If an item already exists, it will be removed at first and then added again, with potentially updated values.
      // We simply use the endpoint as a unique identification of an item.
      const index = this.items.findIndex((el) => el.endpoint === endpoint);

      if (index !== -1) {
        this.items.splice(index, 1);
      }

      // Add items in order when initializing and to the front otherwise.
      if (!this.initialized) {
        this.items.push(item);
      } else {
        this.items.unshift(item);
      }

      this.items = this.items.slice(0, this.maxItems);

      if (this.initialized) {
        this.persistItems();
      }
    },
    persistItems() {
      const results = [];

      for (const item of this.items) {
        const newItem = {...item};
        delete newItem.id;
        results.push(newItem);
      }

      window.localStorage.setItem(this.itemsStorageKey, JSON.stringify(results));
    },
    clearItems() {
      window.localStorage.removeItem(this.itemsStorageKey);
    },
  },
  created() {
    if (kadi.globals.user_active) {
      if (window.localStorage.getItem(this.collapseStorageKey)) {
        this.collapsed = true;
      } else {
        this.collapsed = false;
      }
    }
  },
  mounted() {
    if (!kadi.globals.user_active) {
      // Simply clear all items for non-active users.
      this.clearItems();
    } else {
      try {
        const items = JSON.parse(window.localStorage.getItem(this.itemsStorageKey));

        for (const item of items) {
          this.addItem(item.type, item.title, item.identifier, item.endpoint, item.timestamp);
        }
      } catch {
        this.clearItems();
      }

      this.initialized = true;
    }
  },
};
</script>
