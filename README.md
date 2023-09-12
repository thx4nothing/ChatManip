# ChatManip

Welcome to **ChatManip**! This Python project provides tools to manipulate chat conversations in
various ways.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setting Up the Project with Docker](#setting-up-the-project-with-docker)
- [Installation without Docker](#installation-without-docker)
- [License](#license)

## Prerequisites

Before you get started, make sure you have the following software installed on your machine:

- Python (version 3.11 or higher)
- Git (for cloning the repository)

## Setting Up the Project with Docker

Follow these steps to set up and run the project using Docker:

### Prerequisites

Before you begin, make sure you have the following prerequisites installed on your system:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/) (optional)

### Step 1: Clone the Repository

   ```bash
   git clone https://github.com/thx4nothing/ChatManip.git
   cd ChatManip
   ```

### Step 2: Build the Docker Image

   ```bash
   docker build -t chatmanip .
   ```

### Step 3: Environment Variables

When running the Docker container for the `chatmanip` application, you can customize its behavior by
setting the following environment variables:

- **CHATMANIP_DEBUG:** This environment variable controls the debugging mode of the `chatmanip`
  application. Setting it to `0` (as in `-e "CHATMANIP_DEBUG=0"`) typically means turning off
  debugging or setting the application to run in production mode. Debugging mode may provide
  additional information (FastAPI docs/redocs) for development and troubleshooting but should be
  turned off in a production environment.

- **OPENAI_API_KEY:** To access the OpenAI API, the `chatmanip` application requires an API key. You
  should replace `<APIKEY>` in the command with your actual OpenAI API key. This key is essential
  for making requests to the OpenAI ChatGPT API, enabling the application to generate responses and
  interact with the OpenAI service.

- **CHATMANIP_ADMIN_TOKEN:** This environment variable specifies an admin password for
  authentication and authorization purposes within the `chatmanip` application. You should
  replace `<PASSWORD>` in the command with the actual admin password you want to use. The admin
  token is often used to protect certain routes or functionality that should only be accessible to
  authorized users.

These environment variables allow you to configure and secure your `chatmanip` application when
running it in a Docker container. Ensure that you replace the placeholder values (`<APIKEY>`
and `<PASSWORD>`) with your specific API key and admin token for your application to function
correctly and securely.

### Step 4: Run the Docker Container

You can run the Docker container using either docker run or docker-compose. Choose one of the
following options based on your setup:

Option 1: Using docker run

   ```bash
  docker run -d -p 8000:8000 -e "CHATMANIP_DEBUG=0" -e "OPENAI_API_KEY=<APIKEY>" -e "CHATMANIP_ADMIN_TOKEN=<PASSWORD>" chatmanip
   ```

Option 2: Using docker-compose

If you edited the docker-compose.yml file, simply run:

```bash
docker-compose up -d
```

## Installation without Docker

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/thx4nothing/ChatManip.git
   cd ChatManip
   ```

2. Create a virtual environment (recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate    # On Windows: venv\Scripts\activate
   ```

3. Install project dependencies:

    ```bash
    pip install -r requirements.txt
   ```

Before you can start using **ChatManip**, you need to set up your OpenAI API key as an environment
variable. This API key is required for interacting with OpenAI's language models.

### Setting Up the OpenAI API Key

1. **Get Your OpenAI API Key**: If you don't have an OpenAI API key, you can sign up for one
   at [OpenAI's website](https://openai.com/). Once you have your API key, keep it secure and do not
   share it publicly.

2. **Set the Environment Variable**:

    - On Unix/Linux/MacOS:
      Open your terminal and enter the following command, replacing `YOUR_API_KEY_HERE` with your
      actual OpenAI API key:

      ```bash
      export OPENAI_API_KEY=YOUR_API_KEY_HERE
      ```

    - On Windows (Command Prompt):
      Open Command Prompt and enter the following command, replacing `YOUR_API_KEY_HERE` with your
      actual OpenAI API key:

      ```bash
      set OPENAI_API_KEY=YOUR_API_KEY_HERE
      ```

    - On Windows (PowerShell):
      Open PowerShell and enter the following command, replacing `YOUR_API_KEY_HERE` with your
      actual OpenAI API key:

      ```bash
      $env:OPENAI_API_KEY="YOUR_API_KEY_HERE"
      ```

3. **Verify the Setup**:
   To ensure that the environment variable is set correctly, you can run the following command in
   your terminal or command prompt:

   ```bash
   echo $OPENAI_API_KEY    # Unix/Linux/MacOS
   echo %OPENAI_API_KEY%   # Windows (Command Prompt)
   echo $env:OPENAI_API_KEY  # Windows (PowerShell)
   ```

### Starting the webserver

1. Start the webserver
    ```bash
    python -m uvicorn api_server.main:app
   ```

2. ChatManip provides a webserver at the local address: http://127.0.0.1:8000

3. The admin panel is accessible via http://127.0.0.1:8000/admin/?token=1234
   (The token is hardcoded in the code and will be changeable in later versions.)

## License

This project is licensed under the GPL-3.0 License.