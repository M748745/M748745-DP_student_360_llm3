"""
Journey Assembly and Display System
Combines metrics + narratives into complete journey structures ready for UI display

Main workflow:
1. Load dataset
2. Validate required fields
3. Calculate metrics for all stories
4. Generate LLM narratives for all stories
5. Assemble into complete journey objects
6. Return ready-to-display journeys
"""

import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Import from other journey modules
from journey_definitions import (
    ALL_JOURNEYS,
    FINANCIAL_CONSTANTS,
    JOURNEY_1, JOURNEY_2, JOURNEY_3, JOURNEY_4, JOURNEY_5, JOURNEY_6
)
from journey_metrics import calculate_all_journey_metrics
from journey_narratives import generate_all_journeys_narratives, create_fallback_narrative


# ============================================================================
# VALIDATION
# ============================================================================

def validate_dataset_for_journeys(df: pd.DataFrame) -> Tuple[bool, List[str], Dict[str, List[str]]]:
    """
    Validate dataset has all required fields for journey generation

    Args:
        df: Student dataset DataFrame

    Returns:
        Tuple of:
        - is_valid: Boolean indicating if dataset is valid
        - missing_fields: List of critical missing fields
        - journey_validation: Dict mapping journey_id to list of missing fields per journey
    """
    all_missing = []
    journey_validation = {}

    # Check each journey's required fields
    for journey in ALL_JOURNEYS:
        journey_id = journey['id']
        required_fields = journey.get('required_fields', [])

        missing = [field for field in required_fields if field not in df.columns]

        if missing:
            journey_validation[journey_id] = missing
            all_missing.extend(missing)

        # Check story-level required fields
        for story in journey['stories']:
            story_required = story.get('required_fields', [])
            story_missing = [field for field in story_required if field not in df.columns]

            if story_missing:
                if journey_id not in journey_validation:
                    journey_validation[journey_id] = []
                journey_validation[journey_id].extend(story_missing)
                all_missing.extend(story_missing)

    # Remove duplicates
    all_missing = list(set(all_missing))

    # Dataset is valid if no critical fields are missing
    is_valid = len(all_missing) == 0

    return is_valid, all_missing, journey_validation


