<!-- Copyright 2021 Karlsruhe Institute of Technology
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
  <div ref="container">
    <div class="card toolbar" ref="toolbar">
      <div class="card-body px-1 py-0">
        <button type="button"
                :title="$t('Decrease link depth')"
                :class="toolbarBtnClasses"
                :disabled="!initialized || depth <= minDepth"
                @click="depth--">
          <i class="fa-solid fa-angle-left"></i>
        </button>
        <strong>{{ $t('Link depth:') }} {{ depth }}</strong>
        <button type="button"
                :title="$t('Increase link depth')"
                :class="toolbarBtnClasses"
                :disabled="!initialized || depth >= maxDepth"
                @click="depth++">
          <i class="fa-solid fa-angle-right"></i>
        </button>
        <button type="button"
                :title="$t('Toggle forces')"
                :class="toolbarBtnClasses + (forceDisabled ? ' border-active' : '')"
                :disabled="!initialized"
                @click="forceDisabled = !forceDisabled">
          <i class="fa-solid fa-thumbtack"></i>
        </button>
        <button type="button"
                :title="$t('Hide labels')"
                :class="toolbarBtnClasses + (labelsHidden ? ' border-active' : '')"
                :disabled="!initialized"
                @click="toggleLabels">
          <i class="fa-solid fa-font"></i>
        </button>
        <button type="button"
                :title="$t('Download graph')"
                :class="toolbarBtnClasses"
                :disabled="!initialized"
                @click="downloadGraph">
          <i class="fa-solid fa-download"></i>
        </button>
        <button type="button"
                :title="$t('Reset view')"
                :class="toolbarBtnClasses"
                :disabled="!initialized"
                @click="resetView">
          <i class="fa-solid fa-eye"></i>
        </button>
        <button type="button"
                :title="$t('Toggle fullscreen')"
                :class="toolbarBtnClasses"
                :disabled="!initialized"
                @click="toggleFullscreen">
          <i class="fa-solid fa-expand"></i>
        </button>
        <i class="fa-solid fa-circle-notch fa-spin text-muted ml-3" v-if="loading"></i>
      </div>
    </div>
    <div class="card graph" ref="graphContainer"></div>
  </div>
</template>

<style scoped>
.border-active {
  border: 1px solid #ced4da;
}

.graph {
  border: 1px solid #ced4da;
  border-radius: 0px;
}

.toolbar {
  border-bottom-left-radius: 0px;
  border-bottom-right-radius: 0px;
  border-color: #ced4da;
  margin-bottom: -1px;
}
</style>

<script>
import graphMixin from 'scripts/components/mixins/graph-mixin';

export default {
  mixins: [graphMixin],
  data() {
    return {
      depth: null,
      minDepth: 1,
      maxDepth: 3,
      updateTimeoutHandle: null,
    };
  },
  props: {
    startRecord: Number,
    initialDepth: {
      type: Number,
      default: 1,
    },
    direction: {
      type: String,
      default: '',
    },
  },
  watch: {
    depth() {
      if (this.initialized) {
        window.clearTimeout(this.updateTimeoutHandle);
        this.updateTimeoutHandle = window.setTimeout(this.updateData, 500);

        this.$emit('update-depth', this.depth);
      }
    },
    direction() {
      this.updateData();
    },
    isRendered() {
      this.resizeView(this.$refs.container, this.$refs.toolbar);
    },
  },
  methods: {
    getStartNode() {
      return this.nodes.find((node) => node.id === this.startRecord) || null;
    },
    toggleFullscreen() {
      kadi.utils.toggleFullscreen(this.$refs.container);
    },
    resizeCallback() {
      this.resizeView(this.$refs.container, this.$refs.toolbar);
      this.resetView();
    },
    updateGraph() {
      // For simplicity, we just remove the existing nodes and links each time.
      this.nodesContainer.selectAll('*').remove();
      this.linksContainer.selectAll('*').remove();

      this.simulation.nodes(this.nodes);
      this.simulation.force(this.forces.link).links(this.links);

      this.drawNodes();
      this.drawLinks();
      this.drawLegend();

      this.filterNodes();

      this.simulation.alpha(1).restart();
    },
    async updateData() {
      this.loading = true;

      try {
        const params = {depth: this.depth, direction: this.direction};
        const response = await axios.get(this.endpoint, {params});

        const data = response.data;
        const prevStartNode = this.getStartNode();

        this.nodes = data.records;
        this.links = data.record_links;

        for (const node of this.nodes) {
          node._type = this.types.record;
        }

        // Give the start node a fixed position based on its previous position or use the origin as fallback.
        const startNode = this.getStartNode();

        if (startNode) {
          startNode.fx = prevStartNode ? prevStartNode.x : 0;
          startNode.fy = prevStartNode ? prevStartNode.y : 0;
        }

        this.updateGraph();
      } catch (error) {
        kadi.base.flashDanger($t('Error loading record links.'), {request: error.request});
      } finally {
        this.initialized = true;
        this.loading = false;
        this.forceDisabled = false;
      }
    },
  },
  created() {
    this.depth = kadi.utils.clamp(this.initialDepth, this.minDepth, this.maxDepth);
  },
  mounted() {
    this.createContainers(this.$refs.graphContainer);
    this.createSimulation();

    this.resizeCallback();
    this.updateData();

    window.addEventListener('resize', this.resizeCallback);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.resizeCallback);
  },
};
</script>
