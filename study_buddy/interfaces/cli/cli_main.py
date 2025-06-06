import typer

from app.embedding.embedder import embed_text
from app.ingestion.chunker import chunk_text
from app.ingestion.pdf_reader import extract_text_from_pdf
from app.embedding.indexer import index_text_chunks
from app.embedding.retriever import retrieve_relevant_chunks
from app.agents.study_agent import answer_with_context

from app.utils.logger import logger

cli = typer.Typer()


@cli.command()
def upload(path: str):
    with open(path, "rb") as f:
        text = extract_text_from_pdf(f.read())

    logger.info("Extracted text, now chunking...")
    chunks = chunk_text(text)

    logger.info(f"Chunked into {len(chunks)} parts, embedding...")
    embeddings = embed_text(chunks)

    logger.info("Indexing to FAISS...")
    index_text_chunks(chunks, embeddings)
    logger.info("Indexing complete!")


@cli.command()
def ask(question: str):
    chunks = retrieve_relevant_chunks(question)
    answer = answer_with_context(question, chunks)
    typer.echo(answer)


if __name__ == "__main__":
    cli()