def get_dataset_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate summary statistics for the dataset

    Args:
        df: Student dataset DataFrame

    Returns:
        Dictionary with dataset summary statistics
    """
    summary = {
        'total_students': len(df),
        'total_columns': len(df.columns),
        'columns': list(df.columns),
        'date_analyzed': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'basic_stats': {
            'avg_gpa': round(df['cumulative_gpa'].mean(), 3) if 'cumulative_gpa' in df.columns else None,
            'total_nationalities': df['nationality'].nunique() if 'nationality' in df.columns else None,
            'active_students': len(df[df['enrollment_enrollment_status'] == 'Active']) if 'enrollment_enrollment_status' in df.columns else None,
        }
    }

    return summary


# ============================================================================
# STORY ASSEMBLY
# ============================================================================

def assemble_story(
    story_def: Dict[str, Any],
    metrics: Dict[str, Any],
    narratives: Dict[str, str]
) -> Dict[str, Any]:
    """
    Combine story definition, metrics, and narratives into complete story object

    Args:
        story_def: Story definition from journey_definitions.py
        metrics: Calculated metrics for this story
        narratives: Generated narratives for all components

    Returns:
        Complete story object with all data ready for display
    """
    story = {
        # Metadata
        'id': story_def['id'],
        'title': story_def['title'],
        'subtitle': story_def.get('subtitle', ''),
        'focus_area': story_def.get('focus_area', ''),

        # Metrics (raw data)
        'metrics': metrics,

        # Narratives (LLM-generated text)
        'business_context': narratives.get('business_context', ''),
        'opening_narrative': narratives.get('opening_narrative', ''),
        'data_insights': narratives.get('data_insights', ''),
        'business_impact': narratives.get('business_impact', ''),
        'findings_summary': narratives.get('findings_summary', ''),
        'action_plan': narratives.get('action_plan', ''),

        # Metadata
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'has_complete_data': all([
            narratives.get('business_context'),
            narratives.get('opening_narrative'),
            narratives.get('data_insights'),
            narratives.get('business_impact'),
            narratives.get('findings_summary'),
            narratives.get('action_plan')
        ])
    }

    return story


# ============================================================================
# JOURNEY ASSEMBLY
# ============================================================================

def assemble_journey(
    journey_def: Dict[str, Any],
    journey_metrics: Dict[str, Dict[str, Any]],
    journey_narratives: Dict[str, Dict[str, str]]
) -> Dict[str, Any]:
    """
    Combine journey definition, metrics, and narratives into complete journey

    Args:
        journey_def: Journey definition from journey_definitions.py
        journey_metrics: All metrics for this journey's stories
        journey_narratives: All narratives for this journey's stories

    Returns:
        Complete journey object with all stories assembled
    """
    stories = []

    # Assemble each story
    for story_def in journey_def['stories']:
        story_id = story_def['id']

        # Get metrics and narratives for this story
        metrics = journey_metrics.get(story_id, {})
        narratives = journey_narratives.get(story_id, {})

        # Assemble complete story
        story = assemble_story(story_def, metrics, narratives)
        stories.append(story)

    # Create complete journey object
    journey = {
        # Metadata
        'id': journey_def['id'],
        'name': journey_def['name'],
        'subtitle': journey_def.get('subtitle', ''),
        'priority': journey_def.get('priority', 999),

        # Stories (complete with metrics + narratives)
        'stories': stories,
        'story_count': len(stories),

        # Summary statistics
        'complete_stories': sum(1 for s in stories if s['has_complete_data']),
        'total_metrics_calculated': sum(len(s['metrics']) for s in stories),

        # Metadata
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'is_complete': all(s['has_complete_data'] for s in stories)
    }

    return journey


def assemble_all_journeys(
    all_metrics: Dict[str, Dict[str, Any]],
    all_narratives: Dict[str, Dict[str, Dict[str, str]]]
) -> List[Dict[str, Any]]:
    """
    Assemble all 6 journeys with their stories

    Args:
        all_metrics: All metrics organized by journey_id -> story_id -> metrics
        all_narratives: All narratives organized by journey_id -> story_id -> component -> text

    Returns:
        List of 6 complete journey objects, sorted by priority
    """
    journeys = []

    for journey_def in ALL_JOURNEYS:
        journey_id = journey_def['id']

        # Get metrics and narratives for this journey
        journey_metrics = all_metrics.get(journey_id, {})
        journey_narratives = all_narratives.get(journey_id, {})

        # Assemble complete journey
        journey = assemble_journey(journey_def, journey_metrics, journey_narratives)
        journeys.append(journey)

    # Sort by priority
    journeys.sort(key=lambda j: j['priority'])

    return journeys


# ============================================================================
# MAIN GENERATION PIPELINE
# ============================================================================

def generate_all_journeys(
    df: pd.DataFrame,
    query_llm_func,
    model: str,
    url: str,
    temperature: float = 0.4,
    timeout: int = 120,
    progress_callback=None
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Complete pipeline: Dataset → Metrics → Narratives → Assembled Journeys

    Args:
        df: Student dataset DataFrame
        query_llm_func: Function to call LLM (query_ollama from main app)
        model: LLM model name
        url: Ollama API URL
        temperature: LLM temperature for narratives
        timeout: Request timeout per narrative component
        progress_callback: Optional callback function(stage, current, total, message)

    Returns:
        Tuple of:
        - List of complete journey objects (6 journeys)
        - Metadata dictionary with generation statistics

    Progress stages:
        - 'validation': Validating dataset
        - 'metrics': Calculating metrics (current=story_idx, total=18)
        - 'narratives': Generating narratives (current=component_idx, total=108)
        - 'assembly': Assembling journeys (current=journey_idx, total=6)
    """
    metadata = {
        'start_time': datetime.now(),
        'dataset_summary': get_dataset_summary(df),
        'validation': {},
        'metrics': {},
        'narratives': {},
        'assembly': {},
        'errors': []
    }

    try:
        # ====================================================================
        # STAGE 1: VALIDATION
        # ====================================================================
        if progress_callback:
            progress_callback('validation', 0, 1, 'Validating dataset for journey requirements')

        is_valid, missing_fields, journey_validation = validate_dataset_for_journeys(df)

        metadata['validation'] = {
            'is_valid': is_valid,
            'missing_fields': missing_fields,
            'journey_validation': journey_validation
        }

        if not is_valid:
            error_msg = f"Dataset validation failed. Missing fields: {', '.join(missing_fields)}"
            metadata['errors'].append(error_msg)
            if progress_callback:
                progress_callback('validation', 1, 1, f'❌ {error_msg}')
            return [], metadata

        if progress_callback:
            progress_callback('validation', 1, 1, '✅ Dataset validation passed')

        # ====================================================================
        # STAGE 2: CALCULATE METRICS
        # ====================================================================
        if progress_callback:
            progress_callback('metrics', 0, 18, 'Calculating metrics for all stories')

        all_metrics = calculate_all_journey_metrics(df)

        # Count metrics
        total_metrics = sum(
            len(story_metrics)
            for journey_metrics in all_metrics.values()
            for story_metrics in journey_metrics.values()
        )

        metadata['metrics'] = {
            'total_stories': 18,
            'total_metrics_calculated': total_metrics,
            'journeys_processed': len(all_metrics)
        }

        if progress_callback:
            progress_callback('metrics', 18, 18, f'✅ {total_metrics} metrics calculated across 18 stories')

        # ====================================================================
        # STAGE 3: GENERATE NARRATIVES
        # ====================================================================
        # Total narrative components: 18 stories × 6 components = 108
        total_components = 18 * 6

        if progress_callback:
            progress_callback('narratives', 0, total_components,
                            'Generating LLM narratives for all story components')

        # Custom progress callback for narrative generation
        component_counter = [0]  # Mutable counter

        def narrative_progress(journey_name, current_story, total_stories, story_title):
            component_counter[0] += 6  # Each story has 6 components
            if progress_callback:
                progress_callback('narratives', component_counter[0], total_components,
                                f'{journey_name} - Story {current_story}/{total_stories}: {story_title}')

        all_narratives = generate_all_journeys_narratives(
            ALL_JOURNEYS,
            all_metrics,
            query_llm_func,
            model,
            url,
            temperature,
            timeout,
            narrative_progress
        )

        # Count narratives
        total_narratives = sum(
            len(story_narratives)
            for journey_narratives in all_narratives.values()
            for story_narratives in journey_narratives.values()
        )

        metadata['narratives'] = {
            'total_components_generated': total_narratives,
            'expected_components': total_components,
            'generation_complete': total_narratives == total_components
        }

        if progress_callback:
            progress_callback('narratives', total_components, total_components,
                            f'✅ {total_narratives} narrative components generated')

        # ====================================================================
        # STAGE 4: ASSEMBLE JOURNEYS
        # ====================================================================
        if progress_callback:
            progress_callback('assembly', 0, 6, 'Assembling complete journeys')

        journeys = assemble_all_journeys(all_metrics, all_narratives)

        metadata['assembly'] = {
            'total_journeys': len(journeys),
            'complete_journeys': sum(1 for j in journeys if j['is_complete']),
            'total_stories': sum(j['story_count'] for j in journeys)
        }

        if progress_callback:
            progress_callback('assembly', 6, 6,
                            f'✅ {len(journeys)} complete journeys assembled')

        # ====================================================================
        # COMPLETION
        # ====================================================================
        metadata['end_time'] = datetime.now()
        metadata['duration_seconds'] = (metadata['end_time'] - metadata['start_time']).total_seconds()
        metadata['success'] = True

        return journeys, metadata

    except Exception as e:
        error_msg = f"Error in journey generation pipeline: {str(e)}"
        metadata['errors'].append(error_msg)
        metadata['success'] = False
        metadata['end_time'] = datetime.now()

        if progress_callback:
            progress_callback('error', 0, 1, f'❌ {error_msg}')

        return [], metadata


