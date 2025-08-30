import type { ShikiSetupReturn } from '@slidev/types'
import { defineShikiSetup } from '@slidev/types'

export default defineShikiSetup((): ShikiSetupReturn => {
  return {
    themes: {
      dark: 'material-theme-darker',
      light: 'material-theme-lighter',
    },
    transformers: [
      // Custom transformer for nuclear-hacker theme
      {
        name: 'nuclear-hacker-theme',
        preprocess(code, options) {
          return code
        },
        postprocess(html) {
          // Simply add the nuclear-code class to shiki containers
          // The CSS will handle the styling without nested HTML modifications
          return html.replace(/class="shiki"/g, 'class="shiki nuclear-code"')
        }
      }
    ]
  }
})
