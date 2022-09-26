#!/bin/bash

export GPG_TTY=$(tty)

GITCONFIG="git config --local"
DEFAULT_KEY=0AF816BB57C0ADAC8BCA0401D295724CD80B0956

$GITCONFIG user.email ${GIT_USER_EMAIL:?GIT_USER_EMAIL is not set}
$GITCONFIG commit.gpgsign true
# $GITCONFIG gpg.format ssh
$GITCONFIG user.signingkey ${GIT_SIGNING_KEY:-$DEFAULT_KEY}
$GITCONFIG gpg.program /usr/local/bin/gpg