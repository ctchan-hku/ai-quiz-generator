#!/bin/sh
set -eu

if [ -f "/run/secrets/deposit/.env" ]; then
  SECRETS_FILE="/run/secrets/deposit/.env"
elif [ -f "/run/secrets/.env" ]; then
  SECRETS_FILE="/run/secrets/.env"
else
  SECRETS_FILE=""
fi

if [ -n "$SECRETS_FILE" ]; then
  set -a
  # shellcheck disable=SC1090
  . "$SECRETS_FILE"
  set +a
fi

exec "$@"
