"""
Executive Summary Tab Configuration
===================================
Defines all sections for the Executive Summary tab.
"""

EXECUTIVE_SUMMARY_SECTIONS = [
    {
        'name': 'executive_summary',
        'title': '📊 Executive Summary',
        'phase': 1,  # Foundation section
        'prompt_template': '''
Based on this data analysis:

{context}

Create a compelling executive summary following these steps:

STEP 1: Review the data and identify the top 3 most significant findings
STEP 2: Assess the business impact of each finding
STEP 3: Select the single most critical finding that leadership needs to know
STEP 4: Draft a concise 2-3 sentence summary

Requirements:
- Quantify the impact using specific numbers, percentages, or dollar amounts
- Explain why this matters to leadership (revenue, risk, opportunity, compliance)
- Be specific and actionable - avoid vague statements
- Focus on business outcomes, not just data observations

OUTPUT ONLY the executive summary (no headers, no labels, just the content):
''',
        'num_predict': 200,
        'num_ctx': 1536,
        'timeout': 20,
        'context_focus': ['intelligent_metrics', 'statistical_discovery'],
        'examples': {
            'good': 'Analysis of 2,550 students reveals 17% (450 students) are high-performers (GPA ≥ 3.5) generating $12.5M in tuition revenue, while 5% (120 students) are at-risk of dropping out, representing a $2.8M retention opportunity.',
            'bad': 'The data shows interesting patterns in student performance. There are some high performers and some students who might need help.'
        },
        'min_length': 100,
        'require_numbers': True
    },
    {
        'name': 'big_picture',
        'title': '🎯 The Big Picture',
        'phase': 1,  # Foundation section
        'prompt_template': '''
Based on this data analysis:

{context}

Create "The Big Picture" section following these steps:

STEP 1: Identify the business domain and context (education, healthcare, retail, etc.)
STEP 2: Determine what story the data tells about this domain
STEP 3: Identify why stakeholders should care about this story
STEP 4: Write a compelling 3-4 sentence narrative

Requirements:
- Start with the business domain context (e.g., "This educational institution manages...")
- Explain the overarching business situation or challenge
- Connect data patterns to real business outcomes
- Make stakeholders understand why this matters strategically

OUTPUT ONLY the big picture narrative (no headers, no labels, just the content):
''',
        'num_predict': 250,
        'num_ctx': 1536,
        'timeout': 20,
        'context_focus': ['intelligent_metrics', 'data_discovery'],
        'examples': {
            'good': 'This educational institution manages 2,550 students across multiple programs, generating $45M in annual tuition revenue. The data reveals a critical balance between maintaining academic excellence (17% high-performers) and addressing retention risk (5% at-risk students). With each at-risk student representing $23,000 in potential revenue loss, proactive intervention could secure $2.8M in revenue while improving student outcomes.',
            'bad': 'This is a dataset about students. There are various metrics like GPA and enrollment. The institution has different types of students from different backgrounds.'
        },
        'min_length': 150,
        'require_numbers': True
    },
    {
        'name': 'key_discoveries',
        'title': '🔍 Key Discoveries',
        'phase': 2,  # Uses Phase 1 as context
        'prompt_template': '''
Based on this data analysis:

{context}

Create a "Key Discoveries" section with the top 3-4 discoveries following these steps:

STEP 1: Analyze all available metrics, correlations, and patterns
STEP 2: Identify discoveries that are:
   - Actionable (can drive decisions)
   - Significant (impact on business outcomes)
   - Surprising or non-obvious
STEP 3: For each discovery, determine:
   - What was found (the data pattern)
   - Why it matters (business impact)
   - What it suggests (implication)
STEP 4: Write 3-4 bullet points, each 2-3 sentences

Requirements:
- Each discovery must include specific numbers or percentages
- Explain the business implication, not just the data observation
- Prioritize by business impact (revenue, risk, efficiency, quality)
- Avoid stating obvious facts - find meaningful insights

OUTPUT as a bulleted list (use - for bullets):
''',
        'num_predict': 400,
        'num_ctx': 2048,
        'timeout': 25,
        'context_focus': ['intelligent_metrics', 'statistical_discovery', 'data_discovery'],
        'examples': {
            'good': '''- Financial aid recipients (35% of students) have 12% higher retention rates than non-recipients, suggesting strategic investment in aid could reduce the $2.8M at-risk revenue and improve graduation outcomes.
- International students represent 45% of enrollment but contribute 62% of total tuition revenue ($27.9M), indicating high dependency on this segment for financial sustainability.
- Students with GPA decline >0.3 in first semester are 4x more likely to become at-risk, presenting an early warning opportunity for intervention programs.''',
            'bad': '''- There are high performers and at-risk students
- Students come from different countries
- GPA varies across the student population'''
        },
        'min_length': 300,
        'require_numbers': True
    },
    {
        'name': 'strategic_recommendations',
        'title': '💡 Strategic Recommendations',
        'phase': 2,  # Uses Phase 1 as context
        'prompt_template': '''
Based on this data analysis:

{context}

Create "Strategic Recommendations" with 3-4 actionable recommendations following these steps:

STEP 1: Review the key findings and business challenges
STEP 2: For each major finding, identify:
   - What action should be taken
   - Why it will improve outcomes
   - What the expected impact is
STEP 3: Prioritize recommendations by:
   - Feasibility (can be implemented)
   - Impact (business value)
   - Urgency (time sensitivity)
STEP 4: Write 3-4 recommendations, each 2-3 sentences

Requirements:
- Start each with a clear action verb (Implement, Expand, Optimize, Target, etc.)
- Quantify expected impact whenever possible
- Make recommendations specific and actionable
- Connect to business outcomes (revenue, cost savings, risk reduction, efficiency gains)

OUTPUT as a numbered list:
''',
        'num_predict': 400,
        'num_ctx': 2048,
        'timeout': 25,
        'context_focus': ['intelligent_metrics', 'statistical_discovery'],
        'examples': {
            'good': '''1. Implement an early warning system targeting students with first-semester GPA decline >0.3, which affects 8% of enrollment (204 students). Proactive academic support could improve retention by 15%, securing $700K in revenue and better student outcomes.
2. Expand financial aid budget by $500K to cover 50 additional students, which data shows yields 12% higher retention rates. Expected ROI: $1.15M in retained tuition revenue over 4 years.
3. Diversify international student recruitment beyond current 3 primary countries (65% of international students) to reduce dependency risk and stabilize the $27.9M international revenue stream.''',
            'bad': '''1. Help at-risk students with their studies
2. Consider increasing financial aid if possible
3. Monitor international student enrollment'''
        },
        'min_length': 300,
        'require_numbers': True
    },
    {
        'name': 'risk_areas',
        'title': '⚠️ Risk Areas & Watchpoints',
        'phase': 2,  # Uses Phase 1 as context
        'prompt_template': '''
Based on this data analysis:

{context}

Create "Risk Areas & Watchpoints" section with 2-3 key risks following these steps:

STEP 1: Analyze data for:
   - Revenue concentration or dependency
   - Quality issues or deteriorating metrics
   - Compliance or operational risks
   - Emerging negative trends
STEP 2: For each risk, identify:
   - What the risk is
   - Why it's concerning (potential impact)
   - What should be monitored
STEP 3: Prioritize by severity and likelihood
STEP 4: Write 2-3 risk items, each 2 sentences

Requirements:
- Quantify the risk exposure (dollar amount, percentage, volume)
- Be specific about what could go wrong
- Suggest monitoring metrics or triggers
- Focus on business risks, not just data quality issues

OUTPUT as a bulleted list (use - for bullets):
''',
        'num_predict': 300,
        'num_ctx': 2048,
        'timeout': 20,
        'context_focus': ['intelligent_metrics', 'statistical_discovery', 'data_discovery'],
        'examples': {
            'good': '''- 62% revenue concentration in international students ($27.9M) creates significant risk if visa policies or geopolitical factors disrupt enrollment. Monitor international application rates and deposit confirmations monthly.
- At-risk student population (5%, 120 students) represents $2.8M in immediate revenue risk, with potential 3-year cascade effect of $8.4M if cohort-based programs are disrupted. Track early alert triggers weekly.
- Financial aid coverage declining from 18% to 16% year-over-year may impact access and diversity goals, while competitor institutions maintain 22% coverage. Review aid strategy quarterly.''',
            'bad': '''- Some students are at risk of failing
- International enrollment could change
- Financial aid budget might not be enough'''
        },
        'min_length': 200,
        'require_numbers': True
    }
]
