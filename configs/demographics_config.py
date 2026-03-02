"""
Demographics Configuration
==========================
Diversity, market concentration, inclusion strategies.
"""

DEMOGRAPHICS_SECTIONS = [
    {
        'name': 'diversity_analysis',
        'title': '🌍 Diversity & Representation Analysis',
        'phase': 1,
        'prompt_template': '''
Based on demographic data:

{context}

Analyze diversity and representation:

STEP 1: Review demographic distribution (nationality, geography, or other categories)
STEP 2: Calculate diversity metrics (unique segments, distribution balance)
STEP 3: Compare to goals or benchmarks if available
STEP 4: Assess diversity as strength or opportunity

Requirements:
- Quantify representation (segment counts, percentages)
- Calculate diversity index or balance measures
- Identify dominant segments and underrepresented groups
- Connect to institutional goals (inclusion, global reach, market access)

OUTPUT 3-4 sentences with specific numbers:
''',
        'context_focus': ['intelligent_metrics', 'statistical_discovery', 'domain_discovery'],
        'num_predict': 300,
        'num_ctx': 2048,
        'timeout': 20,
        'examples': {
            'good': '''The institution serves students from 45 nationalities, demonstrating strong international diversity. However, 65% of international students come from just 3 countries (India 28%, Pakistan 22%, Egypt 15%), indicating concentration risk and limited geographic diversity. UAE nationals represent 15% of enrollment, below the 25% national diversity target. Opportunity: Expand recruitment to underrepresented regions (Africa +5%, Southeast Asia +5%, Latin America +3%) to improve resilience and global reach.''',
            'bad': '''The institution has students from many different countries. There is good diversity overall with room for improvement in certain areas.'''
        },
        'min_length': 150,
        'require_numbers': True
    },
    {
        'name': 'market_concentration_risk',
        'title': '⚠️ Market Concentration & Dependency Risk',
        'phase': 2,
        'prompt_template': '''
Based on demographic and business data:

{context}

Analyze market concentration risks:

STEP 1: Identify top markets/segments and their contribution (enrollment, revenue)
STEP 2: Assess concentration risk (single market dependency)
STEP 3: Evaluate vulnerability to market-specific disruptions
STEP 4: Recommend risk mitigation strategies

Requirements:
- Quantify top market concentration (%, revenue, enrollment)
- Specify risk factors (visa policy, economic, political, competitive)
- Assess risk severity (high/moderate/low)
- Recommend diversification targets

OUTPUT 3-4 sentences:
''',
        'context_focus': ['business_discovery', 'intelligent_metrics', 'predictive_discovery', 'domain_discovery'],
        'num_predict': 350,
        'num_ctx': 2048,
        'timeout': 25,
        'examples': {
            'good': '''Top 3 international markets account for 65% of international enrollment and $18.1M revenue (40% of total), creating high concentration risk. Visa policy changes, currency fluctuations, or increased competition in any single market could impact 400+ students and $6M+ in annual revenue. Risk mitigation: Launch recruitment initiatives in 5 new markets (Southeast Asia, Latin America, Africa) targeting 15pp reduction in top-3 concentration over 3 years, while maintaining international enrollment at 45% of total.''',
            'bad': '''Some markets contribute more students than others. This creates some level of risk that should be monitored and potentially addressed through diversification.'''
        },
        'min_length': 150,
        'require_numbers': True
    },
    {
        'name': 'inclusion_strategy',
        'title': '🤝 Inclusion & Belonging Strategy',
        'phase': 2,
        'prompt_template': '''
Based on demographics, relationships, and domain knowledge:

{context}

Recommend inclusion and belonging strategies:

STEP 1: Identify underrepresented or minority populations
STEP 2: Review research on belonging impact (retention, success, satisfaction)
STEP 3: Recommend specific programs or initiatives
STEP 4: Estimate impact on retention and community

Requirements:
- Identify target populations (segments, sizes)
- Cite research or best practices from domain knowledge
- Recommend 2-3 specific, actionable initiatives
- Connect to outcomes (retention, satisfaction, brand)

OUTPUT 2-3 recommendations:
''',
        'context_focus': ['intelligent_metrics', 'domain_discovery', 'relationship_discovery', 'predictive_discovery'],
        'num_predict': 350,
        'num_ctx': 2048,
        'timeout': 25,
        'examples': {
            'good': '''1. Launch affinity groups for underrepresented nationalities (<5% enrollment, 8 countries, 180 students total) to combat isolation and build community. Research shows belonging initiatives improve retention by 8-12% for minority populations. Projected impact: 14-22 additional students retained annually ($322K-$506K 4-year value).

2. Create mentorship program pairing international students (1,148) with domestic mentors and local community members. Best practices show cross-cultural mentorship improves satisfaction (NPS +15 points) and reduces culture shock-related withdrawals. Expected: 5% reduction in international student attrition (57 students, $1.3M protected).''',
            'bad': '''1. Create support groups for minority students to help them feel more included
2. Develop mentorship programs to improve the experience of international students'''
        },
        'min_length': 200,
        'require_numbers': True
    }
]
