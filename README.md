# API service for printing checks

Problem. Let's imagine a chain of delivery restaurants "Pizza & Sushi", which has many points where orders are prepared for customers. Every customer wants to receive a receipt with their order containing detailed information about the order. The kitchen staff also want to receive a receipt, so that in the process of preparing and packing the order, they do not forget to put everything they need.

This service solves this problem. It receives information about the order, generates checks for the printers of the cash register and restaurant kitchen.

### Scheme of the service

![][arch]

### Detailed description

1. The service receives information about a new order, creates checks in the database for all printers of the point specified in the order, and sets asynchronous tasks for generating PDF files for these checks. If the point does not have any printer - returns an error. If receipts for this order have already been created - returns an error.

2. An asynchronous worker generates a PDF file from an HTML template using wkhtmltopdf. The file name has the following form <order ID>_<check type>.pdf (123456_client.pdf). The files are stored in the media/pdf folder at the root of the project.

3. The application polls the service for new checks. The survey takes place in the following way: first, a list of receipts that have already been generated for a specific printer is requested, then a PDF file is downloaded for each receipt and sent for printing.

4. The possibility to filter checks by printer, type and status has been implemented in the admin section

### Technologies used

1. The service is written in python and Django
2. Infrastructure: [PostgreSQL], [Redis], [wkhtmltopdf], run in docker using docker-compose.
3. API - Django REST framework

### Implemented models

1. Printer. Each printer prints only its own type of receipt. The api_key field acquires unique values, it uniquely identifies the printer. Fixtures have been created for this model.

#### To load data:
```
python manage.py loaddata fixtures/model_Printer.json--app printing_checks.Printer
```

| Field      | Type         | Value           | Description                             |
|------------|--------------|-----------------|-----------------------------------------|
| name       | CharField    |                 | name of the printer                     |
| api_key    | CharField    |                 | API access key                          |
| check_type | CharField    | kitchen\|client | type of check printed by a printer      |
| point_id   | IntegerField |                 | the point to which the printer is bound |

2. Check. The order information for each check is stored in JSON.

| Field      | Type         | Value                  | Description                      |
|------------|--------------| -----------------------|----------------------------------|
| printer_id | ForeignKey   |                        | printer                          |
| type       | CharField    | kitchen\|client        | check type                       |
| order      | JSONField    |                        | order information                |
| status     | CharField    | new\|rendered\|printed | check status                     |
| pdf_file   | FileField    |                        | a link to the generated PDF file |

### API

A description of the available methods is contained in the file api.yml (swagger specification).

[wkhtmltopdf]: https://hub.docker.com/r/openlabs/docker-wkhtmltopdf-aas/
[postgresql]: https://hub.docker.com/_/postgres/
[redis]: https://hub.docker.com/_/redis/
[swagger]: https://editor.swagger.io/
[arch]: images/arch.png