# ============================================================================
# INDIVIDUAL JOURNEY GENERATION
# ============================================================================

def generate_single_journey(
    journey_id: str,
    df: pd.DataFrame,
    query_llm_func,
    model: str,
    url: str,
    temperature: float = 0.4,
    timeout: int = 120,
    progress_callback=None
) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any]]:
    """
    Generate a single journey (useful for testing or on-demand generation)

    Args:
        journey_id: ID of journey to generate ('journey_1', 'journey_2', etc.)
        df: Student dataset DataFrame
        query_llm_func: Function to call LLM
        model: LLM model name
        url: Ollama API URL
        temperature: LLM temperature
        timeout: Request timeout
        progress_callback: Optional callback function

    Returns:
        Tuple of:
        - Complete journey object (or None if failed)
        - Metadata dictionary
    """
    # Find journey definition
    journey_def = None
    for j in ALL_JOURNEYS:
        if j['id'] == journey_id:
            journey_def = j
            break

    if not journey_def:
        return None, {'error': f'Journey {journey_id} not found'}

    # Validate dataset
    is_valid, missing_fields, _ = validate_dataset_for_journeys(df)
    if not is_valid:
        return None, {'error': f'Dataset missing required fields: {missing_fields}'}

    # Calculate metrics for this journey
    if progress_callback:
        progress_callback('metrics', 0, 1, f'Calculating metrics for {journey_def["name"]}')

    all_metrics = calculate_all_journey_metrics(df)
    journey_metrics = all_metrics.get(journey_id, {})

    # Generate narratives for this journey
    if progress_callback:
        progress_callback('narratives', 0, len(journey_def['stories']),
                        f'Generating narratives for {journey_def["name"]}')

    from journey_narratives import generate_journey_narratives

    journey_narratives = generate_journey_narratives(
        journey_id,
        journey_def['name'],
        journey_def['stories'],
        journey_metrics,
        query_llm_func,
        model,
        url,
        temperature,
        timeout,
        progress_callback
    )

    # Assemble journey
    if progress_callback:
        progress_callback('assembly', 0, 1, f'Assembling {journey_def["name"]}')

    journey = assemble_journey(journey_def, journey_metrics, journey_narratives)

    metadata = {
        'journey_id': journey_id,
        'journey_name': journey_def['name'],
        'stories_generated': len(journey['stories']),
        'is_complete': journey['is_complete'],
        'generated_at': journey['generated_at']
    }

    if progress_callback:
        progress_callback('complete', 1, 1, f'✅ {journey_def["name"]} complete')

    return journey, metadata


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_journey_summary(journey: Dict[str, Any]) -> str:
    """
    Generate a text summary of a journey

    Args:
        journey: Complete journey object

    Returns:
        Formatted text summary
    """
    summary = f"""
Journey: {journey['name']}
Stories: {journey['story_count']}
Complete: {'Yes' if journey['is_complete'] else 'No'}
Total Metrics: {journey['total_metrics_calculated']}
Generated: {journey['generated_at']}

Stories:
"""

    for idx, story in enumerate(journey['stories'], 1):
        summary += f"  {idx}. {story['title']}\n"
        summary += f"     Metrics: {len(story['metrics'])} | Complete: {'✓' if story['has_complete_data'] else '✗'}\n"

    return summary


def export_journey_to_dict(journey: Dict[str, Any]) -> Dict[str, Any]:
    """
    Export journey to a clean dictionary format (for JSON export)

    Args:
        journey: Complete journey object

    Returns:
        Clean dictionary suitable for JSON serialization
    """
    return {
        'journey': {
            'id': journey['id'],
            'name': journey['name'],
            'subtitle': journey['subtitle'],
            'generated_at': journey['generated_at']
        },
        'stories': [
            {
                'id': story['id'],
                'title': story['title'],
                'subtitle': story['subtitle'],
                'business_context': story['business_context'],
                'opening_narrative': story['opening_narrative'],
                'data_insights': story['data_insights'],
                'business_impact': story['business_impact'],
                'findings_summary': story['findings_summary'],
                'action_plan': story['action_plan'],
                'metrics': story['metrics']
            }
            for story in journey['stories']
        ]
    }
