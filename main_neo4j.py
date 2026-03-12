import os
import dotenv
from neo4j_agent.graph import app

dotenv.load_dotenv()

def main():
    print("\n" + "="*50)
    print("The Anime Archive Assistant.")
    print("Type: 'quit', 'exit', or 'q' to stop.")
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
                "messages": [],
            }
            # enter graph
            config = {"configurable": {"thread_id": "user-session-1"}} # the checkpinter will remember this throughout invocations
            result_state = app.invoke(initial_state, config=config)
            response = result_state["messages"][-1].content
            print(f"Bot: {response}\n")
            
        except KeyboardInterrupt:
            print("\nBot: Goodbye!")
            break
        except Exception as e:
            print(f"\n[System Error]: An unexpected error occurred: {e}\n")

if __name__ == '__main__':
    main()