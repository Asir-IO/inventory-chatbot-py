## What is This
This is an inventory chatbot that translates natural language questions into executable database queries, and then into  a natural language response.

Given a local database, it can accurately answer operational questions about assets, vendors, stock, and much more.

---
## Operation Diagram
Below is the system architecture showing how the LangGraph state machine routes intent, generates SQL, executes queries, and self-corrects errors.
![](assets/operation_diagram.png)

---
## Dependency Requirements
This project requires Python 3.9+ and uses several external libraries. All dependencies are locked in the requirements.txt file.

Key dependencies include:
- langchain & langchain-openai
- langgraph
- python-dotenv
- sqlite3 (Built into Python)

## Setup Instructions
### 1. Set Environment Variables
This project requires an OpenAI API key to run the LLM routing and generation nodes.

1. Create a file named `.env` in the root directory of the project.

2. Add your API key exactly like this:
```
OPENAI_API_KEY=your_api_key_here
```

### 2. Install Dependencies
Open your terminal, navigate to the project folder, and run:

```py
pip install -r requirements.txt
```
### 3. Initialize Database
Before running the bot, you must provide your SQLite database.
replace the `inventory_chatbot.db` file with your own database

---
## Running the Bot/App
To run the terminal-basedbot, execute the following command:
```py
python main.py
```

---
built by Asser =)

