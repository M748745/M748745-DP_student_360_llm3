"""
Journey Narrative Generation System
Generates compelling LLM-powered narratives for all story components

Each narrative component:
- Takes story metadata + calculated metrics
- Uses LLM to generate engaging, business-focused content
- Returns formatted narrative text
"""

import json
from typing import Dict, List, Any, Optional


# ============================================================================
# NARRATIVE COMPONENT GENERATORS
# ============================================================================

def generate_business_context_prompt(story_title: str, story_focus: str, metrics: Dict[str, Any]) -> str:
    """
    Create prompt for generating business context paragraph

    Business context explains:
    - Why this story matters to the institution
    - Strategic importance
    - Impact on business operations
    """
    metrics_summary = _format_metrics_for_prompt(metrics, max_items=10)

    prompt = f"""You are a higher education business analyst writing a strategic business context paragraph.

Story: {story_title}
Focus Area: {story_focus}

Key Metrics:
{metrics_summary}

Write a compelling 3-4 sentence business context paragraph that:
1. Explains WHY this analysis matters to university leadership
2. Connects to strategic goals (revenue, quality, reputation, student success)
3. Sets up the business importance
4. Uses professional, executive-level language

Do NOT include metrics or numbers. Focus on strategic importance and business relevance.
Write in present tense, active voice.

Business Context Paragraph:"""

    return prompt


def generate_opening_narrative_prompt(story_title: str, story_focus: str, metrics: Dict[str, Any]) -> str:
    """
    Create prompt for generating opening narrative

    Opening narrative:
    - Engaging, human-centered introduction
    - Sets the scene with key numbers
    - Creates emotional connection
    - Captures attention
    """
    metrics_summary = _format_metrics_for_prompt(metrics, max_items=15)

    prompt = f"""You are a data storyteller writing an engaging opening narrative for a university analytics story.

Story: {story_title}
Focus Area: {story_focus}

Key Metrics:
{metrics_summary}

Write a compelling 4-5 sentence opening narrative that:
1. Opens with the most striking metric or pattern
2. Weaves in 3-5 key numbers naturally into the narrative
3. Creates a sense of discovery ("Our analysis reveals...")
4. Uses vivid, engaging language while remaining professional
5. Sets up the "so what?" - why should we care?

Use present tense. Include specific numbers from the metrics.
Make it readable and engaging, not dry or academic.

Opening Narrative:"""

    return prompt


def generate_data_insights_prompt(story_title: str, story_focus: str, metrics: Dict[str, Any], story_context: str = "") -> str:
    """
    Create prompt for generating data insights analysis

    Data insights:
    - Detailed analysis of patterns in the data
    - Connections between metrics
    - Comparisons and trends
    - What the numbers reveal
    """
    metrics_summary = _format_metrics_for_prompt(metrics, max_items=20)

    prompt = f"""You are a university data analyst writing a detailed data insights section.

Story: {story_title}
Focus Area: {story_focus}

{f"Context: {story_context}" if story_context else ""}

Complete Metrics:
{metrics_summary}

Write a comprehensive data insights analysis (6-8 sentences) that:
1. Analyzes the patterns and trends in the data
2. Makes comparisons (year-over-year, segment-to-segment, actual vs benchmark)
3. Identifies correlations and relationships between metrics
4. Highlights both strengths and concerns
5. Uses specific numbers and percentages from the metrics
6. Organizes insights from high-level to detailed
7. Maintains analytical, objective tone

Include at least 8-10 specific numbers/metrics in your analysis.
Use phrases like "The data reveals...", "Analysis shows...", "Notably...", "In particular..."

Data Insights:"""

    return prompt


