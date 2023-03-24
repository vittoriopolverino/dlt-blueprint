#!/usr/bin/env bash

print_banner() {
  cat 'scripts/banner.txt'
}

install_dependencies() {
  poetry install --sync
}

update_dependencies() {
  poetry update
}

show_dependencies() {
  echo -en '\n Showing installed dependencies . . . \n'
  poetry show
}

pre_commit_hooks() {
  echo -en '\n Installing pre-commit and pre-push hooks . . . \n'
  poetry run pre-commit install --hook-type pre-commit
  poetry run pre-commit install --hook-type pre-push
}

pre_commit_autoupdate() {
  echo -en '\n pre-commit autoupdate . . . \n'
  poetry run pre-commit autoupdate
}

poetry_init() {
  print_banner
  install_dependencies
  update_dependencies
  show_dependencies
  pre_commit_hooks
}

poetry_init

$SHELL
