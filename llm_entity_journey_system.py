"""
LLM-Driven Entity Journey System
=================================

This system uses LLM to:
1. Identify meaningful entities from the dataset
2. Define journey stages for each entity
3. Generate narratives that tell the story of each entity's lifecycle

Author: AI Assistant
Date: 2026-01-18
Updated: 2026-02-03 - Added support for remote Ollama (Cloudflare)
"""

import pandas as pd
import json
import requests
import re
from typing import Dict, List, Any, Optional

# ============================================================================
# DYNAMIC MODEL DETECTION (no hardcoding required)
# ============================================================================

def detect_model_tier(model_name: str) -> Dict[str, Any]:
    """
    Dynamically detect model capabilities from model name.
    Works with ANY model without hardcoding.

    Args:
        model_name: Any model name (e.g., "qwen2.5:3b", "llama3.3:70b", "custom-model")

    Returns:
        Dict with adaptive configuration
    """
    model_lower = model_name.lower()

    # Extract parameter size using regex (matches patterns like "3b", "7b", "70b")
    size_match = re.search(r'(\d+)b', model_lower)
    param_size = int(size_match.group(1)) if size_match else None

    # Determine tier based on parameter size
    if param_size:
        if param_size <= 4:
            tier = "small"
        elif param_size <= 13:
            tier = "medium"
        else:
            tier = "large"
    else:
        # Fallback: infer from common model families
        if "3b" in model_lower or "1b" in model_lower or "0.5b" in model_lower:
            tier = "small"
        elif "70b" in model_lower or "65b" in model_lower or "72b" in model_lower:
            tier = "large"
        else:
            # Default to medium for unknown models
            tier = "medium"
            param_size = 7  # Assume ~7B

    # Return adaptive configuration based on tier
    if tier == "small":
        return {
            "tier": "small",
            "param_size": param_size or 3,
            "base_timeout_local": 120,
            "base_timeout_remote": 180,
            "entity_token_limits": [2500, 3000, 3500],
            "stage_token_limits": [1200, 1500, 1800],
            "narrative_token_limits": [1500, 2000, 2500],
            "max_entities": 4,
            "temperature": 0.4
        }
    elif tier == "large":
        return {
            "tier": "large",
            "param_size": param_size or 70,
            "base_timeout_local": 360,
            "base_timeout_remote": 480,
            "entity_token_limits": [5000, 6000, 8000],
            "stage_token_limits": [3000, 4000, 5000],
            "narrative_token_limits": [3500, 4500, 6000],
            "max_entities": 8,
            "temperature": 0.2
        }
    else:  # medium (default)
        return {
            "tier": "medium",
            "param_size": param_size or 7,
            "base_timeout_local": 240,
            "base_timeout_remote": 300,
            "entity_token_limits": [4000, 5000, 6000],
            "stage_token_limits": [2000, 2500, 3000],
            "narrative_token_limits": [2500, 3000, 3500],
            "max_entities": 6,
            "temperature": 0.3
        }

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
        # Dynamically detect model capabilities and adjust timeout
        model_config = detect_model_tier(model)
        is_remote = "cloudflare" in ollama_url.lower() or "https://" in ollama_url.lower()

        # Use adaptive timeout based on model size and server location
        timeout = model_config["base_timeout_remote"] if is_remote else model_config["base_timeout_local"]

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
# JSON SANITIZATION HELPER
# ============================================================================

def sanitize_json_string(json_str: str) -> str:
    """
    Sanitize JSON string by removing bare control characters that are
    illegal in JSON.  Newlines/tabs that sit OUTSIDE string values are
    fine (they are whitespace); only those INSIDE string values need to
    be escaped — but we cannot know which is which without a full parse.
    Safe strategy: remove NUL and other non-printable control chars
    (0x00-0x08, 0x0B-0x0C, 0x0E-0x1F) and leave newline/tab alone so
    the JSON structure itself is not corrupted.
    """
    # Remove truly illegal control chars (not tab/LF/CR which are valid whitespace)
    control_chars = ''.join(chr(i) for i in range(0, 32) if i not in (9, 10, 13))
    for char in control_chars:
        json_str = json_str.replace(char, '')
    return json_str


