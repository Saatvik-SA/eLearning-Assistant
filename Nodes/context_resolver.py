from langchain_core.runnables import RunnableLambda
from Utilities.Core import prepare_academic_context
import logging
from typing import Any, Dict
from Nodes.agent_state import AgentState, update_agent_state
from rapidfuzz import process, fuzz

def context_resolver_node() -> RunnableLambda:
    """
    Resolves academic context by embedding uploaded or existing PDFs, updates AgentState.
    Uses fuzzy matching to resolve file references from user query or state.
    Always passes through 'most_recent_question' and 'query' from input state.
    """
    def resolve_context(state: AgentState) -> AgentState:
        try:
            uploaded_files = state.get("uploaded_files", [])
            textbook = state.get("textbook")
            user_query = state.get("most_recent_question") or state.get("query") or ""
            file_reference = state.get("file_reference")
            # Try to resolve file from user query or file_reference using fuzzy matching
            file_candidates = uploaded_files.copy()
            resolved_file = None
            match_source = None
            if file_reference:
                # Fuzzy match file_reference to uploaded_files
                match, score, _ = process.extractOne(file_reference, file_candidates, scorer=fuzz.ratio)
                if score > 80:
                    resolved_file = match
                    match_source = "file_reference"
                    logging.info(f"[Context Resolver] Fuzzy matched file_reference '{file_reference}' to '{resolved_file}' (score={score})")
                else:
                    logging.warning(f"[Context Resolver] No good fuzzy match for file_reference '{file_reference}'. Candidates: {file_candidates}")
            elif user_query:
                # Try to extract a filename-like phrase from the query (very basic)
                for fname in file_candidates:
                    if fname.lower() in user_query.lower():
                        resolved_file = fname
                        match_source = "user_query_exact"
                        logging.info(f"[Context Resolver] Found exact file match in user query: '{fname}'")
                        break
                if not resolved_file:
                    # Fuzzy match any filename to the query
                    match, score, _ = process.extractOne(user_query, file_candidates, scorer=fuzz.partial_ratio)
                    if score > 80:
                        resolved_file = match
                        match_source = "user_query_fuzzy"
                        logging.info(f"[Context Resolver] Fuzzy matched user query to file '{resolved_file}' (score={score})")
            # Fallback to first uploaded file if nothing else
            if not resolved_file and file_candidates:
                resolved_file = file_candidates[0]
                match_source = "default_first"
                logging.info(f"[Context Resolver] Defaulting to first uploaded file: '{resolved_file}'")
            if not resolved_file:
                logging.error(f"[Context Resolver] No file could be resolved from uploaded_files: {file_candidates}")
                return update_agent_state(state, error="No study material found. Please upload a file.")
            collection, embedder, total_chunks = prepare_academic_context()
            state.update({
                "collection": collection,
                "embedder": embedder,
                "total_chunks": total_chunks,
                "textbook": resolved_file,
                "context_match_source": match_source,
                "most_recent_question": state.get("most_recent_question"),
                "query": state.get("query"),
            })
            logging.info(f"[Context Resolver] Returning state: {state}")
            return state
        except Exception as e:
            logging.error(f"[Context Resolver] Error: {e}")
            return update_agent_state(state, error=str(e))
    return RunnableLambda(resolve_context)
