# Opening hours parser and converter

API that receiving opening hours in JSON format and returning
human-readable output.

Example input:

```json
{
  "monday": [
    {
      "type": "open",
      "value": 32400
    },
    {
      "type": "close",
      "value": 72000
    }
  ]
}
```

Example output:
```json
[
  "Monday: 9 AM - 8 PM"
]
```

## How to run project locally

> Required Python version: 3.8

Install requirements:

`pip install -r requirements.txt`

Run dev server:

`make run`

Now API should be available by next URL: http://127.0.0.1:8000

## How to run project using docker-compose

`docker-compose up -d`

Now API should be available by next URL: http://127.0.0.1:8000

## How to test project:

Install dev requirements:

`pip install -r dev_requirements.txt`

Run unit tests:

`make test`

Run linter:

`make lint`

Run static type checker:

`make mypy`

## Example request to API:

Using `curl`:

```
curl -X 'POST' \
  'http://127.0.0.1:8000/convert' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"monday": [], "tuesday": [{"type": "open", "value": 36000}, {"type": "close", "value": 64800}], "wednesday": [], "thursday": [{"type": "open", "value": 36000}, {"type": "close", "value": 64800}], "friday": [{"type": "open", "value": 36000}], "saturday": [{"type": "close", "value": 3600}, {"type": "open", "value": 36000}], "sunday": [{"type": "close", "value": 3600}, {"type": "open", "value": 43200}, {"type": "close", "value": 75600}]}'
```

Using OpenAPI UI:

Open in a browser: http://127.0.0.1:8000/docs#/default/read_item_convert_post
