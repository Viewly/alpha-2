const baseConfig = require('./webpack.config');
const path = require("path");
const webpack = require("webpack");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");

module.exports = Object.assign(baseConfig, {
  output: {
    path: path.resolve(__dirname, "dist/"),
    filename: "[name]-[hash].js"
  },
  plugins: [
    new webpack.HotModuleReplacementPlugin(),
    new MiniCssExtractPlugin({
      // Options similar to the same options in webpackOptions.output
      // both options are optional
      filename: "style-[hash].css",
      chunkFilename: "[id].css"
    })
  ]
})