def _extract_json_from_llm(text: str) -> str:
    """
    Extract a JSON object or array from raw LLM output, handling:
    - Markdown fences (```json ... ```)
    - Preamble text before the first [ or {
    - Trailing text / commentary after the closing ] or }
    - Truncated output (unclosed brackets)
    - Trailing commas, single-quoted strings, JS comments, ellipsis
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
        return text

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

        # If we're mid-string (odd number of unescaped quotes), close it
        quote_count = text.count('"') - text.count('\\"')
        if quote_count % 2 == 1:
            text = text + '"'

        text = text.rstrip().rstrip(',')

        # Drop last incomplete object if unfinished
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
    text = re.sub(r',\s*([}\]])', r'\1', text)           # trailing commas
    # Replace single-quoted JSON values/keys — NOT apostrophes in words like "student's"
    text = re.sub(r"(?<=[:\[,{\s])'([^']*?)'(?=\s*[,\]}\s])", r'"\1"', text)
    text = re.sub(r'//[^\n]*', '', text)                  # JS // comments
    text = re.sub(r'/\*[\s\S]*?\*/', '', text)            # JS /* */ comments
    text = re.sub(r'\.\.\.', '""', text)                  # ellipsis placeholders
    text = re.sub(r'\bTrue\b', 'true', text)              # Python True → JSON true
    text = re.sub(r'\bFalse\b', 'false', text)            # Python False → JSON false
    text = re.sub(r'\bNone\b', 'null', text)              # Python None → JSON null

    return text.strip()


def parse_json_with_fallback(json_str: str):
    """
    Parse JSON with multiple fallback strategies.

    Args:
        json_str: JSON string to parse (may be raw LLM output)

    Returns:
        Parsed dictionary/list, or empty dict/list on total failure
    """
    # Strategy 1: Direct parse (handles clean JSON)
    try:
        return json.loads(json_str, strict=False)
    except json.JSONDecodeError:
        pass

    # Strategy 2: Full extraction + cleaning pipeline
    try:
        cleaned = _extract_json_from_llm(json_str)
        return json.loads(cleaned, strict=False)
    except (json.JSONDecodeError, Exception):
        pass

    # Strategy 3: Sanitize control chars then try extraction again
    try:
        sanitized = sanitize_json_string(json_str)
        cleaned = _extract_json_from_llm(sanitized)
        return json.loads(cleaned, strict=False)
    except (json.JSONDecodeError, Exception):
        pass

    # Strategy 4: strict=False on sanitized raw string
    try:
        sanitized = sanitize_json_string(json_str)
        return json.loads(sanitized, strict=False)
    except json.JSONDecodeError:
        pass

    # All strategies failed
    json_str_stripped = json_str.strip()
    if json_str_stripped.startswith('['):
        return []
    else:
        return {}

# ============================================================================
# PHASE 1: ENTITY IDENTIFICATION
# ============================================================================

def identify_entities_from_dataset(df: pd.DataFrame, ollama_model: str = "qwen2.5:7b", ollama_url: str = "http://localhost:11434") -> List[Dict[str, Any]]:
    """
    Phase 1: LLM analyzes dataset and identifies meaningful entities for journey analysis.

    Args:
        df: The student dataset
        ollama_model: The Ollama model to use
        ollama_url: Ollama server URL (local or Cloudflare)

    Returns:
        List of entity definitions with:
        - entity_id: Unique identifier
        - entity_name: Human-readable name
        - entity_type: Type (cohort, program, service, revenue_segment, etc.)
        - description: What this entity represents
        - data_filter: How to filter the dataset for this entity
        - priority: 1-10 (higher = more important)
    """

    # Get dataset summary for LLM
    dataset_summary = generate_dataset_summary(df)

    # Dynamically adapt to model capabilities
    model_config = detect_model_tier(ollama_model)
    max_entities = model_config["max_entities"]

    print(f"🤖 Model: {ollama_model} ({model_config['tier']} tier, ~{model_config['param_size']}B parameters)")
    print(f"🎯 Target entities: {max_entities}")
    print(f"⏱️  Timeout: {model_config['base_timeout_local']}s (local) / {model_config['base_timeout_remote']}s (remote)")

    prompt = f"""You are analyzing a higher education institution's student dataset to identify meaningful entities for journey analysis.

**Dataset Summary:**
{dataset_summary}

**Your Task:**
Identify EXACTLY {max_entities} meaningful ENTITIES that have a LIFECYCLE and can exist in different STATUSES. An entity is something that evolves through stages over time.

**IMPORTANT: Generate exactly {max_entities} entities - no more, no less.**

**WHAT IS AN ENTITY:**
An entity is a THING that has:
1. **Lifecycle stages** - It progresses through different phases (beginning → middle → end)
2. **Status changes** - It can be in different states (active, at-risk, successful, failed)
3. **Evolution over time** - It changes and develops

**TRUE ENTITY TYPES TO IDENTIFY:**

1. **STUDENT Entity** - Individual students or student status groups
   - Lifecycle: Enrollment → Academic Progress → Performance Status → Graduation/Dropout
   - Statuses: Active, At-Risk, High-Performing, On Probation, Graduated
   - Example: "Student Academic Journey", "Student Retention Journey"

2. **ACADEMIC PROGRAM Entity** - Programs as living entities
   - Lifecycle: Program Launch → Growth → Maturity → Optimization
   - Statuses: New, Growing, Established, Declining
   - Example: "Academic Program Lifecycle", "Program Performance Journey"

3. **FINANCIAL AID Entity** - Aid as a lifecycle process
   - Lifecycle: Application → Approval → Disbursement → Impact Assessment
   - Statuses: Pending, Active, Effective, Ineffective
   - Example: "Financial Aid Lifecycle", "Aid Effectiveness Journey"

4. **ENROLLMENT Entity** - Enrollment as a process
   - Lifecycle: Application → Acceptance → Registration → Retention
   - Statuses: Applicant, Accepted, Enrolled, Retained, Dropped
   - Example: "Enrollment Journey", "Student Acquisition Journey"