def generate_business_impact_prompt(story_title: str, story_focus: str, metrics: Dict[str, Any], insights: str = "") -> str:
    """
    Create prompt for generating business impact analysis

    Business impact:
    - Financial implications (revenue, costs, ROI)
    - Strategic consequences
    - Risk assessment
    - Opportunity identification
    """
    metrics_summary = _format_metrics_for_prompt(metrics, max_items=15)

    prompt = f"""You are a higher education CFO analyzing business impact and financial implications.

Story: {story_title}
Focus Area: {story_focus}

{f"Data Insights: {insights}" if insights else ""}

Key Metrics:
{metrics_summary}

Write a business impact analysis (5-7 sentences) that:
1. Quantifies financial impact (revenue, costs, savings, ROI)
2. Assesses strategic implications for the institution
3. Identifies risks and opportunities
4. Makes clear connections: "This means..." or "The impact is..."
5. Uses business metrics: revenue, margins, efficiency, utilization
6. Includes specific dollar amounts when available
7. Discusses both current impact and future implications

Focus on money, strategy, and competitive position.
Use executive language. Be specific about financial impact.

Business Impact:"""

    return prompt


def generate_findings_summary_prompt(story_title: str, story_focus: str, metrics: Dict[str, Any],
                                     insights: str = "", impact: str = "") -> str:
    """
    Create prompt for generating findings summary (bullet points)

    Findings summary:
    - 4-6 key bullet points
    - Most important discoveries
    - Specific numbers included
    - Action-oriented
    """
    metrics_summary = _format_metrics_for_prompt(metrics, max_items=15)

    prompt = f"""You are summarizing key findings from a university data analysis.

Story: {story_title}
Focus Area: {story_focus}

{f"Data Insights: {insights}" if insights else ""}
{f"Business Impact: {impact}" if impact else ""}

Key Metrics:
{metrics_summary}

Create a findings summary with 4-6 bullet points that:
1. Highlight the most critical discoveries
2. Each bullet includes at least one specific number/metric
3. Mix positive findings and concerns
4. Are concise but substantive (1-2 sentences each)
5. Use strong, active language
6. Focus on actionable insights

Format as bullet points starting with "•"
Each finding should be clear, specific, and include data.

Key Findings:"""

    return prompt


def generate_action_plan_prompt(story_title: str, story_focus: str, metrics: Dict[str, Any],
                                impact: str = "", findings: str = "") -> str:
    """
    Create prompt for generating action plan

    Action plan:
    - 3-5 specific recommended actions
    - Each with: action, timeline, budget/resources, expected outcome
    - Prioritized by impact
    - Concrete and implementable
    """
    metrics_summary = _format_metrics_for_prompt(metrics, max_items=12)

    prompt = f"""You are a university strategy consultant creating an action plan.

Story: {story_title}
Focus Area: {story_focus}

{f"Business Impact: {impact}" if impact else ""}
{f"Key Findings: {findings}" if findings else ""}

Metrics:
{metrics_summary}

Create an action plan with 3-5 specific recommended actions that:
1. Each action is concrete and implementable
2. Includes timeline (immediate/30 days/90 days/6 months)
3. Includes budget estimate or resource requirement
4. States expected outcome/ROI
5. Prioritized by impact (list most important first)
6. Directly addresses issues revealed in the data

Format each action as:
"• [Action]: [Description] (Timeline: [X days/months] | Budget: [Amount] | Expected Impact: [Outcome])"

Be specific about numbers, timelines, and expected results.
Focus on high-ROI, feasible actions.

Recommended Action Plan:"""

    return prompt


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _format_metrics_for_prompt(metrics: Dict[str, Any], max_items: int = 15) -> str:
    """
    Format metrics dictionary into readable text for LLM prompt

    Args:
        metrics: Dictionary of calculated metrics
        max_items: Maximum number of metrics to include

    Returns:
        Formatted string with key metrics
    """
    lines = []
    count = 0

    def format_value(value: Any) -> str:
        """Format metric value for display"""
        if isinstance(value, float):
            if value > 1000000:
                return f"AED {value/1000000:.2f}M"
            elif value > 1000:
                return f"AED {value:,.0f}"
            elif value < 1:
                return f"{value:.1%}" if value <= 1 else f"{value:.3f}"
            else:
                return f"{value:.1f}"
        elif isinstance(value, int):
            if value > 1000000:
                return f"AED {value/1000000:.2f}M"
            elif value > 1000:
                return f"{value:,}"
            else:
                return str(value)
        elif isinstance(value, dict):
            return f"[{len(value)} items]"
        elif isinstance(value, list):
            return f"[{len(value)} entries]"
        else:
            return str(value)

    for key, value in metrics.items():
        if count >= max_items:
            break

        # Skip complex nested structures in summary
        if isinstance(value, (dict, list)) and key not in ['gender_distribution', 'performance_distribution']:
            continue

        # Format the metric
        readable_key = key.replace('_', ' ').title()
        formatted_value = format_value(value)

        lines.append(f"- {readable_key}: {formatted_value}")
        count += 1

    return "\n".join(lines)


