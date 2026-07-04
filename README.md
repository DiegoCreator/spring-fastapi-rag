<h1 align="center">Spring-FastAPI-RAG</h1>

A project integrating Spring Boot (as a backend) and FastAPI (as an AI-enabled service) with a PostgreSQL + pgvector database to create a RAG system.

This project is a learning exercise for experimenting with RAG architecture and service-to-service communication.

* **Who is it for?**

Developers learning RAG systems

for experimenting with Spring + FastAPI integration

Anyone interested in vector databases and AI-powered applications

* **What is RAG?**

RAG (Retrieval-Augmented Generation) is a technique that allows language models (such as GPT, Llama, or Claude) to use your own private data that the model has not seen during the training process.

### 1. Project status

The project is **completed**. All core features of the RAG pipeline, service communication, and frontend interface have been successfully implemented and tested.

### 2. Architecture
 
The system is based on microservices:

* **Spring Boot:** Manages core business logic and user communication. It serves as an API Gateway/Orchestrator that receives requests from the frontend, routes them to FastAPI for specialized processing, and returns the final response to the user.

* **FastAPI:** Serves as the core application backend and AI engine. Beyond handling heavy AI operations, it manages the core business logic, including file upload, and CRUD operations for chats and documents (fetching, deleting, and renaming).

* **PostgreSQL + pgvector:** A database storing vectors for semantic search.

* **frontend:** Visual and interactive layer of the application 

* **Project tree:**

/spring-app

/fastapi-service

/frontend

docker-compose.yml

### 3. Technology stack

* **Backend:** Java 21+, Spring Boot 4.x

* **AI Service:** Python 3.14, FastAPI

* **Database:** PostgreSQL with the pgvector extension

* **Frontend:** Basic HTML, CSS and JS

### 4. AI Models

The system uses different models for generation, chat management, and embeddings:

| Purpose | Model |
|----------|--------|
| Response Generation | Gemini 2.5 Flash |
| Chat Title Generation | Gemini 2.5 Flash Lite |
| Embeddings | all-MiniLM-L6-v2 (Sentence Transformers) |

The embedding model runs locally inside the FastAPI service and generates vector representations that are stored in PostgreSQL.

The Gemini models are used for answer generation and chat management and automatic chat title generation.

### 5. Knowledge Base

This project uses a simple RAG pipeline where users can upload text files through the frontend.

Uploaded files are stored in the database and become available to the AI assistant until they are removed.

The repository includes a sample file in `uploads` folder so the project can be tested immediately after setup.

You can also upload your own .txt, .pdf, .docx, and .md files from the UI to create a custom knowledge base.

### 6. How to start the project

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

* **Frontend:**  Builds from a third Dockerfile (Frontend environment configuration).

* **PostgreSQL:** A database instance with the pgvector extension is automatically launched.

* **Networking:** The containers are connected to a single network, allowing communication between Spring and FastAPI to work out of the box.

### 7. API testing

For the commands to work, you need to start the FastAPI service and the Spring boot service.

* **Using `cURL`:**

#### Ask a question

```bash
curl -X POST http://localhost:8080/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "What is FastAPI?", "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"}'
```

#### Upload a document

```bash
curl -X POST http://localhost:8080/api/upload \
     -F "file=@yourfile"
```

#### List uploaded documents

```bash
curl -X GET http://localhost:8080/api/documents 
```

#### Delete a document

```bash
curl -X DELETE http://localhost:8080/api/documents/{document_id} 
```

#### Rename a chat

```bash
curl -X PUT http://localhost:8080/api/chat/session/{session_id}?title=example 
```

* **using the frontend:**

1. Run the app and enter the frontend: http://localhost:3000.

For a complete list of available endpoints, visit:

* Spring Boot Swagger UI: http://localhost:8080/swagger-ui.html

### 8. Key Features

* **Multi-service Architecture:** Seamless communication between Spring Boot and FastAPI.

* **Advanced Document Processing:** Full ETL pipeline with chunking and embedding generation for `.txt`, `.pdf`, `.docx`, and `.md` files

* **Vector Search:** Powered by PostgreSQL and the `pgvector` extension.

* **Contextual AI:** Integrated with Gemini API, featuring full conversation memory and chat management (including chat renaming).

* **Developer Friendly:** Fully documented with Swagger/OpenAPI for both services and easily containerized via Docker Compose.

### 9. License

This project is open-source and available under the MIT License.