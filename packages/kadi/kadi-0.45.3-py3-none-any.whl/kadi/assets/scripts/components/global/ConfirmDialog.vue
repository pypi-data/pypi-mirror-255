<!-- Copyright 2024 Karlsruhe Institute of Technology
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
  <div class="modal" tabindex="-1" @keydown.enter="handleEnter" ref="dialog">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-body">
          <span ref="message"></span>
          <input class="form-control form-control-sm mt-2" v-model="promptValue" v-if="showPrompt" ref="prompt">
        </div>
        <div class="modal-footer justify-content-between">
          <div>
            <button type="button" class="btn btn-sm btn-primary btn-modal" data-dismiss="modal" ref="btnAccept">
              {{ acceptText }}
            </button>
            <button type="button" class="btn btn-sm btn-light btn-modal" data-dismiss="modal" ref="btnCancel">
              {{ cancelText }}
            </button>
          </div>
          <div class="form-check" v-if="showCheckbox">
            <input type="checkbox" class="form-check-input" :id="`apply-all-${suffix}`" v-model="checkboxValue">
            <label class="form-check-label" :for="`apply-all-${suffix}`">{{ checkboxText }}</label>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.btn-modal {
  width: 100px;
}
</style>

<script>
export default {
  data() {
    return {
      suffix: kadi.utils.randomAlnum(),
      showPrompt: false,
      promptValue: '',
      showCheckbox: false,
      checkboxValue: false,
    };
  },
  props: {
    acceptText: {
      type: String,
      default: $t('Yes'),
    },
    cancelText: {
      type: String,
      default: $t('No'),
    },
    checkboxText: {
      type: String,
      default: $t('Apply to all'),
    },
  },
  methods: {
    handleEnter() {
      this.$refs.btnAccept.click();
    },
    async open(msg, showPrompt = false, showCheckbox = false) {
      this.showPrompt = showPrompt;
      this.showCheckbox = showCheckbox;

      await this.$nextTick();

      return new Promise((resolve) => {
        $(this.$refs.dialog).on('shown.bs.modal', () => {
          // Move the backdrop directly behind the modal dialog once it is shown to ensure that it is always visible.
          const backdrop = document.getElementsByClassName('modal-backdrop')[0];
          this.$el.parentNode.insertBefore(backdrop, this.$el.nextSibling);

          if (this.showPrompt) {
            this.$refs.prompt.focus();
          }
        });

        $(this.$refs.dialog).modal({backdrop: 'static', keyboard: false});
        this.$refs.message.innerText = msg;

        let acceptHandler = null;
        let cancelHandler = null;

        // Make sure that the event listeners are removed again and all inputs are reset after resolving the promise by
        // closing the modal via one of the buttons.
        const resolveDialog = (status) => {
          resolve({status, prompt: this.promptValue, checkbox: this.checkboxValue});

          this.promptValue = '';
          this.checkboxValue = false;

          this.$refs.btnAccept.removeEventListener('click', acceptHandler);
          this.$refs.btnCancel.removeEventListener('click', cancelHandler);
        };

        acceptHandler = () => resolveDialog(true);
        cancelHandler = () => resolveDialog(false);

        this.$refs.btnAccept.addEventListener('click', acceptHandler);
        this.$refs.btnCancel.addEventListener('click', cancelHandler);
      });
    },
  },
  beforeDestroy() {
    $(this.$refs.dialog).modal('dispose');
  },
};
</script>
