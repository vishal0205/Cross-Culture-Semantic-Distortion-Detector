import streamlit as st
import traceback

from config import DEFAULT_TEXT, OLLAMA_MODEL, REWRITE_MODES
from services.history import init_history_db, load_recent_history, save_analysis
from services.llm import canonicalize_text
from services.reporting import highlight_text_diff, metric_rows, risk_items
from services.scoring import build_report
from services.schemas import ComparisonResult


def render_analysis_tab():
    st.title("Cross-Culture Semantic Distortion Detector")
    st.caption("Rewrite text into canonical English, measure what changed, and flag meaning drift.")

    with st.sidebar:
        st.subheader("Model Settings")
        st.write(f"LLM: `{OLLAMA_MODEL}`")
        st.write("Embedding model: `all-mpnet-base-v2`")
        st.info("The app stores recent analyses locally so you can compare results over time.")
        if st.button("Run Health Check", use_container_width=True):
            run_health_check()

    user_input = st.text_area(
        "Enter text to analyze",
        value=DEFAULT_TEXT,
        height=180,
        placeholder="Paste a sentence or paragraph here...",
    )
    selected_modes = st.multiselect(
        "Rewrite modes to compare",
        options=list(REWRITE_MODES.keys()),
        default=["Simple", "Literal", "Culturally Neutral"],
    )

    if st.button("Analyze", type="primary", use_container_width=True):
        cleaned_input = user_input.strip()
        if not cleaned_input:
            st.warning("Please enter some text to analyze.")
            return
        if not selected_modes:
            st.warning("Please select at least one rewrite mode.")
            return

        with st.spinner("Running canonicalization and distortion analysis..."):
            comparisons = []
            for mode in selected_modes:
                try:
                    canonicalization = canonicalize_text(cleaned_input, mode=mode)
                except Exception as exc:
                    show_step_error(f"canonicalization ({mode})", exc)
                    return

                try:
                    report = build_report(cleaned_input, canonicalization.canonicalized_text)
                except Exception as exc:
                    show_step_error(f"scoring ({mode})", exc)
                    return

                try:
                    save_analysis(cleaned_input, canonicalization, report)
                except Exception as exc:
                    show_step_error(f"history save ({mode})", exc)
                    return

                comparisons.append(
                    ComparisonResult(
                        mode=mode,
                        canonicalization=canonicalization,
                        report=report,
                    )
                )

        comparisons.sort(key=lambda item: item.report.overall_score, reverse=True)
        render_comparison_results(cleaned_input, comparisons)


def render_history_tab():
    st.title("Recent Analysis History")
    rows = load_recent_history(limit=12)
    if not rows:
        st.info("No analyses have been saved yet. Run an analysis to populate history.")
        return

    history_records = [
        {
            "Created At": created_at,
            "Original Text": original_text,
            "Canonicalized Text": canonicalized_text,
            "Overall Score": round(overall_score, 4),
            "Distortion Level": distortion_level,
        }
        for created_at, original_text, canonicalized_text, overall_score, distortion_level in rows
    ]
    st.dataframe(history_records, use_container_width=True, hide_index=True)


def render_comparison_results(original_text: str, comparisons: list[ComparisonResult]):
    best_result = comparisons[0]
    st.subheader("Best Overall Rewrite")
    score_col, level_col, mode_col = st.columns(3)
    score_col.metric("Overall score", f"{best_result.report.overall_score:.4f}")
    level_col.metric("Distortion level", best_result.report.distortion_level)
    mode_col.metric("Top mode", best_result.mode)
    st.write(best_result.report.summary)

    leaderboard = [
        {
            "Mode": item.mode,
            "Overall Score": round(item.report.overall_score, 4),
            "Semantic Similarity": round(item.report.semantic_similarity, 4),
            "Token Overlap": round(item.report.token_overlap, 4),
            "Entity Preservation": round(item.report.entity_preservation, 4),
            "Distortion Level": item.report.distortion_level,
        }
        for item in comparisons
    ]
    st.subheader("Mode Comparison")
    st.dataframe(leaderboard, use_container_width=True, hide_index=True)

    mode_tabs = st.tabs([item.mode for item in comparisons])
    for tab, item in zip(mode_tabs, comparisons):
        with tab:
            left_col, right_col = st.columns(2)
            highlighted_original, highlighted_rewrite = highlight_text_diff(
                original_text,
                item.canonicalization.canonicalized_text,
            )
            with left_col:
                st.markdown("**Original Text**")
                st.markdown(highlighted_original)
            with right_col:
                st.markdown(f"**{item.mode} Rewrite**")
                st.markdown(highlighted_rewrite)

            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            metric_col1.metric("Semantic similarity", f"{item.report.semantic_similarity:.4f}")
            metric_col2.metric("Token overlap", f"{item.report.token_overlap:.4f}")
            metric_col3.metric("Entity preservation", f"{item.report.entity_preservation:.4f}")
            metric_col4.metric("Length ratio", f"{item.report.length_ratio:.2f}")
            st.dataframe(metric_rows(item.report), use_container_width=True, hide_index=True)

            insight_tab, risks_tab, concepts_tab = st.tabs(["Explanation", "Nuance Risks", "Concept Tracking"])
            with insight_tab:
                st.write(item.canonicalization.explanation)
                changed_items = item.canonicalization.changed_phrases or ["No explicit phrase changes were listed."]
                st.write("Changed phrases:")
                for changed_item in changed_items:
                    st.write(f"- {changed_item}")
            with risks_tab:
                for risk_item in risk_items(item.canonicalization):
                    st.write(f"- {risk_item}")
            with concepts_tab:
                concepts = item.canonicalization.preserved_concepts or ["No preserved concepts were identified."]
                for concept in concepts:
                    st.write(f"- {concept}")


def main():
    st.set_page_config(page_title="Semantic Distortion Detector", page_icon=":mag:", layout="wide")
    init_history_db()
    analysis_tab, history_tab = st.tabs(["Analyzer", "History"])
    with analysis_tab:
        render_analysis_tab()
    with history_tab:
        render_history_tab()


def show_step_error(step_name: str, exc: Exception):
    st.error(f"The analysis failed during {step_name}.")
    st.code("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)).strip())


def run_health_check():
    health_messages = []

    try:
        sample = canonicalize_text("This is a quick health check sentence.")
        health_messages.append("Ollama check passed.")
    except Exception as exc:
        st.error("Health check failed at the Ollama step.")
        st.code("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)).strip())
        return

    try:
        report = build_report("This is a quick health check sentence.", sample.canonicalized_text)
        health_messages.append(f"Embedding and scoring check passed. Overall score: {report.overall_score:.4f}")
    except Exception as exc:
        st.error("Health check failed at the embedding/scoring step.")
        st.code("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)).strip())
        return

    st.success("\n".join(health_messages))


if __name__ == "__main__":
    main()
