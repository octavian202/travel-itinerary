// Use env for Mapbox token so it's not committed
module.exports = {
  expo: {
    name: 'City Break Planner',
    slug: 'city-break-planner',
    version: '0.1.0',
    orientation: 'portrait',
    icon: './assets/icon.png',
    userInterfaceStyle: 'automatic',
    scheme: 'citybreak',
    plugins: [
      [
        '@rnmapbox/maps',
        {
          RNMapboxMapsDownloadToken: process.env.MAPBOX_SECRET_TOKEN || 'YOUR_MAPBOX_SECRET_TOKEN',
        },
      ],
    ],
    splash: {
      image: './assets/splash-icon.png',
      resizeMode: 'contain',
      backgroundColor: '#1a1a2e',
    },
    assetBundlePatterns: ['**/*'],
    ios: { supportsTablet: true, bundleIdentifier: 'com.citybreak.planner' },
    android: {
      adaptiveIcon: {
        foregroundImage: './assets/adaptive-icon.png',
        backgroundColor: '#1a1a2e',
      },
      package: 'com.citybreak.planner',
    },
  },
};
