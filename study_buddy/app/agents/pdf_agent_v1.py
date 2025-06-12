from textwrap import dedent

from agno.agent import Agent
from dotenv import load_dotenv

from app.utils.logger import logger
from config.llm_config import get_llm

load_dotenv()


async def run_agent(message: str) -> str:
    """Run the pdf agent with the given message."""
    logger.info(f"Starting agent with message: {message}")

    try:
        agent = Agent(
            name="Study buddy",
            model=get_llm(),
            instructions=dedent("""\
                    You are a AI study assistant.
                    - Use headings to organize your responses
                    - Be concise and focus on relevant information\
                """),
            markdown=True,
            show_tool_calls=True,
        )
        logger.info("Agent created")

        # Run the agent
        logger.info("Running agent...")
        logger.info("=" * 50)
        response = await agent.arun(message, stream=False)
        logger.info("=" * 50)
        logger.info("Agent finished")
        return response.content

    except Exception as e:
        logger.info(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
        return f"Error: {e}"


# if __name__ == "__main__":
#     # Basic example - exploring project license
#     async def main():
#         response = await run_agent("List all the endpoints")
#         print(response)
#
#
#     asyncio.run(main())


async def answer_with_context(question, context_chunks):
    context = "\n".join(context_chunks)
    prompt = f"""You are a helpful study assistant. Use the following notes to answer the question.
    Context: {context}
    Question: {question}
    Answer:"""

    response = await run_agent(prompt)
    return response