5. **CAMPUS/FACILITY Entity** - Physical operations
   - Lifecycle: Opening → Expansion → Optimization
   - Statuses: Under-utilized, Optimal, Over-capacity
   - Example: "Campus Operations Journey", "Dormitory Lifecycle"

6. **REVENUE/PAYMENT Entity** - Financial flows
   - Lifecycle: Tuition Assessment → Payment → Collection → Revenue Recognition
   - Statuses: Pending, Paid, Overdue, Defaulted
   - Example: "Revenue Journey", "Payment Collection Journey"

**CRITICAL RULES:**
- ❌ DO NOT create simple groupings (e.g., "Engineering Students", "Business Program")
- ✅ CREATE lifecycle entities (e.g., "Student Academic Journey", "Program Lifecycle")
- ❌ DO NOT filter by nationality, gender, or demographics
- ✅ FILTER by lifecycle stage, status, or operational category
- Think: "What THING has a lifecycle in this institution?"

**Output Format (JSON only, no explanations):**
[
  {{
    "entity_id": "student_academic_journey",
    "entity_name": "Student Academic Journey",
    "entity_type": "student_lifecycle",
    "description": "Tracks student progression from enrollment through academic performance to graduation or dropout",
    "data_filter": {{}},
    "student_count": 1000,
    "priority": 10,
    "why_important": "Core entity representing student lifecycle and institutional success metrics",
    "lifecycle_stages": ["Enrollment", "First Semester", "Academic Progress", "Performance Trends", "Retention/Graduation"]
  }},
  {{
    "entity_id": "financial_aid_lifecycle",
    "entity_name": "Financial Aid Journey",
    "entity_type": "aid_lifecycle",
    "description": "Tracks financial aid from allocation through impact on student performance and retention",
    "data_filter": {{"Total_Aid": "> 0"}},
    "student_count": 800,
    "priority": 9,
    "why_important": "Critical financial entity affecting both student success and institutional revenue",
    "lifecycle_stages": ["Aid Allocation", "Disbursement", "Performance Impact", "Retention Effect", "ROI Assessment"]
  }},
  {{
    "entity_id": "academic_program_evolution",
    "entity_name": "Academic Program Lifecycle",
    "entity_type": "program_lifecycle",
    "description": "Tracks how academic programs evolve from launch to maturity with enrollment and performance trends",
    "data_filter": {{}},
    "student_count": 1000,
    "priority": 8,
    "why_important": "Programs are living entities that grow, mature, and require strategic management",
    "lifecycle_stages": ["Program Portfolio", "Enrollment Trends", "Performance Patterns", "Resource Allocation", "Strategic Position"]
  }}
]

**IMPORTANT:**
- Return ONLY valid JSON array, no markdown
- Include EXACTLY {max_entities} LIFECYCLE entities
- Think about what has a LIFECYCLE, not what is a GROUP
- Entities should have STATUS CHANGES (e.g., student goes from enrolled → at-risk → graduated)
- Include "lifecycle_stages" showing the progression phases
- data_filter can be empty {{}} if entity covers all students"""

    # Try up to 3 times with increasing token limits (adaptive based on model)
    max_retries = 3
    token_limits = model_config["entity_token_limits"]

    for attempt in range(max_retries):
        try:
            current_token_limit = token_limits[attempt]
            print(f"🔄 Attempt {attempt + 1}/{max_retries}: Calling LLM for entity identification (tokens: {current_token_limit})...")

            entities_json = call_ollama_api(
                prompt=prompt,
                model=ollama_model,
                ollama_url=ollama_url,
                temperature=model_config["temperature"],  # Adaptive temperature
                num_predict=current_token_limit
            ).strip()

            print(f"📝 LLM Response length: {len(entities_json)} chars")
            print(f"📝 LLM Response (first 500 chars): {entities_json[:500]}")
            print(f"📝 LLM Response (last 200 chars): {entities_json[-200:]}")

            # Clean JSON if wrapped in markdown
            if '```json' in entities_json:
                entities_json = entities_json.split('```json')[1].split('```')[0].strip()
            elif '```' in entities_json:
                entities_json = entities_json.split('```')[1].split('```')[0].strip()

            # Remove any text before the first '[' and after the last ']'
            if '[' in entities_json and ']' in entities_json:
                start_idx = entities_json.find('[')
                end_idx = entities_json.rfind(']') + 1
                entities_json = entities_json[start_idx:end_idx]

            print(f"🧹 Cleaned JSON length: {len(entities_json)} chars")
            print(f"🧹 Cleaned JSON (first 500 chars): {entities_json[:500]}")

            # Use robust JSON parsing
            entities = parse_json_with_fallback(entities_json)

            if not entities or len(entities) == 0 or not isinstance(entities, list):
                print(f"⚠️ Attempt {attempt + 1}: LLM returned empty entity list, retrying...")
                continue

            # Check if we got the target number of entities
            if len(entities) != max_entities:
                print(f"⚠️ Attempt {attempt + 1}: LLM returned {len(entities)} entities instead of {max_entities}, retrying...")
                if attempt < max_retries - 1:
                    continue
                else:
                    # On last attempt, accept what we got if it's at least half the target
                    min_acceptable = max(2, max_entities // 2)
                    if len(entities) >= min_acceptable:
                        print(f"✅ Accepted {len(entities)} entities (target was {max_entities})")
                        return entities
                    else:
                        continue

            print(f"✅ Identified {len(entities)} entities from dataset")
            return entities

        except json.JSONDecodeError as e:
            print(f"❌ Attempt {attempt + 1}: JSON parsing error: {str(e)}")
            print(f"❌ Raw response length: {len(entities_json) if 'entities_json' in locals() else 0}")
            if 'entities_json' in locals():
                print(f"❌ Raw response (first 1000 chars): {entities_json[:1000]}")
                print(f"❌ Raw response (last 500 chars): {entities_json[-500:]}")

            if attempt < max_retries - 1:
                print(f"🔄 Retrying with more tokens...")
            else:
                print(f"❌ All {max_retries} attempts failed")
                return []

        except Exception as e:
            print(f"❌ Attempt {attempt + 1}: Error in entity identification: {str(e)}")
            print(f"❌ Error type: {type(e).__name__}")
            import traceback
            print(traceback.format_exc())

            if attempt < max_retries - 1:
                print(f"🔄 Retrying...")
            else:
                print(f"❌ All {max_retries} attempts failed")
                return []

    return []


# ============================================================================
# PHASE 2: JOURNEY STAGE DEFINITION
# ============================================================================

def define_journey_stages_for_entity(
    entity: Dict[str, Any],
    df: pd.DataFrame,
    ollama_model: str = "qwen2.5:7b",
    ollama_url: str = "http://localhost:11434"
) -> List[Dict[str, Any]]:
    """
    Phase 2: LLM defines journey stages for a specific entity.

    Args:
        entity: Entity definition from Phase 1
        df: The student dataset
        ollama_model: The Ollama model to use
        ollama_url: Ollama server URL (local or Cloudflare)

    Returns:
        List of journey stages with:
        - stage_id: Unique identifier
        - stage_name: Human-readable name
        - stage_order: 1, 2, 3, etc.
        - description: What happens in this stage
        - metrics_to_track: Key metrics for this stage
    """

    # Filter dataset for this entity
    entity_data = filter_dataset_for_entity(df, entity)
    entity_summary = generate_entity_data_summary(entity_data, entity)

    prompt = f"""You are defining the journey stages for a specific entity in a higher education context.

