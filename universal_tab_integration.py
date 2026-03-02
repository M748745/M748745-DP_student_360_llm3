"""
Universal Tab Integration
=========================
A single function that can be called from ANY tab to generate LLM-driven insights.

Usage from any tab:
    from universal_tab_integration import generate_tab_insights

    result = generate_tab_insights(
        df=df,
        tab_name='executive_summary',  # or 'academic_analytics', etc.
        model=model,
        url=url
    )
"""

import streamlit as st
from context_builder import build_universal_context
from llm_multi_caller import generate_with_llm
from typing import Dict, Any, Optional
import importlib


# ============================================================================
# UNIVERSAL INTEGRATION FUNCTION
# ============================================================================

def generate_tab_insights(
    df,
    tab_name: str,
    model: str,
    url: str,
    config_overrides: Optional[Dict[str, Any]] = None,
    use_cache: bool = True
) -> Dict[str, Any]:
    """
    Universal function to generate LLM-driven insights for ANY tab.

    This function:
    1. Builds universal context (all 7 layers)
    2. Loads tab-specific configuration
    3. Generates content with LLM
    4. Caches results
    5. Returns structured output

    Args:
        df: pandas DataFrame with data
        tab_name: Name of tab config (e.g., 'executive_summary', 'academic_analytics')
        model: Ollama model name (e.g., 'llama3.1')
        url: Ollama server URL (e.g., 'http://localhost:11434')
        config_overrides: Optional dict to override context config
        use_cache: Whether to use Streamlit session state cache

    Returns:
        Dict containing:
            - sections: Dict of section results
            - metadata: Generation metadata
            - context: The built context (for debugging)
            - config_used: The configuration used
    """

    # Check cache first
    cache_key = f'{tab_name}_insights'
    if use_cache and cache_key in st.session_state.llm_cache:
        return st.session_state.llm_cache[cache_key]

    # Step 1: Build universal context (works with ANY dataset)
    context_config = config_overrides or {
        'enable_layers': ['all'],
        'domain': 'auto',
        'depth': 'standard'
    }

    context = build_universal_context(df, config=context_config)

    # Step 2: Load tab-specific configuration
    try:
        # Dynamic import of tab configuration
        config_module = importlib.import_module(f'configs.{tab_name}_config')
        sections_config = getattr(config_module, f'{tab_name.upper()}_SECTIONS')
    except (ImportError, AttributeError) as e:
        st.error(f"Configuration not found for tab: {tab_name}")
        st.error(f"Expected file: configs/{tab_name}_config.py")
        st.error(f"Expected variable: {tab_name.upper()}_SECTIONS")
        return {
            'sections': {},
            'metadata': {'error': str(e)},
            'context': context,
            'config_used': None
        }

    # Step 3: Generate with LLM
    model_config = {
        'model': model,
        'url': url,
        'enable_parallel': True,
        'enable_coherence': True
    }

    result = generate_with_llm(
        context=context,
        sections_config=sections_config,
        model_config=model_config
    )

    # Add context and config to result
    result['context'] = context
    result['config_used'] = {
        'tab_name': tab_name,
        'sections_count': len(sections_config),
        'context_config': context_config,
        'model_config': model_config
    }

    # Cache result
    if use_cache:
        st.session_state.llm_cache[cache_key] = result

    return result


# ============================================================================
# DISPLAY HELPER FUNCTIONS
# ============================================================================

