<h1 align="center">Spring-FastAPI-RAG (WIP)</h1>

A project integrating Spring Boot (as a backend) and FastAPI (as an AI-enabled service) with a PostgreSQL + pgvector database to create a RAG system.

This project is a learning exercise for experimenting with RAG architecture and service-to-service communication.

* **Who is it for?**

for developers learning RAG systems

for experimenting with Spring + FastAPI integration

* **What is RAG?**

RAG (Retrieval-Augmented Generation) is a technique that allows language models (such as GPT, Llama, or Claude) to use your own private data that the model has not seen during the training process.

### 1. Project status

The project is under active development.

* **Ready:** Communication between services (Spring <-> FastAPI), connection to the pgvector database, possibility of using the `/ask` endpoint.

* **Under construction:** Integration with LLM, document processing (chunking/embedding), ingestion, frontend, logging + monitoring

### 2. Architecture

The system is based on microservices:

* **Spring boot:** Manages business logic and user communication.

* **FastAPI:** Responsible for heavy AI operations.

* **PostgreSQL + pgvector:** A database storing vectors for semantic search.

* **Project tree:**

/spring-app

/fastapi-service

docker-compose.yml

### 3. Technology stack

* **Backend:** Java 21+, Spring Boot 4.x

* **AI Service:** Python 3.14, FastAPI

* **Database:** PostgreSQL with the pgvector extension

### 4. How to start the project

The easiest way to get the whole system up and running is to use Docker Compose.

1. **Requirements:**

* `Docker` and `Docker Compose` installed.

2. **Get Gemini API Key:**

* Go to https://aistudio.google.com/prompts/new_chat

* Create a new API Key.

* Copy the key for the next step.

3. **Environment configuration:**

The project requires defining environment variables for the database.

* In the main project directory, create an .env file based on the example:

```bash
cp .env.example .env
```

* Open the .env file in an editor and fill in the DB_USER, DB_PASSWORD, DB_NAME, DATABASE_URL and GOOGLE_API_KEY values ​​with your own data.

4. **Run the project:**

In the main project directory, execute the command:

```bash
docker-compose up --build
```

5. **What gets started**

* **Service A (Spring Boot):** Builds from a first Dockerfile (Java environment configuration).

* **Service B (FastAPI):** Builds from a second Dockerfile (Python environment configuration).

* **PostgreSQL:** A database instance with the pgvector extension is automatically launched.

* **Networking:** The containers are connected to a single network, allowing communication between Spring and FastAPI to work out of the box.

### 5. API testing

After running the application using docker-compose, you can test communication with the RAG system by sending a request to the `/ask` endpoint.

* **Using `cURL`:**

```bash
curl -X POST http://localhost:8080/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "What is FastAPI?"}'
```

### 6. Roadmap

* [x] Integration with a specific LLM provider (e.g. OpenAI / Ollama).

* [] Implementation of a document processing pipeline (ETL).

* [] Add Swagger/OpenAPI documentation for both services.


### 7. License

This project is open-source and available under the MIT License.