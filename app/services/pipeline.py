from app.services.state import ConversationState
from app.services.ingestion import normalize_input
from app.services.transcription import transcribe_text_input_with_trace
from app.services.context import update_context
from app.services.suggestions import generate_suggestions
from app.services.quick_replies import generate_quick_replies
from app.services.fillers import generate_fillers
from app.services.terms import suggest_terms


def process_ingest(state: ConversationState, text: str) -> dict:
    normalized = normalize_input(text)
    trace = transcribe_text_input_with_trace(normalized)
    transcript_text = str(trace.get("text", ""))
    context_metadata = {
        "context_source": "audio_comprehension",
        "transcription_provider_configured": trace.get("configured_provider"),
        "transcription_provider_selected": trace.get("provider_selected"),
        "transcription_provider_effective": trace.get("effective_provider"),
        "transcription_provider_used": trace.get("provider_used"),
        "transcription_fallback_used": bool(trace.get("fallback_used", False)),
        "transcription_fallback_reason": trace.get("fallback_reason", ""),
        "transcription_latency_ms": int(trace.get("transcription_latency_ms", 0) or 0),
        "recognized_context": True,
    }
    update_context(state, speaker="user", text=transcript_text, metadata=context_metadata)

    state.suggestions = generate_suggestions(state)
    state.quick_replies = generate_quick_replies(state)
    state.fillers = generate_fillers()
    state.term_hints = suggest_terms(transcript_text)

    return state.snapshot()
