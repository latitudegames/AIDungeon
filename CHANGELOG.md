# Changelog
All notable changes to AIDungeon will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- This changelog!
- Formal grammars for the noble and knight contexts/prompts.
- Better regex logic to detect terminal states.
- Directory `saved_stories`.
- A few more censored words.
- Feedback for user for the censor command.
- iPython notebook utilities to save/load to Google Drive, and an OOM error workaround.

### Fixed
- Loading not working on `develop`.
- [No Save Game on Quit for Loaded Games](https://github.com/AIDungeon/AIDungeon/issues/97)

### Changed
- Made `install.sh` more robust.
- Sorted imports.
- Split the model downloading script into `download_model.sh` from `install.sh`.
- User commands are now case-insensitive.
- User commands are now denoted with the prefix `/`.

## [2.0.0] - 2019-12-05

### Added
- AIDungeon 2, which allows players to type in any desired action.

## [1.0.0] - ?

### Added
- AiDungeon Classic, which gives players action options to choose from.
