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
  <div class="dropup float-lg-right">
    <a class="text-white dropdown-toggle" href="#" data-toggle="dropdown">
      <i class="fa-solid fa-globe"></i> {{ $t('Language') }}
    </a>
    <div class="dropdown-menu dropdown-menu-right mb-3">
      <strong class="dropdown-header">{{ $t('Select a language') }}</strong>
      <button type="button"
              class="dropdown-item"
              v-for="(language, locale) in locales"
              :key="locale"
              @click="switchLocale(locale)">
        {{ language }}
        <span class="float-right" v-if="locale === kadi.globals.locale">
          <i class="fa-solid fa-check fa-sm"></i>
        </span>
      </button>
    </div>
  </div>
</template>

<script>
import localeCookieMixin from 'scripts/components/mixins/locale-cookie-mixin';

export default {
  mixins: [localeCookieMixin],
  props: {
    locales: Object,
  },
};
</script>
