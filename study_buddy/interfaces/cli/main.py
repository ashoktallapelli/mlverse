import typer
from app.ingestion.pdf_reader import extract_text_from_pdf
from app.embedding.indexer import index_text
from app.embedding.retriever import retrieve_relevant_chunks
from app.agents.study_agent import answer_with_context

cli = typer.Typer()

@cli.command()
def upload(path: str):
    with open(path, "rb") as f:
        text = extract_text_from_pdf(f.read())
    index_text(text)
    typer.echo("Indexed successfully")

@cli.command()
def ask(question: str):
    chunks = retrieve_relevant_chunks(question)
    answer = answer_with_context(question, chunks)
    typer.echo(answer)

if __name__ == "__main__":
    cli()
