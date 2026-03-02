"""
Fully Dynamic Entity Discovery System
======================================

This system uses PURE LLM DISCOVERY with ZERO guidance or examples.
The LLM analyzes the dataset and discovers entities based solely on data patterns.

NO predefined entity types.
NO examples.
NO templates.

PURE DATA-DRIVEN DISCOVERY.

Author: AI Assistant
Date: 2026-01-18
Updated: 2026-02-03 - Added support for remote Ollama (Cloudflare)
"""

import pandas as pd
import json
import re
import requests
from typing import Dict, List, Any, Optional


# ============================================================================
# ROBUST JSON EXTRACTION
# ============================================================================

def extract_json_from_response(text: str) -> str:
    """
    Robustly extract a JSON array or object from an LLM response that may
    contain markdown fences, preamble text, trailing commentary, or
    partial/malformed output.

    Strategy (in order):
    1. Strip markdown code fences (```json ... ``` or ``` ... ```)
    2. Find the first '[' or '{' and the matching closing bracket
    3. Fix common LLM JSON mistakes:
       - Trailing commas before ] or }
       - Single-quoted strings  →  double-quoted
       - Unquoted keys
       - Ellipsis / placeholder values
    4. Return the cleaned string ready for json.loads()
    """

    if not text:
        return text

    # 1. Strip markdown fences
    fence_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
    if fence_match:
        text = fence_match.group(1).strip()

    # 2. Find outermost JSON structure
    start_idx = -1
    start_char = None
    for i, ch in enumerate(text):
        if ch in ('[', '{'):
            start_idx = i
            start_char = ch
            break

    if start_idx == -1:
        return text  # nothing to extract

    end_char = ']' if start_char == '[' else '}'
    depth = 0
    end_idx = -1
    in_string = False
    escape_next = False

    for i in range(start_idx, len(text)):
        ch = text[i]
        if escape_next:
            escape_next = False
            continue
        if ch == '\\' and in_string:
            escape_next = True
            continue
        if ch == '"' and not escape_next:
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == start_char:
            depth += 1
        elif ch == end_char:
            depth -= 1
            if depth == 0:
                end_idx = i
                break

    if end_idx == -1:
        # Truncated response — reconstruct a parseable fragment
        text = text[start_idx:].rstrip()

        # If we're mid-string (odd number of unescaped quotes after start),
        # close the string first so JSON structure is valid
        quote_count = text.count('"') - text.count('\\"')
        if quote_count % 2 == 1:
            text = text + '"'

        # Drop any dangling comma or incomplete key-value pair
        text = text.rstrip().rstrip(',')

        # Remove the last incomplete object if it looks unfinished
        # (last '{' has no matching '}')
        last_open = text.rfind('{')
        last_close = text.rfind('}')
        if last_open > last_close:
            text = text[:last_open].rstrip().rstrip(',')

        # Close all open brackets/braces
        open_braces = text.count('{') - text.count('}')
        open_brackets = text.count('[') - text.count(']')
        text = text + ('}' * max(0, open_braces)) + (']' * max(0, open_brackets))
    else:
        text = text[start_idx:end_idx + 1]

    # 3. Fix common LLM JSON mistakes

    # Trailing commas before closing bracket/brace  e.g.  [...,]  or  {...,}
    text = re.sub(r',\s*([}\]])', r'\1', text)

    # Replace single-quoted JSON values/keys with double-quoted.
    # Only match quotes that follow a JSON structural character (: [ , {)
    # or start of line — NOT apostrophes inside words like "student's".
    text = re.sub(r"(?<=[:\[,{\s])'([^']*?)'(?=\s*[,\]}\s])", r'"\1"', text)

    # Remove JavaScript-style comments
    text = re.sub(r'//[^\n]*', '', text)
    text = re.sub(r'/\*[\s\S]*?\*/', '', text)

    # Ellipsis placeholders that break JSON
    text = re.sub(r'\.\.\.', '""', text)

    # Python/JS boolean literals → JSON booleans
    # Use word-boundary so we don't mangle strings containing "True"/"False"
    text = re.sub(r'\bTrue\b', 'true', text)
    text = re.sub(r'\bFalse\b', 'false', text)
    text = re.sub(r'\bNone\b', 'null', text)

    return text.strip()

# ============================================================================
# OLLAMA API HELPER (supports both local and remote)
# ============================================================================

