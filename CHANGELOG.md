# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.5] - 2022-10-19

### Added
* `.xlsx` input
* if `legend_position` is set to `None`, no legend is shown

### Fixed
* hatches of unique values are now displayed correctly (fake coords in antarctica)

## [0.0.4] -- 2022-09-29

### Changed
* better API by @xrotwang

### Fixed
* pinned dependencies

## [0.0.3] -- 2022-09-19

### Added
* `hatching` for black-and-white maps with many values

### Changed
* `text_df` can specify a filename, to be read with pandas

### Fixed
* missing dependencies

## [0.0.2] -- 2022-09-17

### Added
* `print_labels` (default: true): print language labels on the tree leafs
* `leaf_lw` (default: from pyplot): line width of tree branches
* `connection_lw` (default: 1): line width of the leaf-map connections
* `map_marker_lw` (default: 1): line width of the circles on the map
* `color_tree` (default: false): color the lines leading to colored nodes
* `nonterminal_nodes` (default: false): put circle markers onto proto-notes

### Changed
* if proto-nodes are present in the value dataframe, their values can be shown by activating `color_tree` and/or `nonterminal_nodes`

## [0.0.1] - 2022-08-29

Initial release

[Unreleased]: https://github.com/fmatter/lingtreemaps/compare/v0.0.5...HEAD
[0.0.5]: https://github.com/fmatter/lingtreemaps/compare/0.0.4...v0.0.5
[0.0.4]: https://github.com/fmatter/lingtreemaps/releases/tag/0.0.4
[0.0.3]: https://github.com/fmatter/lingtreemaps/releases/tag/0.0.3
[0.0.2]: https://github.com/fmatter/lingtreemaps/releases/tag/0.0.2
[0.0.1]: https://github.com/fmatter/lingtreemaps/releases/tag/0.0.1