def _extract_json_metrics(metrics: Dict[str, Any]) -> str:
    """
    Convert metrics to clean JSON string for prompts that need structured data
    """
    # Create a simplified version of metrics for JSON
    simplified = {}

    for key, value in metrics.items():
        if isinstance(value, (int, float, str)):
            simplified[key] = value
        elif isinstance(value, dict):
            simplified[key] = {k: v for k, v in value.items() if isinstance(v, (int, float, str))}[:5]  # Limit nested items
        elif isinstance(value, list):
            simplified[key] = value[:5]  # Limit list items

    return json.dumps(simplified, indent=2)


# ============================================================================
# MAIN GENERATION FUNCTIONS
# ============================================================================

def generate_narrative_component(
    component_type: str,
    story_title: str,
    story_focus: str,
    metrics: Dict[str, Any],
    query_llm_func,
    model: str,
    url: str,
    context: Optional[Dict[str, str]] = None,
    temperature: float = 0.4,
    timeout: int = 120
) -> str:
    """
    Generate a specific narrative component using LLM

    Args:
        component_type: Type of component ('business_context', 'opening_narrative', etc.)
        story_title: Title of the story
        story_focus: Focus area description
        metrics: Calculated metrics for this story
        query_llm_func: Function to call LLM (query_ollama from main app)
        model: LLM model name
        url: Ollama API URL
        context: Optional context from previous components (e.g., {'insights': '...', 'impact': '...'})
        temperature: LLM temperature (0.3-0.5 for structured content)
        timeout: Request timeout in seconds

    Returns:
        Generated narrative text
    """
    context = context or {}

    # Select appropriate prompt generator
    prompt_generators = {
        'business_context': generate_business_context_prompt,
        'opening_narrative': generate_opening_narrative_prompt,
        'data_insights': generate_data_insights_prompt,
        'business_impact': generate_business_impact_prompt,
        'findings_summary': generate_findings_summary_prompt,
        'action_plan': generate_action_plan_prompt
    }

    if component_type not in prompt_generators:
        return f"Error: Unknown component type '{component_type}'"

    # Generate prompt
    generator = prompt_generators[component_type]

    # Build kwargs based on what the generator accepts
    kwargs = {'story_title': story_title, 'story_focus': story_focus, 'metrics': metrics}

    # Add context if generator accepts it
    if component_type == 'data_insights' and 'story_context' in context:
        kwargs['story_context'] = context.get('story_context', '')
    elif component_type == 'business_impact' and 'insights' in context:
        kwargs['insights'] = context.get('insights', '')
    elif component_type == 'findings_summary':
        if 'insights' in context:
            kwargs['insights'] = context.get('insights', '')
        if 'impact' in context:
            kwargs['impact'] = context.get('impact', '')
    elif component_type == 'action_plan':
        if 'impact' in context:
            kwargs['impact'] = context.get('impact', '')
        if 'findings' in context:
            kwargs['findings'] = context.get('findings', '')

    prompt = generator(**kwargs)

    # Call LLM
    try:
        response = query_llm_func(
            prompt,
            model,
            url,
            temperature=temperature,
            num_predict=800,  # Enough for detailed narratives
            timeout=timeout,
            num_ctx=4096,
            top_k=40,
            top_p=0.9,
            auto_optimize=False
        )

        return response.strip() if response else f"Error: Empty response for {component_type}"

    except Exception as e:
        return f"Error generating {component_type}: {str(e)}"


