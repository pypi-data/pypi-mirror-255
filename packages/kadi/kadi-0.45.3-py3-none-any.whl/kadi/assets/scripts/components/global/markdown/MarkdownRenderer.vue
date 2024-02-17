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
  <span v-html="result"></span>
</template>

<script>
import markdownit from 'markdown-it';
import markdownitSub from 'markdown-it-sub';
import markdownitSup from 'markdown-it-sup';
import markdownitTexmath from 'markdown-it-texmath';

export default {
  data() {
    return {
      renderer: null,
      result: '',
    };
  },
  props: {
    input: String,
  },
  watch: {
    input() {
      this.render();
    },
  },
  methods: {
    render() {
      this.result = this.renderer.render(this.input);
    },
  },
  mounted() {
    this.renderer = markdownit()
      .use(markdownitSub)
      .use(markdownitSup)
      .use(markdownitTexmath, {outerSpace: true, katexOptions: {output: 'html', maxSize: 10, maxExpand: 100}});

    // Customize some of the rendering rules.
    this.renderer.renderer.rules.heading_open = (tokens, idx, options, env, self) => {
      const token = tokens[idx];
      const sizes = [1.7, 1.5, 1.4, 1.3, 1.2, 1.1];
      const level = token.markup.length - 1;

      token.attrSet('class', 'font-weight-bold');
      token.attrSet('style', `font-size: ${sizes[level]}rem`);

      return self.renderToken(tokens, idx, options);
    };

    this.renderer.renderer.rules.link_open = (tokens, idx, options, env, self) => {
      const token = tokens[idx];

      token.attrSet('target', '_blank');
      token.attrSet('rel', 'noopener noreferrer');
      token.attrSet('style', 'color: inherit; text-decoration: underline');

      return self.renderToken(tokens, idx, options);
    };

    this.renderer.renderer.rules.table_open = (tokens, idx, options, env, self) => {
      const token = tokens[idx];

      token.attrSet('class', 'table table-sm table-bordered table-hover');
      token.attrSet('style', 'color: inherit');

      return self.renderToken(tokens, idx, options);
    };

    const imageRenderer = this.renderer.renderer.rules.image;

    this.renderer.renderer.rules.image = (tokens, idx, options, env, self) => {
      const token = tokens[idx];
      const src = token.attrGet('src') || '';

      // For images loaded via Kadi, we only use the path of the image source to stay domain-independent, which also
      // ensures that even full URLs with an incorrect domain work correctly.
      if (src.includes('/api/records')) {
        let srcPath = '';

        // The URL might already be specified without a domain.
        try {
          srcPath = new URL(src).pathname;
        } catch {
          srcPath = src;
        }

        token.attrSet('src', srcPath);
      }
      token.attrSet('style', 'max-width: 33%');

      return imageRenderer(tokens, idx, options, env, self);
    };

    this.render();
  },
};
</script>
