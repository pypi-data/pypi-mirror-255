import { sveltekit } from '@sveltejs/kit/vite';
import type { UserConfig } from 'vite';
import { purgeCss } from 'vite-plugin-tailwind-purgecss';

const config: UserConfig = {
	plugins: [sveltekit(), purgeCss()],
	server: {
		proxy: {
			'/api': {
				target: 'http://127.0.0.1:8000',
				changeOrigin: true
			}
		},
	},
};

export default config;
