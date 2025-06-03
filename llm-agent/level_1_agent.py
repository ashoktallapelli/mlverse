import asyncio

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.yfinance import YFinanceTools

agent = Agent(
    model=Ollama(id="llama3.2"),
    tools=[YFinanceTools(stock_price=True)],
    instructions="Use tables to display data. Don't include any other text.",
    markdown=True,
)


async def chat_loop():
    """Interactive chat loop"""
    print("Commands: 'quit' (exit)")

    while True:
        try:
            query = input("\n🧑 YOU: ").strip()

            if query.lower() == 'quit':
                break
            elif not query:
                continue

            print(f"\n🤖 BOT:")
            agent.print_response(query, stream=True)

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    asyncio.run(chat_loop())
