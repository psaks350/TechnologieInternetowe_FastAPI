# Zbiorcze Laboratoria (Docker Umbrella)

Ten projekt agreguje 6 niezależnych aplikacji (Library, Shop, Movies, Kanban, Notes, Blog) i pozwala uruchomić je wszystkie jedną komendą.

## Wymagania
- **Git**
- **Docker Desktop** (lub Docker Engine)
- **Docker Compose v2.20+** (wymagane do obsługi funkcji `include`)

## Uruchomienie
- **Klon REPO** — `git clone https://github.com/psaks350/TechnologieInternetowe_FastAPI.git`
- **Wejdź do katalogu projektu:** — `cd TechnologieInternetowe_FastAPI`
- **Będąc w głównym katalogu, uruchom wszystkie projekty z przebudowaniem obrazów:** — `docker compose up --build`

## Dostęp do aplikacji
- Po uruchomieniu, każda aplikacja jest dostępna pod unikalnym portem:

Projekt	        Frontend                Backend (API / Swagger)
Lab 01: Library	http://localhost:8080	http://localhost:8000/docs
Lab 02: Shop	http://localhost:8081	http://localhost:8001/docs
Lab 03: Blog	http://localhost:8082	http://localhost:8002/docs
Lab 04: Movies	http://localhost:8083	http://localhost:8003/docs
Lab 05: Kanban	http://localhost:8084	http://localhost:8004/docs
Lab 06: Notes	http://localhost:8085	http://localhost:8005/docs

## Zatrzymywanie i czyszczenie
- **Aby zatrzymać wszystkie serwisy:** — `docker compose down`