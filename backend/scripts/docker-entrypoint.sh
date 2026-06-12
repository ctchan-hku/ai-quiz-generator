#!/bin/sh
set -eu

SECRETS_FILE="/run/secrets/.env"

if [ -f "$SECRETS_FILE" ]; then
  set -a
  # shellcheck disable=SC1090
  . "$SECRETS_FILE"
  set +a
fi

exec "$@"
