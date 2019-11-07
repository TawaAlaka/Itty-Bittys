# Endpoints

## Authentication

Endpoints associated with authenticating the user.

### `POST /auth`

Request an authorization token.

#### Request

```json
{
  "email": "email@email.com",
  "password": "password"
}
```

#### Responses

##### `200 OK`

Successful authentication response. Place this in the `Authorization` header on each subsequent request as a `Bearer` token type.

`Authorization: Bearer long-random-string`

 If this is not set on authenticated routes, then a `403` error will be returned.

```json
{
  "token": "long-random-string"
}
```

##### `400 BAD REQUEST`

There are two possible results that could lead to a `400` error.
* Incorrect username and password combination.
* Email is not a valid email.

```json
{
  "detail": "Information on malformed request",
  "email": ["Not a valid email"]
}
```

## Registration

Endpoint for creating a new user.

### `POST /registration`

Create a new user with the given registration information.

#### Request

```json
{
  "email": "email@email.com",
  "first_name": "George",
  "last_name": "Costanza",
  "password": "password",
  "age": 30,
  "weight": 150,
  "birth_date": "2019-01-01"
}
```

#### Responses

##### `200 OK`

Same as the login response string.

```json
{
  "token": "really-long-string"
}
```

##### `400 BAD REQUEST`

Bad request can happen if the email is already in use, or if the request was malformed.

```json
{
  "detail": "Bad message",
  "email": ["Email already in use"]
}
```

## Users

Endpoints associated with user information.

### `GET /users/me`

Retrieve information about the currently authenticated user.

#### Responses

##### `200 OK`

```json
{
  "email": "email@email.com",
  "first_name": "George",
  "last_name": "Costanza",
  "info": {
    "age": 30,
    "weight": 150,
    "birth_date": "2019-01-01"
  },
  "conditions": [
    {
      "id": 1,
      "name": "Diabetes"
    }
  ]
}
```

### `PUT /users/me`

Update information about the current user.

#### Request

```json
{
  "email": "email@gmail.com",
  "first_name": "George",
  "last_name": "Costanza",
  "info": {
    "age": 30,
    "weight": 140
  },
  "conditions": [
    {
      "id": 1,
      "name": "Diabetes"
    },
    {
      "id": 2,
      "name": "High Blood Pressure"
    }
  ]
}
```

#### Responses

##### `200 OK`

```json
{
  "email": "email@gmail.com",
  "first_name": "George",
  "last_name": "Costanza",
  "info": {
    "age": 30,
    "weight": 140
  },
  "conditions": [
    {
      "id": 1,
      "name": "Diabetes"
    },
    {
      "id": 2,
      "name": "High Blood Pressure"
    }
  ]
}
```

## Conditions

### `GET /conditions`

List chronic condition choices.

#### URL Parameters

* `name`: Full or parial name of the condition.

#### Responses

##### `200 OK`

```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "name": "Diabetes"
    }
  ]
}
```

### `POST /conditions`

Create a new condition.

#### Request

```json
{
  "name": "Diabetes"
}
```

#### Response

##### `201 CREATED`

```json
{
  "id": 2,
  "name": "Diabetes",
}
```

##### `400 BAD REQUEST`

Would happen if a condition with the name already exists.

```json
{
  "detail": "Unique name constraint"
}
```

### `GET /conditions/:id`

Get a condition by it's ID.

#### Response

##### `200 OK`

Return the condition associate with the ID.

```json
{
  "id": 2,
  "name": "Diabetes",
}
```

###### `404 NOT FOUND`

Condition with the ID does not exist.

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

Get food by its ID.

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

Create a new food.

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

## Temporary Ailments

### `GET /ailments`

List the currently stored temporary ailments.

#### URL Parameters

* `name`: Partial or full name of the ailment.

#### Responses

##### `200 OK`

```json
{
  "count": 4,
  "results": [
    {
      "id": 1,
      "name": "Headache"
    },
    {
      "id": 2,
      "name": "Lightheadedness"
    },
    ...
  ]
}
```

### `GET /ailments/:id`