def generate_full_story_narrative(
    story_id: str,
    story_title: str,
    story_focus: str,
    metrics: Dict[str, Any],
    query_llm_func,
    model: str,
    url: str,
    temperature: float = 0.4,
    timeout: int = 120
) -> Dict[str, str]:
    """
    Generate all narrative components for a complete story

    Components generated in order:
    1. business_context
    2. opening_narrative
    3. data_insights (uses business_context)
    4. business_impact (uses data_insights)
    5. findings_summary (uses insights + impact)
    6. action_plan (uses impact + findings)

    Args:
        story_id: Story identifier
        story_title: Story title
        story_focus: Story focus area
        metrics: All calculated metrics for this story
        query_llm_func: Function to call LLM
        model: LLM model name
        url: Ollama API URL
        temperature: LLM temperature
        timeout: Request timeout per component

    Returns:
        Dictionary with all narrative components:
        {
            'business_context': '...',
            'opening_narrative': '...',
            'data_insights': '...',
            'business_impact': '...',
            'findings_summary': '...',
            'action_plan': '...'
        }
    """
    narratives = {}
    context = {}

    # Generate components in sequence (some depend on previous ones)

    # 1. Business Context
    narratives['business_context'] = generate_narrative_component(
        'business_context', story_title, story_focus, metrics,
        query_llm_func, model, url, {}, temperature, timeout
    )
    context['story_context'] = narratives['business_context']

    # 2. Opening Narrative
    narratives['opening_narrative'] = generate_narrative_component(
        'opening_narrative', story_title, story_focus, metrics,
        query_llm_func, model, url, context, temperature, timeout
    )

    # 3. Data Insights
    narratives['data_insights'] = generate_narrative_component(
        'data_insights', story_title, story_focus, metrics,
        query_llm_func, model, url, context, temperature, timeout
    )
    context['insights'] = narratives['data_insights']

    # 4. Business Impact
    narratives['business_impact'] = generate_narrative_component(
        'business_impact', story_title, story_focus, metrics,
        query_llm_func, model, url, context, temperature, timeout
    )
    context['impact'] = narratives['business_impact']

    # 5. Findings Summary
    narratives['findings_summary'] = generate_narrative_component(
        'findings_summary', story_title, story_focus, metrics,
        query_llm_func, model, url, context, temperature, timeout
    )
    context['findings'] = narratives['findings_summary']

    # 6. Action Plan
    narratives['action_plan'] = generate_narrative_component(
        'action_plan', story_title, story_focus, metrics,
        query_llm_func, model, url, context, temperature, timeout
    )

    return narratives


def generate_journey_narratives(
    journey_id: str,
    journey_name: str,
    stories: List[Dict[str, Any]],
    all_metrics: Dict[str, Dict[str, Any]],
    query_llm_func,
    model: str,
    url: str,
    temperature: float = 0.4,
    timeout: int = 120,
    progress_callback=None
) -> Dict[str, Dict[str, str]]:
    """
    Generate narratives for all stories in a journey

    Args:
        journey_id: Journey identifier (e.g., 'journey_1')
        journey_name: Journey display name
        stories: List of story definitions from journey_definitions.py
        all_metrics: All calculated metrics organized by story_id
        query_llm_func: Function to call LLM
        model: LLM model name
        url: Ollama API URL
        temperature: LLM temperature
        timeout: Request timeout per component
        progress_callback: Optional callback function(current, total, story_title)

    Returns:
        Dictionary organized by story_id:
        {
            'story_1_1': {
                'business_context': '...',
                'opening_narrative': '...',
                ...
            },
            'story_1_2': {...},
            ...
        }
    """
    journey_narratives = {}
    total_stories = len(stories)

    for idx, story in enumerate(stories, 1):
        story_id = story['id']
        story_title = story['title']
        story_focus = story['focus_area']

        # Progress callback
        if progress_callback:
            progress_callback(idx, total_stories, story_title)

        # Get metrics for this story
        metrics = all_metrics.get(story_id, {})

        if not metrics:
            print(f"⚠️ Warning: No metrics found for {story_id}")
            continue

        # Generate all narrative components for this story
        journey_narratives[story_id] = generate_full_story_narrative(
            story_id, story_title, story_focus, metrics,
            query_llm_func, model, url, temperature, timeout
        )

    return journey_narratives