def call_ollama_api(prompt: str, model: str, ollama_url: str, temperature: float = 0.3, num_predict: int = 2000) -> str:
    """
    Call Ollama API via HTTP requests (works with both local and Cloudflare)

    Args:
        prompt: The prompt text
        model: Model name
        ollama_url: Ollama server URL (local or Cloudflare)
        temperature: Temperature setting
        num_predict: Max tokens to generate

    Returns:
        Response text from LLM
    """
    try:
        # Determine timeout based on URL type
        is_remote = "cloudflare" in ollama_url.lower() or "https://" in ollama_url.lower()
        timeout = 300 if is_remote else 60  # 5 minutes for Cloudflare (increased for Streamlit Cloud)

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": num_predict
            }
        }

        response = requests.post(
            f"{ollama_url}/api/generate",
            json=payload,
            timeout=timeout
        )

        if response.status_code == 200:
            return response.json()['response']
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")

    except Exception as e:
        raise Exception(f"Ollama API call failed: {str(e)}")

# ============================================================================
# PHASE 1: AUTONOMOUS ENTITY DISCOVERY (NO GUIDANCE)
# ============================================================================

def discover_entities_autonomously(df: pd.DataFrame, ollama_model: str = "qwen2.5:7b", ollama_url: str = "http://localhost:11434") -> List[Dict[str, Any]]:
    """
    Phase 1: PURE autonomous entity discovery - NO examples, NO guidance.

    The LLM must discover entities by analyzing data patterns alone.

    Args:
        df: The student dataset
        ollama_model: The Ollama model to use

    Returns:
        List of discovered entities
    """

    # Get raw dataset statistics
    dataset_analysis = analyze_dataset_patterns(df)

    prompt = f"""You are analyzing a higher education dataset. Your task is to discover ENTITIES that exist in this data.

**WHAT IS AN ENTITY:**
An entity is a THING that:
1. Has a LIFECYCLE - it progresses through stages over time
2. Has STATUS CHANGES - it can be in different states
3. EVOLVES - its characteristics change

**DO NOT use any predetermined categories. DISCOVER entities from the data patterns below.**

**Dataset Analysis:**
{dataset_analysis}

**Your Task:**
Analyze the data patterns and discover 6-8 entities that have lifecycles. Base your discovery PURELY on what the data reveals.

**Discovery Process:**
1. Look for patterns in the data (correlations, distributions, trends)
2. Identify THINGS that change over time or have different states
3. Find groupings that reveal a progression or lifecycle
4. Discover relationships that suggest an entity's journey

**Rules:**
- DO NOT use predetermined entity types
- DISCOVER entities from data patterns
- Each entity must have a clear lifecycle (beginning → middle → end)
- Each entity must be trackable through different statuses
- Base entity names on what the DATA shows, not on assumptions

**Output Format (JSON only, no explanations):**
[
  {{
    "entity_id": "<unique_identifier>",
    "entity_name": "<descriptive name based on data patterns>",
    "entity_type": "<type you discovered>",
    "description": "<what this entity represents based on data>",
    "data_filter": {{"field": "value"}},
    "discovery_rationale": "<why this is an entity - what patterns in the data revealed it>",
    "student_count": <number>,
    "priority": <1-10>,
    "lifecycle_indicators": ["<status 1>", "<status 2>", ...]
  }}
]

**IMPORTANT:**
- Return ONLY valid JSON array, no markdown
- Base everything on DATA PATTERNS, not assumptions
- Discover 6-8 entities
- Each entity must be justified by data patterns
- Be creative - discover what's actually in the data"""

    raw_response = ""
    try:
        print(f"🔄 Calling LLM for autonomous entity discovery...")
        raw_response = call_ollama_api(
            prompt=prompt,
            model=ollama_model,
            ollama_url=ollama_url,
            temperature=0.7,  # Higher temperature for creative discovery
            num_predict=4000  # 6-8 entities need more tokens; 2500 was truncating
        ).strip()

        print(f"📝 LLM Response (first 500 chars): {raw_response[:500]}")

        # Robustly extract and clean JSON from any LLM response format
        entities_json = extract_json_from_response(raw_response)

        print(f"🧹 Cleaned JSON (first 500 chars): {entities_json[:500]}")

        entities = json.loads(entities_json)

        # Ensure we got a list
        if isinstance(entities, dict):
            entities = [entities]

        print(f"✅ DISCOVERED {len(entities)} entities autonomously from data patterns")
        return entities

    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {str(e)}")
        # Print chars around the exact error position so we can see what's wrong
        err_pos = e.pos if hasattr(e, 'pos') else 0
        snippet_start = max(0, err_pos - 80)
        snippet_end = min(len(raw_response), err_pos + 80)
        print(f"❌ Error at char {err_pos}: ...{repr(raw_response[snippet_start:snippet_end])}...")
        print(f"❌ Full raw response:\n{raw_response}")
        return []
    except Exception as e:
        print(f"❌ Error in autonomous entity discovery: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        print(traceback.format_exc())
        return []


# ============================================================================
# PHASE 2: AUTONOMOUS STAGE DISCOVERY
# ============================================================================

def discover_stages_autonomously(
    entity: Dict[str, Any],
    df: pd.DataFrame,
    ollama_model: str = "qwen2.5:7b",
    ollama_url: str = "http://localhost:11434"
) -> List[Dict[str, Any]]:
    """
    Phase 2: Discover journey stages autonomously based on entity data patterns.

    NO predetermined stage templates. LLM discovers stages from data.

    Args:
        entity: Discovered entity from Phase 1
        df: The student dataset
        ollama_model: The Ollama model to use
        ollama_url: Ollama server URL (local or Cloudflare)

    Returns:
        List of discovered stages
    """

    # Filter dataset for this entity
    from llm_entity_journey_system import filter_dataset_for_entity
    entity_data = filter_dataset_for_entity(df, entity)

    # Analyze entity data patterns
    entity_patterns = analyze_entity_patterns(entity_data)

    prompt = f"""You are analyzing a specific entity discovered in the data. Your task is to discover its LIFECYCLE STAGES.

**Entity Discovered:**
- Name: {entity['entity_name']}
- Type: {entity['entity_type']}
- Description: {entity['description']}
- Discovery Rationale: {entity.get('discovery_rationale', 'N/A')}

**Entity Data Patterns:**
{entity_patterns}

**Your Task:**
Analyze the data patterns and discover 4-6 lifecycle stages for this entity. Base your discovery PURELY on what the data reveals.

**Discovery Process:**
1. Look for natural transitions in the data (performance changes, status shifts, time-based progression)
2. Identify milestones or inflection points
3. Find patterns that suggest different phases
4. Discover the natural progression this entity follows

**Rules:**
- DO NOT use predetermined stage names
- DISCOVER stages from data patterns
- Each stage must be evident in the data
- Stages should follow a logical progression
- Base stage names on what the DATA shows

**Output Format (JSON only):**
[
  {{
    "stage_id": "<unique_id>",
    "stage_name": "<name based on data pattern>",
    "stage_order": <1, 2, 3...>,
    "description": "<what happens in this stage based on data>",
    "discovery_rationale": "<what data patterns revealed this stage>",
    "data_indicators": ["<metric 1>", "<metric 2>", ...]
  }}
]

**IMPORTANT:**
- Return ONLY valid JSON, no markdown
- Discover stages from DATA PATTERNS
- Include 4-6 stages in logical order
- Each stage must be justified by data evidence"""

    raw_response = ""
    try:
        raw_response = call_ollama_api(
            prompt=prompt,
            model=ollama_model,
            ollama_url=ollama_url,
            temperature=0.7,
            num_predict=3000  # increased — 1800 was truncating longer stage lists
        ).strip()

        print(f"  📝 Stage LLM Response (first 300 chars): {raw_response[:300]}")

        # Robustly extract and clean JSON from any LLM response format
        stages_json = extract_json_from_response(raw_response)

        stages = json.loads(stages_json)

        # Ensure we got a list
        if isinstance(stages, dict):
            stages = [stages]

        print(f"  ✅ DISCOVERED {len(stages)} stages for {entity['entity_name']}")
        return stages

    except json.JSONDecodeError as e:
        print(f"  ❌ JSON parsing error in stage discovery: {str(e)}")
        print(f"  ❌ Raw response: {raw_response[:2000]}")
        return []
    except Exception as e:
        print(f"  ❌ Error discovering stages: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return []


# ============================================================================
# PHASE 3: NARRATIVE + VISUALIZATION GENERATION (SAME AS GUIDED)
# ============================================================================

def generate_narrative_for_discovered_stage(
    entity: Dict[str, Any],
    stage: Dict[str, Any],
    df: pd.DataFrame,
    ollama_model: str = "qwen2.5:7b"
) -> Dict[str, Any]:
    """
    Phase 3: Generate narrative for a discovered stage.

    This is the same as the guided version since we're telling the story
    of what we discovered.
    """

    from llm_entity_journey_system import (
        filter_dataset_for_entity,
        calculate_stage_metrics,
        generate_narrative_for_stage
    )

    # Use the same narrative generation since we're just describing what we found
    return generate_narrative_for_stage(entity, stage, df, ollama_model)


# ============================================================================
# COMPLETE AUTONOMOUS DISCOVERY PIPELINE
# ============================================================================

def generate_fully_dynamic_journeys(df: pd.DataFrame, ollama_model: str = "qwen2.5:7b", ollama_url: str = "http://localhost:11434") -> List[Dict[str, Any]]:
    """
    Complete autonomous discovery pipeline with ZERO guidance.

    Pipeline:
    1. LLM discovers entities from data patterns (NO examples)
    2. LLM discovers stages for each entity (NO templates)
    3. LLM generates narratives and visualizations

    Args:
        df: Student dataset
        ollama_model: Ollama model to use
        ollama_url: Ollama server URL (local or Cloudflare)

    Returns:
        List of complete journeys discovered autonomously
    """

    print("\n" + "="*80)
    print("🔬 FULLY AUTONOMOUS ENTITY DISCOVERY (NO GUIDANCE)")
    print("="*80 + "\n")

    all_journeys = []

    # PHASE 1: Discover entities autonomously
    print("🔍 PHASE 1: Discovering entities from data patterns (NO examples)...")
    entities = discover_entities_autonomously(df, ollama_model, ollama_url)

    if not entities:
        print("❌ No entities discovered. Aborting.")
        return []

    print(f"\n✅ DISCOVERED {len(entities)} entities autonomously:\n")
    for ent in entities:
        print(f"   • {ent['entity_name']} ({ent['entity_type']}) - {ent.get('discovery_rationale', 'N/A')[:80]}...")

    # PHASE 2 & 3: For each discovered entity, discover stages and generate narratives
    for idx, entity in enumerate(entities, 1):
        print(f"\n{'='*80}")
        print(f"🎯 Processing Discovered Entity {idx}/{len(entities)}: {entity['entity_name']}")
        print(f"{'='*80}\n")

        # Discover stages autonomously
        print(f"  🔍 PHASE 2: Discovering lifecycle stages from data patterns...")
        stages = discover_stages_autonomously(entity, df, ollama_model, ollama_url)

        if not stages:
            print(f"  ❌ No stages discovered for {entity['entity_name']}, skipping.")
            continue

        # Generate narratives for discovered stages
        print(f"\n  ✍️  PHASE 3: Generating narratives for {len(stages)} discovered stages...")
        stage_narratives = []

        for stage in stages:
            narrative = generate_narrative_for_discovered_stage(entity, stage, df, ollama_model)
            stage_narratives.append({
                **stage,
                **narrative
            })

        # Compile complete journey
        complete_journey = {
            **entity,
            'stages': stage_narratives,
            'total_stages': len(stage_narratives),
            'discovery_method': 'FULLY_AUTONOMOUS'
        }

        all_journeys.append(complete_journey)

        print(f"\n  ✅ Completed autonomous discovery for {entity['entity_name']}")

    print("\n" + "="*80)
    print(f"✅ AUTONOMOUS DISCOVERY COMPLETE - {len(all_journeys)} journeys discovered")
    print("="*80 + "\n")

    return all_journeys


# ============================================================================
# HELPER FUNCTIONS - DATA PATTERN ANALYSIS
# ============================================================================

def analyze_dataset_patterns(df: pd.DataFrame) -> str:
    """
    Analyze dataset to reveal patterns for entity discovery.

    NO assumptions - just raw data patterns.
    """

    analysis = f"""
DATASET SIZE: {len(df)} records

AVAILABLE FIELDS: {', '.join(df.columns.tolist())}

FIELD ANALYSIS:
"""

    # Analyze each field
    for col in df.columns:
        if df[col].dtype == 'object' or df[col].nunique() < 50:
            # Categorical field
            unique_count = df[col].nunique()
            top_values = df[col].value_counts().head(5)
            analysis += f"\n{col}: {unique_count} unique values\n"
            analysis += f"  Top values: {dict(top_values)}\n"
        else:
            # Numerical field
            analysis += f"\n{col}: Numeric field\n"
            analysis += f"  Range: {df[col].min():.2f} - {df[col].max():.2f}\n"
            analysis += f"  Mean: {df[col].mean():.2f}, Median: {df[col].median():.2f}\n"

    # Correlation patterns
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 1:
        analysis += "\nCORRELATION PATTERNS:\n"
        corr_matrix = df[numeric_cols].corr()

        # Find strong correlations
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.3:
                    analysis += f"  {corr_matrix.columns[i]} <-> {corr_matrix.columns[j]}: {corr_value:.2f}\n"

    return analysis


def analyze_entity_patterns(entity_df: pd.DataFrame) -> str:
    """Analyze patterns within a specific entity's data."""

    if len(entity_df) == 0:
        return "No data available."

    analysis = f"""
ENTITY SIZE: {len(entity_df)} records

FIELD DISTRIBUTIONS:
"""

    for col in entity_df.columns:
        if entity_df[col].dtype == 'object' or entity_df[col].nunique() < 20:
            unique_count = entity_df[col].nunique()
            analysis += f"{col}: {unique_count} unique values\n"
        else:
            analysis += f"{col}: Range {entity_df[col].min():.2f} - {entity_df[col].max():.2f}\n"

    return analysis
