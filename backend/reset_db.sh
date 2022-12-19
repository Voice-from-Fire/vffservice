export PGPASSWORD=postgres
psql -U postgres -h db -c "DROP DATABASE voicedb;"
python3 -m app initdb