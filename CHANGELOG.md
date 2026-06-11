## Unreleased

### New Features

- feat(`core`): add `Object` (experimental) ([#918](https://github.com/geospaitial-lab/aviary/pull/918))
- feat(`Channel`): add `ObjectChannel` (experimental) ([#919](https://github.com/geospaitial-lab/aviary/pull/919))
- feat(`TilesProcessor`): add `ObjectExporter` (experimental) ([#920](https://github.com/geospaitial-lab/aviary/pull/920))
- feat(`TileFetcher`): add `OGCAPIFeaturesFetcher` (experimental) ([#921](https://github.com/geospaitial-lab/aviary/pull/921))

---

## 1.8.2 (2026-05-28)

### Bug Fixes

- fix: set upper bound for typer ([#914](https://github.com/geospaitial-lab/aviary/pull/914))

[Full Changelog](https://github.com/geospaitial-lab/aviary/releases/tag/1.8.2)

---

## 1.8.1 (2026-05-28)

### Bug Fixes

- fix(`Logger`): add serialize to add_handler ([#912](https://github.com/geospaitial-lab/aviary/pull/912))

[Full Changelog](https://github.com/geospaitial-lab/aviary/releases/tag/1.8.1)

---

## 1.8.0 (2026-05-26)

### New Features

- feat: add tiles / vector logs on call ([#896](https://github.com/geospaitial-lab/aviary/pull/896))
- feat(`Logger`): add serialize ([#910](https://github.com/geospaitial-lab/aviary/pull/910))

[Full Changelog](https://github.com/geospaitial-lab/aviary/releases/tag/1.8.0)

---

## 1.7.0 (2026-05-16)

### New Features

- feat(utils): add `Logger` ([#891](https://github.com/geospaitial-lab/aviary/pull/891))
- feat(cli): add log-level option ([#892](https://github.com/geospaitial-lab/aviary/pull/892))
- feat: add log util ([#893](https://github.com/geospaitial-lab/aviary/pull/893))

### Bug Fixes

- fix(cli): add default value to log-level option ([#894](https://github.com/geospaitial-lab/aviary/pull/894))

[Full Changelog](https://github.com/geospaitial-lab/aviary/releases/tag/1.7.0)

---

## 1.6.0 (2026-05-15)

### New Features

- feat(`RasterExporter`): add dynamic block size ([#877](https://github.com/geospaitial-lab/aviary/pull/877))
- feat(`RasterChannel`): add dtype and cast ([#878](https://github.com/geospaitial-lab/aviary/pull/878))
- feat(`TilesProcessor`): add `CastProcessor` ([#879](https://github.com/geospaitial-lab/aviary/pull/879))
- feat(`TilesProcessor`): add `SieveProcessor` ([#880](https://github.com/geospaitial-lab/aviary/pull/880))
- feat(`ExpressionProcessor`): add dtype ([#881](https://github.com/geospaitial-lab/aviary/pull/881))
- feat(`NormalizeProcessor`): add dtype ([#882](https://github.com/geospaitial-lab/aviary/pull/882))
- feat(`StandardizeProcessor`): add dtype ([#883](https://github.com/geospaitial-lab/aviary/pull/883))
- feat(`RasterizeProcessor`): add dtype ([#884](https://github.com/geospaitial-lab/aviary/pull/884))
- feat(`WMSFetcher`): add time ([#885](https://github.com/geospaitial-lab/aviary/pull/885))
- feat(`RasterExporter`): add channel descriptions ([#886](https://github.com/geospaitial-lab/aviary/pull/886))
- feat(`RasterExporter`): add dynamic predictor ([#887](https://github.com/geospaitial-lab/aviary/pull/887))
- feat(`RasterExporter`): add mapping ([#888](https://github.com/geospaitial-lab/aviary/pull/888))

[Full Changelog](https://github.com/geospaitial-lab/aviary/releases/tag/1.6.0)

---

## 1.5.0 (2026-05-12)

### New Features

- feat(`Grid`): add buffer ([#871](https://github.com/geospaitial-lab/aviary/pull/871))
- feat(`Pipeline`): add spinner ([#873](https://github.com/geospaitial-lab/aviary/pull/873))
- feat(cli): add experimental-warnings option ([#874](https://github.com/geospaitial-lab/aviary/pull/874))

### Bug Fixes

- fix(`Grid`): cast coordinates ([#872](https://github.com/geospaitial-lab/aviary/pull/872))

[Full Changelog](https://github.com/geospaitial-lab/aviary/releases/tag/1.5.0)

---

## 1.4.0 (2026-05-10)

### New Features

- feat(`TileFetcher`): add `GPKGFetcher` (experimental) ([#862](https://github.com/geospaitial-lab/aviary/pull/862))
- feat(`TilesProcessor`): add `RasterizeProcessor` (experimental) ([#863](https://github.com/geospaitial-lab/aviary/pull/863))
- feat(`TilesProcessor`): add `StubProcessor` (experimental) ([#864](https://github.com/geospaitial-lab/aviary/pull/864))
- feat(`TileFetcher`): add `StubFetcher` (experimental) ([#865](https://github.com/geospaitial-lab/aviary/pull/865))
- feat(`VectorProcessor`): add `StubProcessor` (experimental) ([#866](https://github.com/geospaitial-lab/aviary/pull/866))
- feat(`VectorLoader`): add `StubLoader` (experimental) ([#867](https://github.com/geospaitial-lab/aviary/pull/867))

### Bug Fixes

- fix(`RasterExporter`): include buffer ([#868](https://github.com/geospaitial-lab/aviary/pull/868))

[Full Changelog](https://github.com/geospaitial-lab/aviary/releases/tag/1.4.0)

---

## 1.3.0 (2026-05-07)

### New Features

- feat(`Grid`): add from_osm (experimental) ([#823](https://github.com/geospaitial-lab/aviary/pull/823))
- feat(`RasterChannel`): add ground_sampling_distance ([#836](https://github.com/geospaitial-lab/aviary/pull/836))
- feat: add IDMixin ([#835](https://github.com/geospaitial-lab/aviary/pull/835))
- feat(`TilesProcessor`): add `ExpressionProcessor` (experimental) ([#838](https://github.com/geospaitial-lab/aviary/pull/838))
- feat(`TilesProcessor`): add `RasterExporter` (experimental) ([#856](https://github.com/geospaitial-lab/aviary/pull/856))
- feat(`TilesProcessor`): add `AspectProcessor`, `HillshadeProcessor`, and `SlopeProcessor` (experimental) ([#859](https://github.com/geospaitial-lab/aviary/pull/859))
- feat(cli): show deprecated or experimental in components and plugins command output ([#860](https://github.com/geospaitial-lab/aviary/pull/860))

### Bug Fixes

- fix(`StandardizeProcessor`): cast data item ([#842](https://github.com/geospaitial-lab/aviary/pull/842))
- fix(`WMSFetcher`): add user agent ([#857](https://github.com/geospaitial-lab/aviary/pull/857))

[Full Changelog](https://github.com/geospaitial-lab/aviary/releases/tag/1.3.0)

---

## 1.2.0 (2026-03-09)

### Other Changes

- build: support python version 3.13 ([#802](https://github.com/geospaitial-lab/aviary/pull/802))

[Full Changelog](https://github.com/geospaitial-lab/aviary/releases/tag/1.2.0)

---

## 1.1.0 (2026-01-21)

### Other Changes

- docs(how-to-guides): add bounding box ([#781](https://github.com/geospaitial-lab/aviary/pull/781))

[Full Changelog](https://github.com/geospaitial-lab/aviary/releases/tag/1.1.0)