**Entity Information:**
- Name: {entity['entity_name']}
- Type: {entity['entity_type']}
- Description: {entity['description']}
- Student Count: {entity.get('student_count', 'N/A')}

**Entity Data Summary:**
{entity_summary}

**Your Task:**
Define 4-6 journey stages that track this entity's lifecycle through the institution. Each stage should represent a meaningful milestone, transition, or phase.

**Stage Definition Guidelines:**
- Stages should follow chronological or logical progression
- Each stage should have measurable metrics
- Stages should reveal how the entity evolves over time
- Consider: enrollment → performance → interventions → outcomes

**Output Format (JSON only, no explanations):**
[
  {{
    "stage_id": "enrollment_entry",
    "stage_name": "Enrollment & Initial Profile",
    "stage_order": 1,
    "description": "Students enter the institution - initial demographics, aid allocation, and baseline metrics",
    "metrics_to_track": ["initial_gpa", "aid_amount", "demographic_breakdown", "enrollment_trends"],
    "key_questions": ["Who are these students?", "What support did they receive?", "What were their starting conditions?"]
  }},
  ...
]

**IMPORTANT:**
- Return ONLY valid JSON array, no markdown
- Include 4-6 stages in logical order
- Ensure stages are specific to this entity type
- Focus on actionable insights at each stage"""

    # Dynamically adapt to model capabilities
    model_config = detect_model_tier(ollama_model)

    try:
        print(f"  🔄 Calling LLM to define stages for {entity['entity_name']}...")
        stages_json = call_ollama_api(
            prompt=prompt,
            model=ollama_model,
            ollama_url=ollama_url,
            temperature=model_config["temperature"],  # Adaptive
            num_predict=model_config["stage_token_limits"][1]  # Use middle value
        ).strip()

        print(f"  📝 Stage response length: {len(stages_json)} chars")

        # Clean JSON if wrapped in markdown
        if '```json' in stages_json:
            stages_json = stages_json.split('```json')[1].split('```')[0].strip()
        elif '```' in stages_json:
            stages_json = stages_json.split('```')[1].split('```')[0].strip()

        # Remove any text before the first '[' and after the last ']'
        if '[' in stages_json and ']' in stages_json:
            start_idx = stages_json.find('[')
            end_idx = stages_json.rfind(']') + 1
            stages_json = stages_json[start_idx:end_idx]

        # Use robust JSON parsing
        stages = parse_json_with_fallback(stages_json)

        if stages and isinstance(stages, list):
            print(f"  ✅ Defined {len(stages)} stages for {entity['entity_name']}")
            return stages
        else:
            print(f"  ⚠️ JSON parsing failed for stages, returning empty list")
            return []

    except json.JSONDecodeError as e:
        print(f"  ❌ JSON parsing error for stages: {str(e)}")
        if 'stages_json' in locals():
            print(f"  ❌ Raw response (first 500 chars): {stages_json[:500]}")
        return []
    except Exception as e:
        print(f"  ❌ Error defining stages for {entity['entity_name']}: {str(e)}")
        import traceback
        print(f"  ❌ Traceback: {traceback.format_exc()}")
        return []


# ============================================================================
# PHASE 3: NARRATIVE GENERATION
# ============================================================================

def generate_narrative_for_stage(
    entity: Dict[str, Any],
    stage: Dict[str, Any],
    df: pd.DataFrame,
    ollama_model: str = "qwen2.5:7b",
    ollama_url: str = "http://localhost:11434"
) -> Dict[str, Any]:
    """
    Phase 3: LLM generates narrative story for a specific stage of an entity's journey.

    Args:
        entity: Entity definition
        stage: Stage definition
        df: The student dataset
        ollama_model: The Ollama model to use
        ollama_url: Ollama server URL (local or Cloudflare)

    Returns:
        Narrative with:
        - narrative_text: The story of what happened in this stage
        - key_metrics: Important metrics highlighted
        - insights: Strategic insights discovered
        - recommendations: Actions to take based on this stage
    """

    # Filter and calculate metrics for this entity
    entity_data = filter_dataset_for_entity(df, entity)
    stage_metrics = calculate_stage_metrics(entity_data, stage)

    prompt = f"""You are telling the story of what happened to a specific entity in a specific stage of their journey through a higher education institution.