def display_tab_insights(result: Dict[str, Any], sections_config: list):
    """
    Display tab insights in a standardized format.

    Args:
        result: Result from generate_tab_insights()
        sections_config: The sections configuration used
    """

    if 'error' in result.get('metadata', {}):
        st.error(f"Generation failed: {result['metadata']['error']}")
        return

    # Display each section
    for section in sections_config:
        section_name = section['name']
        section_result = result['sections'].get(section_name, {})

        st.markdown(f"#### {section['title']}")

        if section_result.get('success'):
            # Display content
            st.markdown(section_result['response'])

            # Show validation info in expander
            validation = section_result.get('validation', {})
            if validation:
                with st.expander("📊 Quality Metrics", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Quality Score", f"{validation['score']}/100")
                    with col2:
                        st.metric("Valid", "✅" if validation['valid'] else "❌")
                    with col3:
                        st.metric("Tokens", section_result.get('tokens', 0))

                    if validation.get('issues'):
                        st.caption(f"Issues: {', '.join(validation['issues'])}")
        else:
            st.error(f"❌ Failed: {section_result.get('error', 'Unknown error')}")

        st.divider()

    # Display metadata
    metadata = result.get('metadata', {})
    if metadata:
        with st.expander("⚙️ Generation Metadata", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Time", f"{metadata.get('total_time', 0):.1f}s")
            with col2:
                st.metric("Total Tokens", metadata.get('total_tokens', 0))
            with col3:
                st.metric("Success Rate", f"{metadata.get('success_rate', 0)*100:.0f}%")
            with col4:
                st.metric("Sections", metadata.get('sections_count', 0))

            st.caption(f"Execution Mode: {metadata.get('execution_mode', 'unknown')}")


def display_context_summary(context: Dict[str, Any]):
    """
    Display a summary of the built context for debugging/transparency.

    Args:
        context: Context from build_universal_context()
    """

    st.markdown("### 🔍 Context Analysis Summary")

    metrics_intel = context.get('intelligent_metrics', {})

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Detected Domain", metrics_intel.get('detected_domain', 'unknown').upper())
    with col2:
        entities = metrics_intel.get('detected_entities', [])
        st.metric("Primary Entity", entities[0] if entities else 'unknown')
    with col3:
        calc_metrics = metrics_intel.get('calculated_metrics', {})
        st.metric("Auto-Calculated Metrics", len(calc_metrics))

    # Show layers enabled
    st.caption("**Enabled Layers:**")
    layers_present = [key for key in context.keys() if key.endswith('_discovery') or key == 'intelligent_metrics']
    st.caption(", ".join([layer.replace('_', ' ').title() for layer in layers_present]))

    # Show sample calculated metrics
    if calc_metrics:
        with st.expander("📊 Sample Auto-Calculated Metrics", expanded=False):
            for key, value in list(calc_metrics.items())[:5]:
                if isinstance(value, float):
                    st.caption(f"**{key}**: {value:,.2f}")
                else:
                    st.caption(f"**{key}**: {value:,}" if isinstance(value, int) else f"**{key}**: {value}")


# ============================================================================
# STREAMLIT TAB INTEGRATION PATTERN
# ============================================================================

def create_llm_driven_tab(
    tab_name: str,
    tab_title: str,
    tab_description: str,
    button_text: str,
    df,
    model: str,
    url: str,
    ollama_connected: bool,
    show_context_summary: bool = False
):
    """
    Complete ready-to-use tab implementation.

    Just call this function from within a `with tabs[X]:` block!

    Args:
        tab_name: Config name (e.g., 'executive_summary')
        tab_title: Display title (e.g., "📊 Executive Summary")
        tab_description: Short description
        button_text: Button text (e.g., "Generate Executive Summary")
        df: pandas DataFrame
        model: Ollama model name
        url: Ollama server URL
        ollama_connected: Whether Ollama is connected
        show_context_summary: Whether to show context analysis summary
    """

    st.header(tab_title)
    st.caption(tab_description)

    if not ollama_connected:
        st.warning("⚠️ Connect to Ollama to enable AI-driven insights")
        return

    # Generate button
    if st.button(f"🤖 {button_text}", key=f"{tab_name}_generate", type="primary"):
        with st.spinner("🔄 Analyzing data and generating insights..."):
            # Generate insights
            result = generate_tab_insights(
                df=df,
                tab_name=tab_name,
                model=model,
                url=url
            )

            # Show context summary if requested
            if show_context_summary and 'context' in result:
                display_context_summary(result['context'])
                st.divider()

    # Display cached results if available
    cache_key = f'{tab_name}_insights'
    if cache_key in st.session_state.llm_cache:
        result = st.session_state.llm_cache[cache_key]

        # Load config to get sections
        try:
            config_module = importlib.import_module(f'configs.{tab_name}_config')
            sections_config = getattr(config_module, f'{tab_name.upper()}_SECTIONS')

            display_tab_insights(result, sections_config)
        except Exception as e:
            st.error(f"Error displaying results: {e}")


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("UNIVERSAL TAB INTEGRATION - MODULE LOADED")
    print("=" * 80)
    print("\nThis module provides universal functions to integrate LLM insights into ANY tab.")
    print("\nKey Functions:")
    print("  - generate_tab_insights(): Generate insights for any tab")
    print("  - display_tab_insights(): Display results in standard format")
    print("  - display_context_summary(): Show context analysis")
    print("  - create_llm_driven_tab(): Complete tab implementation in 1 function call")
    print("\nUsage Example:")
    print("""
    # In your Streamlit app:
    from universal_tab_integration import create_llm_driven_tab

    with tabs[0]:
        create_llm_driven_tab(
            tab_name='executive_summary',
            tab_title='📊 Executive Summary',
            tab_description='AI-Driven Strategic Analytics',
            button_text='Generate Executive Summary',
            df=df,
            model=model,
            url=url,
            ollama_connected=st.session_state.ollama_connected
        )
    """)
    print("\n" + "=" * 80)
