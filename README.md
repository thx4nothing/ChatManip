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

1. Start the webserver
    ```bash
    python -m uvicorn api_server.main:app

2. ChatManip provides a webserver at the local address: http://127.0.0.1:8000

3. The admin panel is accessible via http://127.0.0.1:8000/admin/?token=1234
   (The token is hardcoded in the code and will be changeable in later versions.)

## License

This project is licensed under the GPL-3.0 License.