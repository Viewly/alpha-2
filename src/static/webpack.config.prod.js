const baseConfig = require('./webpack.config');
const path = require("path");

module.exports = Object.assign(baseConfig, {
  output: {
    path: path.resolve(__dirname, "dist/"),
    filename: "[name]-[hash].js"
  },
})
