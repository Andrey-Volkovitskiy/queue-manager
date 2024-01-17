# Queue manager

**A pet project to practice developing a real-life web app from scratch.**

*The queue manager that helps operators serve bank clients in order of appearance.*

Deployed at: https://queue-man.up.railway.app/

- Designed a diagram of the future application, reflecting entities of the domain and their interaction
- Designed a database in 5th normal form
- Implemented the web app using Django, ClassBasdViews and object level permissions (4000 lines of code written)
- The app covered with 141 tests (unit & end-to-end)
- Used complex (20+ lines) database queries through Django ORM
- Reduced the quantity of DB queries per page load by 4 times using DjangoDebugToolbar, select/prefetch_related()
- The code refactored to follow DRY, KISS


---
### Tests and code quality assessment:
[![Pytest (with postgres)](https://github.com/Andrey-Volkovitskiy/queue-manager/actions/workflows/pytest_with_postgres.yml/badge.svg)](https://github.com/Andrey-Volkovitskiy/queue-manager/actions/workflows/pytest_with_postgres.yml)    [![Linter (Flake8)](https://github.com/Andrey-Volkovitskiy/queue-manager/actions/workflows/flake8_linter.yml/badge.svg)](https://github.com/Andrey-Volkovitskiy/queue-manager/actions/workflows/flake8_linter.yml)

[![Maintainability](https://api.codeclimate.com/v1/badges/44bb226bc3cac3d7dfbd/maintainability)](https://codeclimate.com/github/Andrey-Volkovitskiy/queue-manager/maintainability)    [![Test Coverage](https://api.codeclimate.com/v1/badges/44bb226bc3cac3d7dfbd/test_coverage)](https://codeclimate.com/github/Andrey-Volkovitskiy/queue-manager/test_coverage)


---
This project was built using these tools:

| Tool                                                                        | Description                                             |
|-----------------------------------------------------------------------------|---------------------------------------------------------|
| [Django](https://www.djangoproject.com/)         | Web framework  |
| [Django ORM](https://docs.djangoproject.com/en/4.2/topics/db/)         | Database-abstraction API  |
| [PostgreSQL](https://www.postgresql.org)         | Database management system  |
| [Bootstrap](https://getbootstrap.com/)         | CSS framework  |
| [Docker](https://www.docker.com)       | Container-based platform for building apps  |
| [Poetry](https://poetry.eustace.io/)         | Python dependency manager  |
| [Pytest](https://docs.pytest.org/)               | Testing framework |
| [Django Debug Toolbar](https://django-debug-toolbar.readthedocs.io/)      | DB query analysis tool |
| [Flake8](https://flake8.pycqa.org/)               | Linter to check code style |
| [Code Climate](https://codeclimate.com/)               | Clean Code verification system |
| [GitHub Actions](https://github.com/features/actions)               | Continuous Integration (CI) |
| [Railway](https://railway.app)               | Deployment platform |
| [Rollbar](https://rollbar.com/)               | Error logging & tracking service |


---
### Installation and running
The application stores data using PostgresSQL (connected via DATABASE_URL).

- *make install* - to install dependencies
- *make migrate* - to migrate a database
- *make start* - to start the app
- *make dev* - to start app on development web server
- *make test* - to run tests

(more service commands can be found in Makefile)

---
*ER diagram*
![er diagram](https://github.com/Andrey-Volkovitskiy/queue-manager/blob/main/staticfiles/readme/er_diagram.jpg?raw=true)

---

*Examle of a multi-line database query*
![Multi-line DB query](https://github.com/Andrey-Volkovitskiy/queue-manager/blob/main/staticfiles/readme/comlpex_query.jpg?raw=true)

---

*BD query analysis using Django Debug Toolbar*
![Django Debug Toolbar](https://github.com/Andrey-Volkovitskiy/queue-manager/blob/main/staticfiles/readme/django_debug_toolbar.jpg?raw=true)

---

*Error tracking (Rollbar)*
![Error tracking (Rollbar)](https://github.com/Andrey-Volkovitskiy/queue-manager/blob/main/staticfiles/readme/rollbar.jpg?raw=true)
