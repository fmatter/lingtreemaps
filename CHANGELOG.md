# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
* `print_labels` (default: true): print language labels on the tree leafs
* `leaf_lw` (default: from pyplot): line width of tree branches
* `connection_lw` (default: 1): line width of the leaf-map connections
* `map_marker_lw` (default: 1): line width of the circles on the map
* `color_tree` (default: false): color the lines leading to colored nodes
* `nonterminal_nodes` (default: false): put circle markers onto proto-notes

### Removed

### Changed
* if proto-nodes are present in the value dataframe, their values can be shown by activating `color_tree` and/or `nonterminal_nodes`

### Fixed

## [0.0.1] - 2022-08-29

Initial release

[Unreleased]: https://github.com/fmatter/lingtreemaps/compare/0.0.1...HEAD
[0.0.1]: https://github.com/fmatter/lingtreemaps/releases/tag/0.0.1