# ============================================================================
# BATCH PROCESSING
# ============================================================================

def generate_all_journeys_narratives(
    all_journeys: List[Dict[str, Any]],
    all_metrics: Dict[str, Dict[str, Any]],
    query_llm_func,
    model: str,
    url: str,
    temperature: float = 0.4,
    timeout: int = 120,
    progress_callback=None
) -> Dict[str, Dict[str, Dict[str, str]]]:
    """
    Generate narratives for ALL stories across ALL journeys

    Args:
        all_journeys: List of journey definitions from journey_definitions.py
        all_metrics: All calculated metrics organized by journey_id -> story_id
        query_llm_func: Function to call LLM
        model: LLM model name
        url: Ollama API URL
        temperature: LLM temperature
        timeout: Request timeout per component
        progress_callback: Optional callback function(journey_name, story_idx, total_stories, story_title)

    Returns:
        Complete narrative structure:
        {
            'journey_1': {
                'story_1_1': {'business_context': '...', ...},
                'story_1_2': {...},
                ...
            },
            'journey_2': {...},
            ...
        }
    """
    all_narratives = {}

    for journey in all_journeys:
        journey_id = journey['id']
        journey_name = journey['name']
        stories = journey['stories']

        print(f"\n🎯 Generating narratives for {journey_name}...")

        # Create journey-specific progress callback
        def journey_progress(current, total, story_title):
            if progress_callback:
                progress_callback(journey_name, current, total, story_title)
            print(f"  📝 Story {current}/{total}: {story_title}")

        # Get metrics for this journey
        journey_metrics = all_metrics.get(journey_id, {})

        # Generate narratives for all stories in this journey
        all_narratives[journey_id] = generate_journey_narratives(
            journey_id, journey_name, stories, journey_metrics,
            query_llm_func, model, url, temperature, timeout,
            journey_progress
        )

    return all_narratives


# ============================================================================
# FALLBACK NARRATIVES
# ============================================================================

def create_fallback_narrative(component_type: str, story_title: str, metrics: Dict[str, Any]) -> str:
    """
    Create a basic fallback narrative if LLM generation fails

    Args:
        component_type: Type of component
        story_title: Story title
        metrics: Calculated metrics

    Returns:
        Simple fallback text
    """
    fallbacks = {
        'business_context': f"This analysis examines {story_title.lower()} to inform strategic decision-making and identify opportunities for improvement.",
        'opening_narrative': f"Our analysis of {story_title.lower()} reveals important patterns in the data that require attention.",
        'data_insights': f"Analysis of the data shows key metrics and trends across {story_title.lower()}. Further investigation of these patterns is recommended.",
        'business_impact': f"These findings have significant implications for institutional performance and should be considered in strategic planning.",
        'findings_summary': "• Key metrics identified\n• Patterns observed in the data\n• Areas requiring attention noted\n• Opportunities for improvement identified",
        'action_plan': "• Review findings with leadership team (Timeline: 30 days)\n• Develop detailed action plan (Timeline: 60 days)\n• Implement recommended changes (Timeline: 90 days)"
    }

    return fallbacks.get(component_type, f"Content for {component_type}")
