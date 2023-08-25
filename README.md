# ChatManip

Welcome to **ChatManip**! This Python project provides tools to manipulate chat conversations in
various ways.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

Before you get started, make sure you have the following software installed on your machine:

- Python (version 3.11 or higher)
- Git (for cloning the repository)

## Installation

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/thx4nothing/ChatManip.git
   cd ChatManip

2. Create a virtual environment (recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate    # On Windows: venv\Scripts\activate

3. Install project dependencies:

    ```bash
    pip install -r requirements.txt

## Usage

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

### Starting the webserver

1. Start the webserver
    ```bash
    python -m uvicorn api_server.main:app

2. ChatManip provides a webserver at the local address: http://127.0.0.1:8000

3. The admin panel is accessible via http://127.0.0.1:8000/admin/?token=1234
   (The token is hardcoded in the code and will be changeable in later versions.)

## License

This project is licensed under the GPL-3.0 License.