**Entity:** {entity['entity_name']}
**Stage:** {stage['stage_name']} (Stage {stage['stage_order']})
**Stage Description:** {stage['description']}

**Metrics for This Stage:**
{json.dumps(stage_metrics, indent=2)}

**Your Task:**
Generate a compelling narrative that tells the story of what happened to this entity during this stage. Use the data to support your narrative.

**Narrative Guidelines:**
- Write 3-4 paragraphs (200-300 words total)
- Start with the context and what the data shows
- **INCLUDE nationality breakdown** when analyzing student cohorts (e.g., "The cohort includes 45 Iraqi students, 30 Jordanian students...")
- Highlight key patterns, trends, and anomalies
- Explain WHY these patterns matter
- Connect to institutional goals and student outcomes
- Use specific numbers and metrics from the data
- Write in professional, engaging style

**Output Format (JSON only):**
{{
  "narrative_text": "The Engineering student cohort comprises 120 students across diverse nationalities, with Iraqi students representing the largest group (45 students, 37.5%), followed by Jordanian (30 students, 25%) and Palestinian students (25 students, 21%). Initial assessments reveal an average GPA of 3.2, with notable variations across nationality groups. Financial aid distribution shows 80% of students receiving support, totaling AED 4.8M in institutional investment...",
  "key_metrics": [
    {{"metric": "Total Students", "value": "120", "significance": "Largest academic program"}},
    {{"metric": "Average GPA", "value": "3.2", "significance": "Slightly below institutional average of 3.4"}},
    {{"metric": "Aid Recipients", "value": "96 out of 120 (80%)", "significance": "High aid dependency"}},
    {{"metric": "Nationality Diversity", "value": "15 countries", "significance": "Diverse international composition"}}
  ],
  "insights": [
    "Iraqi students form the largest cohort within Engineering, requiring culturally-aware support services",
    "Performance patterns suggest need for targeted academic interventions across nationality groups",
    "High aid dependency indicates strategic importance for institutional revenue planning"
  ],
  "recommendations": [
    "Establish peer mentoring program pairing students across nationalities",
    "Monitor aid effectiveness by nationality group to identify optimization opportunities",
    "Create culturally-inclusive academic support programs"
  ],
  "visualizations": [
    {{
      "viz_type": "pie_chart",
      "title": "Student Distribution by Nationality",
      "description": "Shows the proportion of students from each country",
      "data_fields": ["Nationality"],
      "chart_purpose": "Visualize diversity and identify dominant nationality groups"
    }},
    {{
      "viz_type": "bar_chart",
      "title": "Average GPA by Nationality",
      "description": "Compares academic performance across nationality groups",
      "data_fields": ["Nationality", "GPA"],
      "chart_purpose": "Identify performance variations requiring targeted interventions"
    }},
    {{
      "viz_type": "stacked_bar",
      "title": "Aid Distribution by Nationality",
      "description": "Shows total aid amount and recipient count per nationality",
      "data_fields": ["Nationality", "Total_Aid"],
      "chart_purpose": "Understand financial aid allocation patterns and dependencies"
    }}
  ]
}}

