#!/bin/sh
# msgpost.sh
# change MESSAGE, WEBHOOK and USERNAME as makes sense
# This code is trivial, and not covered by any license or warranty.

# explode on errors
set -e

#WEBHOOK_E2_GENERAL="https://discordapp.com/api/webhooks/532255035141128192/OZYxXHCdlzSXtZAPgP8aBRtsHSuc8yQdXP4sbAZlqYN8BHVqmoY90BTz4ABnp9bkIVej"
#WEBHOOK_TEST_INVITADOS="https://discordapp.com/api/webhooks/530403952752066580/yzWOFFnJidEpQycCrbE-st-5krSrAxAfrMAjOifl2Egsh9xSGK-y4NH-sWnUeWsyxNGM"
WEBHOOK_E2_AVISOS="https://discordapp.com/api/webhooks/532986851037020161/e8zgy2iCIZMS_Xux3iL-6KF_5ylChdmJvI4jXq1pmHasG00BYrK2RhY05ANiZ6qAfITF"


MESSAGE="\@everyone Estamos en horario del reset semanal !! Disfruten de Destiny2 !!"
USERNAME=DEFINITIVO

curl -X POST \
     -F "content=${MESSAGE}" \
     -F "username=${USERNAME}" \
     "${WEBHOOK_E2_AVISOS}"
