KBASE_ENDPOINT=https://ci.kbase.us/services/ \
ORCID_CLIENT_ID=${ORCID_CLIENT_ID} \
ORCID_CLIENT_SECRET=${ORCID_CLIENT_SECRET} \
MONGO_HOST=mongo \
MONGO_PORT=27017 \
MONGO_DATABASE=orcidlink \
MONGO_USERNAME=${MONGO_USERNAME} \
MONGO_PASSWORD=${MONGO_PASSWORD} \
DEV=yes \
docker compose -f docker-compose-dev.yml run orcidlink bash