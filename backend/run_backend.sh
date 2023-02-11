export VFF_RUN_ENV=local
export VFF_INVITATION_CODES=test1 test2
export DB_HOST=db
export DB_USER=postgres
export DB_PASSWORD=postgres
export DB_NAME=voicedb
uvicorn app.service:app --reload