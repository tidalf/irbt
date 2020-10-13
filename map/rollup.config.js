import commonjs from 'rollup-plugin-commonjs';
import nodeResolve from 'rollup-plugin-node-resolve';
import { terser } from 'rollup-plugin-terser';

const pkg = {
    name: 'robmap'
};

const outputDefault = {
    exports: 'named',
    globals: {}
};

const output = [
    { ...outputDefault, file: `html/js/${pkg.name}.js`, format: 'es', name: pkg.name },
];

const plugins = [
    nodeResolve({}), // resolve modules in node_modulels/
    commonjs({}), // commonjs module format
    terser({}) // minify
];

const configuration = [{
    name: 'robMap',
    input: './build/app.js',
    external: [],
    output,
    plugins,
}];

export default configuration;
