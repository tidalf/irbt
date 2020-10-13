# RobMap

Draw robot map!

## Note

  * Lot of typescript errors, thing is built anyway but that's ugly!
  * The data is in `src/data.ts`, it's just the *JSON* pasted and exported (easier for dev).
  * `src/map-parser` contain interfaces for the *JSON* robot map format, but it's not finished and buggy.
  * Rollup bundle is writed in `html/bundle.js`.
  * Map should be scaled by getting `min/max` for all `x, y` and mapping the range to `0, n`.

## Prerequisite

  * node `>= 12.11.1`
  * yarn `>= 1.19.0`

## Install

```bash
yarn
```

## Start

Will open you browser with the HTML located in `html/index.html` after the bundle has been built.

```bash
yarn start
```

## Build

```bash
yarn build
```

## Watch

You need two watchers, the one that transpile *Typescript* and the one that create the **bundle**.

```bash
yarn watch:transpile
yarn watch:bundle
```

## Open

Should open ```html/index.htm``` in your favorite browser.

```bash
yarn open
```