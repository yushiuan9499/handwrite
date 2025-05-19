export default {
  plugins: [
    {
      name: 'preset-default',
      params: {
        overrides: {
          // disable a default plugin
          mergePaths: false,
          convertPathData: false,
        },
      },
    },
  ],
};
