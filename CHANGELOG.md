# Changelog
All notable changes to AIDungeon will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [[Unreleased]](https://github.com/AIDungeon/AIDungeon/compare/master...develop)

### Added

- Formal grammars for apocalyptic setting: scavenger, mutant and headhunter contexts/prompts
- 'Finetune the model yourself' section in README.md
- Command line argument `--cpu` which forces use of the CPU instead of a GPU.

### Fixed

- `install.sh` will only use `sudo` if the user is not root
- Fix loading saved games from the title splash to use the new local save path.
- Fix ending punctuation being chopped off of generated text.

## [2.2.0] - 2019-12-19

### Added

- `/reset` is a new command with the same functionality as the
old `/restart`, saving the old and beginning a brand new game.
- Ratings after death and winning
- `get_rating` function to `Story` objects.
- New content in fantasy grammar.
- Formal grammars for peasant and rogue contexts/prompts.

### Removed

- F-strings for python 3.4 and 3.5 compatibility
- Trailing comma in function args for 3.5 compatibility

### Fixed

- Typos in story grammar.
- AI no longer sees `You you` when the user inputs commands beginning with `You` or `I`.
- Some caption issues with actions.

### Changed

- `/restart` now restarts from the beginning of the same game.

## [2.1.1] - 2019-12-17

### Fixed

- Bug preventing `Custom` game setting selection from working.
- Code style.

## [2.1.0] - 2019-12-16

### Added
- This changelog!
- Formal grammars for the noble, knight, and wizard contexts/prompts.
- Better regex logic to detect terminal states.
- Directory `saved_stories`.
- A few more censored words.
- Feedback for user for the censor command.
- iPython notebook utilities to save/load to Google Drive, and an OOM error workaround.
- install.sh now detects python version and fails if it's not supported.
- Issue and PR template improvements.

### Fixed
- Loading not working on `develop`.
- Loading now print properly.
- [No Save Game on Quit for Loaded Games](https://github.com/AIDungeon/AIDungeon/issues/97)
- install.sh no longer tries calling `apt-get` on distributions without it.
- Arch Linux now works with install.sh (with pyenv is used or python3.6 is set as python3).
- A bug that caused game to crash if given an incorrect game ID to load.

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
