# Endpoints

## Authentication

### `POST /auth`

#### Request

```json
{
  "email": "email@email.com",
  "password": "password"
}
```

#### Responses

##### `200 OK`

```json
{
  "token": "long-random-string"
}
```

##### `400 BAD REQUEST`

```json
{
  "detail": "Information on malformed request"
}
```

## Users

### `GET /users/me`

#### Responses

##### `200 OK`

```json
{
  "email": "email@email.com",
  "first_name": "George",
  "last_name": "Costanza"
}
```

## Foods

### `GET /foods`

#### URL Parameters

* `name`: Partial or full name of the food

#### Responses

##### `200 OK`

```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "name": "Food Name",
      "calories": 100,
      "protein": 24,
      "carbohydrates": 29,
      "fats": 73
    }
  ]
}
```

### `GET /foods/:id`

#### Responses

##### `200 OK`

```json
{
  "id": 1,
  "name": "Food Name",
  "calories": 100,
  "protein": 24,
  "carbohydrates": 29,
  "fats": 73
}
```

### `POST /foods`

#### Request

```json
{
  "name": "Another Food",
  "calories": 100,
  "protein": 24,
  "carbohydrates": 29,
  "fats": 73
}
```

#### Responses

##### `201 CREATED`

```json
{
  "name": "Another Food",
  "calories": 100,
  "protein": 24,
  "carbohydrates": 29,
  "fats": 73
}
```

## Food Logs

### `GET /logs`

#### URL Parameters

* `before`: ISO date to search for logs before.
* `after`: ISO date to search for logs after.

#### Responses

##### `200 OK`

```json
{
  "count": 14,
  "results": [
    {
      "id": 1,
      "date": "2019-01-01",
      "entries": 4
    },
    ...
  ]
}
```

### `GET /logs/:id`

#### Responses

##### `200 OK`

```json
{
  "id": 1,
  "date": "2019-01-01",
  "calories": 1780,
  "protein": 89,
  "carbohydrates": 28,
  "fats": 19,
  "water": 6,
  "meals": [
    {
      "timestamp": "2019-09-19T21:19:00+00:00",
      "food": {
        "id": 1,
        "calories": 100,
        "protein": 24,
        "carbohydrates": 29,
        "fats": 73
      }
    },
    ...
  ]
}
```

### `POST /logs`

#### Request

```json
{
  "date": "2019-01-01"
}
```

#### Responses

##### `400 BAD REQUEST`

```json
{
  "detail": "Daily log already exists"
}
```

##### `200 OK`

```json
{
  "id": 2,
  "date": "2019-01-01"
}
```

### `DELETE /logs/:id`

#### Responses

##### `200 OK`

### `POST /logs/:id/meals`

#### Request

```json
{
  "timestamp": "2019-09-19T21:19:00+00:00",
  "food": 1
}
```

#### Responses

##### `200 OK`

```json
{
  "timestamp": "2019-09-19T21:19:00+00:00",
  "food": {
    "id": 1,
    "calories": 100,
    "protein": 24,
    "carbohydrates": 29,
    "fats": 73
  }
}
```

### `DELETE /logs/:id/meals`

#### Responses

##### `200 OK`