**IMPORTANT:**
- Return ONLY valid JSON, no markdown
- Use actual metrics from the data provided
- **ALWAYS include nationality breakdown** in the narrative for student cohorts
- Make narrative specific and data-driven
- Focus on actionable insights
- **INCLUDE 2-4 visualizations** that best tell the story of this stage
- Choose visualization types that match the data: pie_chart, bar_chart, line_chart, scatter_plot, stacked_bar, heatmap, histogram"""

    # Dynamically adapt to model capabilities
    model_config = detect_model_tier(ollama_model)

    try:
        print(f"    🔄 Generating narrative for stage: {stage['stage_name']}...")
        narrative_json = call_ollama_api(
            prompt=prompt,
            model=ollama_model,
            ollama_url=ollama_url,
            temperature=model_config["temperature"],  # Adaptive
            num_predict=model_config["narrative_token_limits"][1]  # Use middle value
        ).strip()

        print(f"    📝 Narrative response length: {len(narrative_json)} chars")

        # Use robust JSON parsing — handles fences, preamble, truncation, etc.
        narrative = parse_json_with_fallback(narrative_json)

        if narrative:
            print(f"    ✅ Generated narrative for {entity['entity_name']} - {stage['stage_name']}")
            return narrative
        else:
            # Log the full raw response so we can diagnose the exact failure
            print(f"    ⚠️ JSON parsing failed for stage: {stage['stage_name']}")
            print(f"    ⚠️ Full raw narrative response:\n{narrative_json}")
            return {
                "narrative_text": "Narrative generation encountered formatting issues.",
                "key_metrics": [],
                "insights": [],
                "recommendations": [],
                "visualizations": []
            }

    except json.JSONDecodeError as e:
        print(f"    ❌ JSON parsing error for narrative: {str(e)}")
        if 'narrative_json' in locals():
            print(f"    ❌ Raw response (first 500 chars): {narrative_json[:500]}")
        return {
            "narrative_text": "Narrative generation encountered formatting issues.",
            "key_metrics": [],
            "insights": [],
            "recommendations": [],
            "visualizations": []
        }
    except Exception as e:
        print(f"    ❌ Error generating narrative: {str(e)}")
        import traceback
        print(f"    ❌ Traceback: {traceback.format_exc()}")
        return {
            "narrative_text": "Error generating narrative.",
            "key_metrics": [],
            "insights": [],
            "recommendations": []
        }


# ============================================================================
# COMPLETE JOURNEY GENERATION
# ============================================================================

def generate_complete_llm_journeys(df: pd.DataFrame, ollama_model: str = "qwen2.5:7b", ollama_url: str = "http://localhost:11434") -> List[Dict[str, Any]]:
    """
    Complete journey generation pipeline:
    1. Identify entities
    2. Define stages for each entity
    3. Generate narratives for each stage

    Args:
        df: Student dataset
        ollama_model: Ollama model to use
        ollama_url: Ollama server URL (local or Cloudflare)

    Returns:
        List of complete journeys with all narratives
    """
    import sys

    print("\n" + "="*80, flush=True)
    print("🚀 STARTING LLM-DRIVEN ENTITY JOURNEY GENERATION", flush=True)
    print(f"📊 Dataset: {len(df)} rows, {len(df.columns)} columns", flush=True)
    print(f"🤖 Model: {ollama_model}", flush=True)
    print(f"🌐 URL: {ollama_url}", flush=True)
    print("="*80 + "\n", flush=True)
    sys.stdout.flush()

    all_journeys = []

    # PHASE 1: Identify entities
    print("📊 PHASE 1: Identifying entities from dataset...", flush=True)
    sys.stdout.flush()

    try:
        entities = identify_entities_from_dataset(df, ollama_model, ollama_url)
    except Exception as e:
        print(f"❌ CRITICAL ERROR in identify_entities_from_dataset: {str(e)}", flush=True)
        import traceback
        print(traceback.format_exc(), flush=True)
        sys.stdout.flush()
        return []

    if not entities:
        print("❌ No entities identified. Aborting.", flush=True)
        sys.stdout.flush()
        return []

    print(f"\n✅ Found {len(entities)} entities\n")

    # PHASE 2 & 3: For each entity, define stages and generate narratives
    for idx, entity in enumerate(entities, 1):
        print(f"\n{'='*80}")
        print(f"🎯 Processing Entity {idx}/{len(entities)}: {entity['entity_name']}")
        print(f"{'='*80}\n")

        # Define journey stages for this entity
        print(f"  📋 PHASE 2: Defining journey stages...")
        stages = define_journey_stages_for_entity(entity, df, ollama_model, ollama_url)

        if not stages:
            print(f"  ❌ No stages defined for {entity['entity_name']}, skipping.")
            continue

        # Generate narratives for each stage
        print(f"\n  ✍️  PHASE 3: Generating narratives for {len(stages)} stages...")
        stage_narratives = []

        for stage in stages:
            narrative = generate_narrative_for_stage(entity, stage, df, ollama_model, ollama_url)
            stage_narratives.append({
                **stage,
                **narrative
            })

        # Compile complete journey
        complete_journey = {
            **entity,
            'stages': stage_narratives,
            'total_stages': len(stage_narratives)
        }

        all_journeys.append(complete_journey)

        print(f"\n  ✅ Completed journey for {entity['entity_name']} with {len(stage_narratives)} stages")

    print("\n" + "="*80)
    print(f"✅ JOURNEY GENERATION COMPLETE - {len(all_journeys)} journeys created")
    print("="*80 + "\n")

    return all_journeys


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_dataset_summary(df: pd.DataFrame) -> str:
    """Generate a concise summary of the dataset for LLM analysis."""

    # Build summary with proper conditionals
    nationality_info = f"{df['Nationality'].nunique()} unique" if 'Nationality' in df.columns else 'N/A'
    nationality_top = ', '.join(df['Nationality'].value_counts().head(5).index.tolist()) if 'Nationality' in df.columns else 'N/A'

    major_info = f"{df['Major'].nunique()} unique" if 'Major' in df.columns else 'N/A'
    major_top = ', '.join(df['Major'].value_counts().head(5).index.tolist()) if 'Major' in df.columns else 'N/A'

    gpa_range = f"{df['GPA'].min():.2f} - {df['GPA'].max():.2f}" if 'GPA' in df.columns else 'N/A'

    aid_count = len(df[df['Total_Aid'] > 0]) if 'Total_Aid' in df.columns else 0
    aid_pct = (aid_count / len(df) * 100) if 'Total_Aid' in df.columns and len(df) > 0 else 0
    aid_info = f"{aid_count} students ({aid_pct:.1f}%)" if 'Total_Aid' in df.columns else 'N/A'

    dorm_count = len(df[df['Room_Number'].notna()]) if 'Room_Number' in df.columns else 0
    dorm_info = f"{dorm_count} students" if 'Room_Number' in df.columns else 'N/A'

    summary = f"""