Retrieve an ailment by it's ID.

#### Responses

##### `200 OK`

```json
{
  "id": 1,
  "name": "Headache"
}
```

##### `404 NOT FOUND`

Ailment with the given ID does not exist.

### `POST /ailments`

Create a new ailment.

#### Request

```json
{
  "name": "Ailment"
}
```

#### Responses

##### `200 OK`

```json
{
  "id": "4",
  "name": "Ailment"
}
```

##### `400 BAD REQUEST`

Happens if an ailment with the current name already exists.

```json
{
  "name": ["Name already exists"]
}
```

## Logs

### `GET /logs`

#### URL Parameters

* `before`: ISO date (`2020-01-01`) to search for logs before.
* `after`: ISO date (`2020-01-01`) to search for logs after.

#### Responses

##### `200 OK`

```json
{
  "count": 14,
  "results": [
    {
      "id": 1,
      "date": "2019-01-01",
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
      "time": "BREAKFAST",
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

Create a new daily log.

#### Request

```json
{
  "date": "2019-01-01"
}
```

#### Responses

##### `400 BAD REQUEST`

Would happen if a log with the given date already exists.

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

Delete a log and it's associated objects.

#### Responses

##### `200 OK`

### `POST /logs/:id/meals`

Create a meal that relates to a particular log.

#### Request

```json
{
  "time": "BREAKFAST",
  "food": 1
}
```

#### Responses

##### `200 OK`

```json
{
  "id": 2,
  "time": "BREAKFAST",
  "food": {
    "id": 1,
    "calories": 100,
    "protein": 24,
    "carbohydrates": 29,
    "fats": 73
  }
}
```

## Meals

### `POST /meals`

Create meal for a particular user.

#### Request

```json
{
  "log": 3,
  "time": "LUNCH",
  "food": 6
}
```

#### Responses

##### `200 OK`

```json
{
  "id": 7,
  "log": {
    "id": 3,
    "date": "2019-01-01"
  },
  "food": {
    "id": 6,
    "name": "berries",
    "calories": 100,
    "protein": 24,
    "carbohydrates": 29,
    "fats": 73
  }
}
```

##### `400 BAD REQUEST`

Happens if the food does not exist, if the log does not exist, or if the log does belong to the user creating the meal.

```json
{
  "log": ["Log does not exist"],
  "food": ["Food does not exist"]
}
```

### `GET /meals/:id`

Retrieve a particular meal by ID.

#### Response

##### `200 OK`

```json
{
  "id": 7,
  "log": {
    "id": 3,
    "date": "2019-01-01"
  },
  "food": {
    "id": 6,
    "name": "berries",
    "calories": 100,
    "protein": 24,
    "carbohydrates": 29,
    "fats": 73
  }
}
```

##### `404 NOT FOUND`

Meal does not exist.

```json
{
  "detail": "Not found"
}
```

##### `403 FORBIDDEN`

Tried to retrieve a meal that does not belong to the user.

```json
{
  "detail": "Forbidden"
}
```

## Tickets

These are errors that the application needs to report back to the system administrators for review.

### `POST /tickets`

Create a ticket.

#### Request

```json
{
  "message": "Something broke"
}
```

#### Responses

```json
{
  "id": 1,
  "message": "Something broke",
  "created_on": "2019-10-10T22:12:55+00:00"
}
```

### `GET /tickets`

List tickets associated with the authenticated user.

#### Responses

##### `200 OK`

```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "message": "Something broke",
      "created_on": "2019-10-10T22:12:55+00:00"
    }
  ]
}
```

### `GET /tickets/:id`

Retrieve a particular ticket by ID.

#### Responses

##### `200 OK`

```json
{
  "id": 1,
  "info": "Something broke",
  "timestamp": "2019-10-10T22:12:55+00:00"
}
```

##### `403 FORBIDDEN`

This occurs when the user tryies to retrieve a ticket ID they're not associated with.

```json
{
  "detail": "Forbidden"
}
```

##### `404 NOT FOUND`

When the ticket with the ID doesn't exist.

```json
{
  "detail": "Not found"
}
```
