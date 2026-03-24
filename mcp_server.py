import os
import logging
import multiprocessing
from fastmcp import FastMCP

# Crawler
from crawler.fetch_data import run_spider

# Data processing
from data.data import INDEX_FILE, chunk_data, embed_data, OUTPUT_CSV

# LLM + Retrieval
from LLM.main import retrieve_context, ask_ollama, load_index

logging.basicConfig(level=logging.INFO)

mcp = FastMCP("WebBuddy")


# -------------------------------
# 🚀 PIPELINE TOOL
# -------------------------------
@mcp.tool(
    "run_pipeline",
    description="Crawl a website, process content, and build a searchable knowledge index"
)
def run_pipeline(url: str):
    try:
        logging.info(f"Starting pipeline for URL: {url}")

        # Step 1 — Crawl website
        p = multiprocessing.Process(target=run_spider, args=(url,))
        p.start()
        p.join()

        # Step 2 — Validate crawl output
        if not os.path.exists(OUTPUT_CSV):
            return {
                "status": "error",
                "message": "Crawling failed. output.csv not found."
            }

        logging.info("Crawling completed successfully.")

        # Step 3 — Chunk data
        chunk_data()
        logging.info("Chunking completed.")

        # Step 4 — Generate embeddings + FAISS index
        embed_data()
        logging.info("Embedding + indexing completed.")

        return {
            "status": "success",
            "message": "Pipeline completed successfully",
            "url": url
        }

    except Exception as e:
        logging.error(f"Pipeline failed: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }


# -------------------------------
# 🤖 QUESTION ANSWERING TOOL
# -------------------------------
@mcp.tool(
    "ask_website_question",
    description="Ask a question about a website. Automatically builds knowledge base if needed."
)
def ask(query: str, url: str, top_k: int = 10):
    try:
        logging.info(f"Received query: {query}")

        # Step 0 — Ensure index exists
        if not os.path.exists(INDEX_FILE):
            logging.info("Index not found. Running pipeline...")

            pipeline_result = run_pipeline(url)

            if pipeline_result.get("status") == "error":
                return pipeline_result

            # 🔥 Reload FAISS index after creation
            load_index()
            logging.info("Index loaded successfully.")

        # Step 1 — Retrieve relevant chunks
        results = retrieve_context(query, top_k)

        if not results:
            return {
                "status": "error",
                "message": "No relevant context found."
            }

        # Step 2 — Build context
        context = "\n\n".join([
            f"Source: {r['url']}\n{r['text']}" for r in results
        ])

        # Step 3 — Generate answer using Ollama
        answer = ask_ollama(query, context)

        return {
            "status": "success",
            "query": query,
            "answer": answer
        }

    except Exception as e:
        logging.error(f"Ask failed: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }


# -------------------------------
# ▶️ START MCP SERVER
# -------------------------------
if __name__ == "__main__":
    logging.info("Starting WebBuddy MCP server...")
    mcp.run(transport="stdio")