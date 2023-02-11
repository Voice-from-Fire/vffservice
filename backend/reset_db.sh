export VFF_RUN_ENV=local
export VFF_INVITATION_CODES=test1 test2
export DB_HOST=db
export DB_USER=postgres
export DB_PASSWORD=postgres
export DB_NAME=voicedb


export PGPASSWORD=postgres
psql -U postgres -h db -c "DROP DATABASE voicedb;"
python3 -m app initdb --create-test-user
