# exchange-rate-service
This service provides real-time exchange rate conversions using an external API for currency rates.
It leverages Docker for environment consistency and Makefile commands for easy setup and management.
## Prerequisites
    Docker: Ensure Docker is installed on your system. This service runs in a containerized environment.
    Make: For streamlined management, using Makefile commands is recommended.


  ## Environment Configuration

  1. Copy the `.env.dev` file (example environment configuration) to a `.env` file in the root directory:

      ```bash
      cp .env.dev .env
      ```

  2. Open the `.env` file and add your environment variables as needed. In particular, set your `FREECURRENCYAPI_KEY`, which you can obtain from [Free Currency API](https://app.freecurrencyapi.com).

      ```plaintext
      # .env
      FREECURRENCYAPI_KEY=your_api_key_here
      ```

  3. After configuring the `.env` file, start and stop the service with the following commands:

      - **Start the service**:
          ```bash
          make run
          ```

      - **Stop the service**:
          ```bash
          make down
          ```
## Tooling

This project utilizes a range of tools and libraries designed to streamline development and enhance performance:

- **UV**: We use `uv` instead of the traditional `pip` for dependency management. It's fast and eliminates the need for a `requirements.txt` file, simplifying package management.

- **Docker and Docker Compose**: For local development, Docker Compose manages our services seamlessly. The Dockerfile is production-ready, so you can set up a CI/CD pipeline and deploy to your preferred server.

- **FastAPI**: Chosen for its simplicity and efficiency, FastAPI powers the API layer of this service. It’s an easy-to-use, high-performance framework that I personally enjoy working with.
3
- **WebSockets Library**: Provides support for handling WebSocket connections, allowing real-time data flows.

- **Pydantic**: This library validates inputs and outputs, ensuring data integrity throughout the service. For environment variables, we rely on `pydantic-settings` to validate the `.env` configuration file.

- **Free Currency API**: This project uses the [Free Currency API](https://app.freecurrencyapi.com) for exchange rate data, which includes a simple SDK for easy integration.


## Architecture

The architecture follows a classic microservices approach with **Redis** as a caching layer. The core components include:

- **WebSocketClient**: This client manages real-time WebSocket connections and is initialized using FastAPI's `lifespan`. It handles the service's primary exchange rate functionality. Connections are managed asynchronously for performance and efficiency.

- **Redis and FreeCurrencyAPI Clients**: Each external dependency (Redis and Free Currency API) is defined in its own client file, ensuring clear dependency management and responsibility isolation. Redis uses an **asynchronous connection pool** for optimized handling of concurrent requests.

- **Asynchronous Setup**: Efforts have been made to keep all relevant functions asynchronous, enhancing performance where it makes sense. For example, the WebSocket client setup uses an `@asynccontextmanager`, which ensures the connection is initialized and closed gracefully:

- **Caching**: Exchange rate data is cached for **2 hours**, set as a hardcoded TTL for each cache entry in Redis. The TTL and other constants are centralized in `src/exchange_rate/config.py` for easy access and configuration.


## Testing

Currently, there are no implemented tests due to time constraints. An initial attempt was made to set up unit tests, but challenges with configuring `PYTHONPATH` for module imports in `pytest` prevented completion.

### Planned Testing Approach

If work continues on this project, testing would focus on:

1. **Unit Tests**: Primarily for `conversion_service.py`, to validate core functionalities.
2. **Integration Tests**: Using [Testcontainers](https://testcontainers.com/) for temporary, isolated testing environments, including:
   - **Redis**: Ensuring cache interactions are handled as expected.
   - **Free Currency API**: Mocking responses to test API integrations.
   - **WebSocket**: Creating a fake WebSocket server to simulate connections and message handling.

### Performance Testing

The current setup hasn't undergone stress testing to verify handling of tens of requests per second. For now, we rely on FastAPI's performance capabilities to handle this load.
