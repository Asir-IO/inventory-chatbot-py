import os
import dotenv
from agent.graph import app
from langchain_core.messages import HumanMessage

# Load environment variables (API keys)
dotenv.load_dotenv()

def main():
    print("\n" + "="*50)
    print("Inventory Chatbot Initialized.")
    print("Type 'quit', 'exit', or 'q' to stop.")
    print("="*50 + "\n")

    while True:
        try:
            user_input = input("You: ")
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Bot: Goodbye!")
                break
                
            if not user_input.strip():
                continue
                
            initial_state = {
                "question": user_input,
                "messages": [] 
            }
            # enter graph
            result_state = app.invoke(initial_state)  
            # --- NEW: PRINTING THE MESSAGES OBJECT ---
            print("\n--- DEBUG: RAW MESSAGES OBJECT ---")
            print(result_state["messages"])
            print("----------------------------------\n")
            response = result_state["messages"][-1].content
            print(f"Bot: {response}\n")
            
        except KeyboardInterrupt:
            print("\nBot: Goodbye!")
            break
        except Exception as e:
            print(f"\n[System Error]: An unexpected error occurred: {e}\n")

if __name__ == '__main__':
    main()