Total Students: {len(df)}
Columns Available: {', '.join(df.columns.tolist())}

Key Distributions:
- Nationalities: {nationality_info} ({nationality_top})
- Programs/Majors: {major_info} ({major_top})
- GPA Range: {gpa_range}
- Aid Recipients: {aid_info}
- Dormitory Residents: {dorm_info}
"""
    return summary.strip()


def generate_entity_data_summary(entity_df: pd.DataFrame, entity: Dict[str, Any]) -> str:
    """Generate summary of data for a specific entity."""

    if len(entity_df) == 0:
        return "No data available for this entity."

    gpa_info = f"Average {entity_df['GPA'].mean():.2f}, Range {entity_df['GPA'].min():.2f}-{entity_df['GPA'].max():.2f}" if 'GPA' in entity_df.columns else 'N/A'

    aid_recipients = len(entity_df[entity_df['Total_Aid'] > 0]) if 'Total_Aid' in entity_df.columns else 0
    aid_total = entity_df['Total_Aid'].sum() if 'Total_Aid' in entity_df.columns else 0
    aid_info = f"{aid_recipients} recipients, Total AED {aid_total:,.0f}" if 'Total_Aid' in entity_df.columns else 'N/A'

    summary = f"""
Student Count: {len(entity_df)}
GPA: {gpa_info}
Aid: {aid_info}
"""
    return summary.strip()


def filter_dataset_for_entity(df: pd.DataFrame, entity: Dict[str, Any]) -> pd.DataFrame:
    """Filter dataset based on entity's data_filter criteria."""

    data_filter = entity.get('data_filter', {})
    filtered_df = df.copy()

    for column, value in data_filter.items():
        if column in filtered_df.columns:
            # Handle special filter notations
            if value == "!= null":
                # Non-null filtering
                filtered_df = filtered_df[filtered_df[column].notna()]
            elif isinstance(value, str) and value.startswith("> "):
                # Greater than filtering (e.g., "> 0")
                try:
                    threshold = float(value.split("> ")[1])
                    # Convert column to numeric, coerce errors to NaN
                    numeric_col = pd.to_numeric(filtered_df[column], errors='coerce')
                    filtered_df = filtered_df[numeric_col > threshold]
                except (ValueError, TypeError) as e:
                    print(f"  ⚠️ Warning: Could not apply numeric filter '> {threshold}' to column '{column}': {e}")
            elif isinstance(value, str) and value.startswith("< "):
                # Less than filtering
                try:
                    threshold = float(value.split("< ")[1])
                    numeric_col = pd.to_numeric(filtered_df[column], errors='coerce')
                    filtered_df = filtered_df[numeric_col < threshold]
                except (ValueError, TypeError) as e:
                    print(f"  ⚠️ Warning: Could not apply numeric filter '< {threshold}' to column '{column}': {e}")
            elif isinstance(value, str) and value.startswith(">= "):
                # Greater than or equal filtering
                try:
                    threshold = float(value.split(">= ")[1])
                    numeric_col = pd.to_numeric(filtered_df[column], errors='coerce')
                    filtered_df = filtered_df[numeric_col >= threshold]
                except (ValueError, TypeError) as e:
                    print(f"  ⚠️ Warning: Could not apply numeric filter '>= {threshold}' to column '{column}': {e}")
            elif isinstance(value, str) and value.startswith("<= "):
                # Less than or equal filtering
                try:
                    threshold = float(value.split("<= ")[1])
                    numeric_col = pd.to_numeric(filtered_df[column], errors='coerce')
                    filtered_df = filtered_df[numeric_col <= threshold]
                except (ValueError, TypeError) as e:
                    print(f"  ⚠️ Warning: Could not apply numeric filter '<= {threshold}' to column '{column}': {e}")
            elif isinstance(value, list):
                # List of values (IN filter)
                filtered_df = filtered_df[filtered_df[column].isin(value)]
            else:
                # Exact match filtering
                filtered_df = filtered_df[filtered_df[column] == value]

    return filtered_df


