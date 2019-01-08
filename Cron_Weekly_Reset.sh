#!/bin/sh
# msgpost.sh
# change MESSAGE, WEBHOOK and USERNAME as makes sense
# This code is trivial, and not covered by any license or warranty.

# explode on errors
set -e

WEBHOOK="https://discordapp.com/api/webhooks/532255035141128192/OZYxXHCdlzSXtZAPgP8aBRtsHSuc8yQdXP4sbAZlqYN8BHVqmoY90BTz4ABnp9bkIVej"


MESSAGE="\@everyone Estamos en horario del reset semanal !! Disfruten de Destiny2 !!"
USERNAME=DEFINITIVO

curl -X POST \
     -F "content=${MESSAGE}" \
     -F "username=${USERNAME}" \
     "${WEBHOOK}"
