# VFF service


## Development

Start dev container

### Backend

Installation

```
$ cd backend
$ python3 -m app initdb --create-test-user
```

Start

```
$ sh run_backend.sh
```

### Frontend

Installation

```
$ cd frontend
$ npm upgrade npm
$ sh generate.sh ## Backend has to be running for this!
$ npm install
```

Start

```
npm run start
```