def calculate_stage_metrics(entity_df: pd.DataFrame, stage: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate metrics relevant to a specific stage."""

    metrics = {
        'student_count': len(entity_df),
        'avg_gpa': float(entity_df['GPA'].mean()) if 'GPA' in entity_df.columns else 0,
        'gpa_range': f"{entity_df['GPA'].min():.2f} - {entity_df['GPA'].max():.2f}" if 'GPA' in entity_df.columns else 'N/A',
        'total_aid': float(entity_df['Total_Aid'].sum()) if 'Total_Aid' in entity_df.columns else 0,
        'aid_recipients': int(len(entity_df[entity_df['Total_Aid'] > 0])) if 'Total_Aid' in entity_df.columns else 0,
    }

    # Add nationality breakdown if available
    if 'Nationality' in entity_df.columns:
        nationality_counts = entity_df['Nationality'].value_counts().head(10).to_dict()
        metrics['nationality_breakdown'] = {
            nat: {'count': int(count), 'percentage': round(count / len(entity_df) * 100, 1)}
            for nat, count in nationality_counts.items()
        }
        metrics['total_nationalities'] = int(entity_df['Nationality'].nunique())

    # Add major/program breakdown if available and not already filtered by it
    if 'Major' in entity_df.columns and entity_df['Major'].nunique() > 1:
        major_counts = entity_df['Major'].value_counts().head(5).to_dict()
        metrics['major_breakdown'] = {
            major: {'count': int(count), 'percentage': round(count / len(entity_df) * 100, 1)}
            for major, count in major_counts.items()
        }

    # Add stage-specific metrics based on metrics_to_track
    # This can be expanded based on the stage requirements

    return metrics


def generate_visualization(entity_df: pd.DataFrame, viz_spec: Dict[str, Any]):
    """
    Generate a Plotly visualization based on LLM-provided specification.

    Args:
        entity_df: The filtered dataset for this entity
        viz_spec: Visualization specification from LLM containing:
            - viz_type: Type of chart (pie_chart, bar_chart, etc.)
            - title: Chart title
            - description: Chart description
            - data_fields: List of fields to visualize
            - chart_purpose: Why this chart matters

    Returns:
        Plotly figure object
    """
    import plotly.express as px
    import plotly.graph_objects as go

    viz_type = viz_spec.get('viz_type', 'bar_chart')
    title = viz_spec.get('title', 'Visualization')
    data_fields = viz_spec.get('data_fields', [])

    try:
        if viz_type == 'pie_chart' and len(data_fields) >= 1:
            # Pie chart for distribution
            field = data_fields[0]
            if field in entity_df.columns:
                counts = entity_df[field].value_counts().head(10)
                fig = px.pie(values=counts.values, names=counts.index, title=title)
                return fig

        elif viz_type == 'bar_chart' and len(data_fields) >= 2:
            # Bar chart for comparisons
            category_field = data_fields[0]
            value_field = data_fields[1]
            if category_field in entity_df.columns and value_field in entity_df.columns:
                grouped = entity_df.groupby(category_field)[value_field].mean().sort_values(ascending=False).head(10)
                fig = px.bar(x=grouped.index, y=grouped.values, title=title,
                           labels={'x': category_field, 'y': f'Average {value_field}'})
                return fig

        elif viz_type == 'stacked_bar' and len(data_fields) >= 2:
            # Stacked bar for multi-dimensional data
            category_field = data_fields[0]
            value_field = data_fields[1]
            if category_field in entity_df.columns and value_field in entity_df.columns:
                grouped = entity_df.groupby(category_field).agg({
                    value_field: ['sum', 'count']
                }).head(10)
                fig = go.Figure()
                fig.add_trace(go.Bar(name='Total', x=grouped.index, y=grouped[(value_field, 'sum')]))
                fig.update_layout(title=title, barmode='stack')
                return fig

        elif viz_type == 'histogram' and len(data_fields) >= 1:
            # Histogram for distribution
            field = data_fields[0]
            if field in entity_df.columns:
                fig = px.histogram(entity_df, x=field, title=title, nbins=20)
                return fig

        elif viz_type == 'scatter_plot' and len(data_fields) >= 2:
            # Scatter plot for correlation
            x_field = data_fields[0]
            y_field = data_fields[1]
            if x_field in entity_df.columns and y_field in entity_df.columns:
                fig = px.scatter(entity_df, x=x_field, y=y_field, title=title)
                return fig

        elif viz_type == 'line_chart' and len(data_fields) >= 2:
            # Line chart for trends
            x_field = data_fields[0]
            y_field = data_fields[1]
            if x_field in entity_df.columns and y_field in entity_df.columns:
                fig = px.line(entity_df, x=x_field, y=y_field, title=title)
                return fig

        # Default: simple bar chart of first field
        if len(data_fields) > 0 and data_fields[0] in entity_df.columns:
            counts = entity_df[data_fields[0]].value_counts().head(10)
            fig = px.bar(x=counts.index, y=counts.values, title=title)
            return fig

    except Exception as e:
        print(f"    ⚠️ Could not generate {viz_type}: {str(e)}")

    return None
