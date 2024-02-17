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
  <dynamic-pagination :endpoint="endpoint" :placeholder="$t('No revisions.')" ref="pagination">
    <template #default="props">
      <p v-if="title">
        <strong>{{ title }}</strong>
        <span class="badge badge-pill badge-light text-muted border border-muted">{{ props.total }}</span>
      </p>
      <div v-for="(revision, index) in props.items"
           :key="revision.id"
           :class="{'mb-3': index < props.items.length - 1}">
        <div class="form-row align-items-center">
          <div class="col-md-1 d-md-flex justify-content-center d-none d-md-block">
            <span class="fa-stack">
              <i class="fa-solid fa-circle fa-stack-2x" :class="getRevisionType(revision).color"></i>
              <i class="fa-solid fa-stack-1x text-white" :class="getRevisionType(revision).icon"></i>
            </span>
          </div>
          <div class="col-md-8">
            <span v-if="revision.user">
              <identity-popover :user="revision.user"></identity-popover>
              <em>{{ getRevisionType(revision).textUser }}</em>
            </span>
            <slot :revision="revision">
              <strong>{{ revision.data.title }}</strong>
            </slot>
            <span v-if="!revision.user">
              <em>{{ getRevisionType(revision).textNoUser }}</em>
            </span>
            <br>
            <a :href="revision._links.view">
              <i class="fa-solid fa-eye"></i> {{ $t('View revision') }}
            </a>
          </div>
          <div class="col-md-3 text-md-right">
            <small class="text-muted">
              <from-now :timestamp="revision.timestamp"></from-now>
            </small>
          </div>
        </div>
      </div>
    </template>
  </dynamic-pagination>
</template>

<script>
export default {
  data() {
    return {
      revisionType: {
        created: {
          color: 'text-success',
          icon: 'fa-plus',
          textUser: $t('created', {context: 'revision'}),
          textNoUser: $t('was created'),
        },
        updated: {
          color: 'text-primary',
          icon: 'fa-pencil',
          textUser: $t('updated', {context: 'revision'}),
          textNoUser: $t('was updated'),
        },
        deleted: {
          color: 'text-danger',
          icon: 'fa-trash',
          textUser: $t('deleted', {context: 'revision'}),
          textNoUser: $t('was deleted'),
        },
        restored: {
          color: 'text-info',
          icon: 'fa-trash-arrow-up',
          textUser: $t('restored', {context: 'revision'}),
          textNoUser: $t('was restored'),
        },
      },
    };
  },
  props: {
    endpoint: String,
    title: {
      type: String,
      default: '',
    },
    activeState: {
      type: String,
      default: 'active',
    },
  },
  methods: {
    getRevisionType(revision) {
      // To decide on the revision type, the 'state' property in the revision data and potentially the diff is checked.
      if (revision.data.state === this.activeState) {
        // For active states, check if there is also a corresponding diff. If so, the revision either represents a
        // creation or restoration, depending on the previous state. Otherwise, we assume an update.
        if (revision.diff.state) {
          if (revision.diff.state.prev === null) {
            return this.revisionType.created;
          }
          return this.revisionType.restored;
        }

        return this.revisionType.updated;
      }

      // For other state values, we assume the state represents the item's deleted state. If there is a corresponding
      // diff, we assume a deletion, and an update otherwise.
      if (revision.diff.state) {
        return this.revisionType.deleted;
      }
      return this.revisionType.updated;
    },
    // Convenience function for forcing an update from outside.
    update() {
      this.$refs.pagination.update();
    },
  },
};
</script>
