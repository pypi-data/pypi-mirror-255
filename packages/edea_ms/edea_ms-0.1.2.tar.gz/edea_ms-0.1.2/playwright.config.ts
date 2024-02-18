import { type PlaywrightTestConfig, devices } from '@playwright/test';

const config: PlaywrightTestConfig = {
	webServer: {
		command: 'npm run build && npm run preview',
		port: 4173
	},
	testDir: 'tests',
	testMatch: /.*\.ts/,

	projects: [
		// Setup project
		{ name: 'setup', testMatch: /.*\.setup\.ts/ },

		{
			name: 'chromium',
			use: {
				...devices['Desktop Chrome'],
				// Use prepared auth state.
				storageState: 'playwright/.auth/user.json',
			},
			dependencies: ['setup'],
		},

		{
			name: 'firefox',
			use: {
				...devices['Desktop Firefox'],
				// Use prepared auth state.
				storageState: 'playwright/.auth/user.json',
			},
			dependencies: ['setup'],
		},
	],
};

export default config;
