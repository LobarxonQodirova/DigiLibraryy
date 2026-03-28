# DigiLibrary - Digital Library Management System

A comprehensive, production-grade digital library management system built with Django, Django REST Framework, React, PostgreSQL, Redis, Celery, and Elasticsearch.

## Features

- **Book Catalog Management** - Full CRUD for books, authors, publishers, genres, and ISBN tracking with cover image support
- **Digital Lending** - E-book licensing, digital loans with automatic expiration, DRM-aware lending
- **Physical Lending** - Book checkouts, returns, renewals, holds, and reservation queues
- **Member Management** - Membership types, profiles, librarian roles, and self-service portal
- **Fine Management** - Automated overdue fine calculation, payment tracking, and waiver workflows
- **Reading Room Booking** - Room and seat reservations with time-slot management
- **Inter-Library Loans (ILL)** - Partner library network, loan requests, and fulfillment tracking
- **Usage Analytics** - Circulation statistics, popular books, member activity, and trend dashboards
- **Catalog Search** - Elasticsearch-powered full-text search with faceted filtering

## Architecture

```
digilibrary/
├── backend/              # Django + DRF API server
│   ├── config/           # Django settings, URLs, WSGI/ASGI, Celery
│   ├── apps/
│   │   ├── accounts/     # User, Librarian, Member, Membership models
│   │   ├── catalog/      # Book, Author, Publisher, Genre, BookCopy
│   │   ├── lending/      # Loan, Reservation, Hold, LoanHistory
│   │   ├── ebooks/       # EBook, EBookLicense, DigitalLoan
│   │   ├── fines/        # Fine, FinePayment
│   │   ├── reading_rooms/# ReadingRoom, Seat, RoomBooking
│   │   ├── interlibrary/ # ILLRequest, PartnerLibrary
│   │   └── analytics/    # Analytics services and endpoints
│   └── utils/            # Shared pagination, exceptions
├── frontend/             # React SPA
│   ├── src/
│   │   ├── api/          # Axios API clients
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # Route-level page components
│   │   ├── store/        # Redux store and slices
│   │   ├── hooks/        # Custom React hooks
│   │   └── styles/       # Global CSS
│   └── public/           # Static HTML entry point
├── nginx/                # Reverse proxy configuration
├── docker-compose.yml    # Full stack orchestration
└── .env.example          # Environment variable template
```

## Prerequisites

- Docker and Docker Compose v2+
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

## Quick Start

1. **Clone and configure environment:**

```bash
cp .env.example .env
# Edit .env with your settings
```

2. **Start all services with Docker Compose:**

```bash
docker-compose up --build -d
```

3. **Run database migrations and create a superuser:**

```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

4. **Rebuild the Elasticsearch index:**

```bash
docker-compose exec backend python manage.py search_index --rebuild
```

5. **Access the application:**

| Service           | URL                          |
|-------------------|------------------------------|
| Frontend (React)  | http://localhost              |
| API               | http://localhost/api/         |
| Admin Panel       | http://localhost/admin/       |
| API Documentation | http://localhost/api/docs/    |
| Flower (Celery)   | http://localhost:5555         |

## Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm start
```

### Running Celery Workers

```bash
cd backend
celery -A config worker -l info
celery -A config beat -l info
```

## API Endpoints

| Endpoint                     | Method | Description                      |
|------------------------------|--------|----------------------------------|
| `/api/auth/login/`           | POST   | Obtain JWT token pair            |
| `/api/auth/register/`        | POST   | Register new member              |
| `/api/catalog/books/`        | GET    | List/search books                |
| `/api/catalog/books/{id}/`   | GET    | Book detail                      |
| `/api/lending/loans/`        | GET    | List loans                       |
| `/api/lending/loans/checkout/`| POST  | Checkout a book                  |
| `/api/lending/reservations/` | GET    | List reservations                |
| `/api/ebooks/`               | GET    | List e-books                     |
| `/api/ebooks/{id}/borrow/`   | POST   | Borrow digital copy              |
| `/api/fines/`                | GET    | List fines                       |
| `/api/fines/{id}/pay/`       | POST   | Pay a fine                       |
| `/api/reading-rooms/`        | GET    | List reading rooms               |
| `/api/reading-rooms/book/`   | POST   | Book a room/seat                 |
| `/api/ill/requests/`         | GET    | List ILL requests                |
| `/api/analytics/dashboard/`  | GET    | Analytics dashboard data         |
| `/api/members/`              | GET    | List members (staff only)        |

## Environment Variables

See `.env.example` for a complete list of configurable environment variables covering database connections, Redis, Elasticsearch, email, and JWT settings.

## Testing

```bash
# Backend tests
docker-compose exec backend python manage.py test

# Frontend tests
docker-compose exec frontend npm test
```

## License

MIT License. See LICENSE file for details.
