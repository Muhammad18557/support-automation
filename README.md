# support-automation

## Description

This repository contains the code for the support automation project. The project is aimed at automating the support process for defog customers. The reply is sent in the same thread and any subsequent replies from the customer are also replied to with the appropriate response. In such cases, the replier also has the previous conversation history to refer to.

The job runs as an infinite while loop that sleeps for `TIME_INTERVAL` seconds (defined in `main.py`) before checking for new emails to reply. If the latest message is from the customer, the job will reply to the customer with the appropriate response. If the latest reply is from the support, the job will ignore the email and move on to the next one.

Create a `.env` file in the root directory with the following variables (copy the `.env.template` file and fill in the values):

```
OPENAI_API_KEY=
MY_EMAIL_ID=
```

## Installation

```
pip install -r requirements.txt
```

## Usage

```
python main.py
```
