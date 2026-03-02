"""
Financial Intelligence Configuration
====================================
Financial sustainability, aid effectiveness, revenue optimization.
"""

FINANCIAL_INTELLIGENCE_SECTIONS = [
    {
        'name': 'revenue_sustainability',
        'title': '💰 Revenue Sustainability & Risk Analysis',
        'phase': 1,
        'prompt_template': '''
Based on financial data:

{context}

Analyze revenue sustainability and concentration risk:

STEP 1: Review total revenue, sources, and segment distribution
STEP 2: Identify revenue concentration (top segments, geographic, demographic)
STEP 3: Assess concentration risks and dependencies
STEP 4: Recommend diversification strategies

Requirements:
- Quantify total revenue and top revenue sources
- Calculate concentration percentages (e.g., top segment %)
- Identify specific risks (e.g., international dependency, single nationality)
- Suggest actionable diversification tactics

OUTPUT 3-4 sentences with specific numbers:
''',
        'context_focus': ['business_discovery', 'intelligent_metrics', 'domain_discovery', 'statistical_discovery'],
        'num_predict': 350,
        'num_ctx': 2048,
        'timeout': 25,
        'examples': {
            'good': '''Total tuition revenue of $45M shows concerning concentration: 62% from international students ($27.9M), with top 3 countries representing 65% of international enrollment. This creates significant risk from visa policy changes, geopolitical factors, or economic shifts. Revenue diversification strategy: Target domestic enrollment growth (+15%, $2.7M), expand to 5 additional international markets (-15pp concentration), and develop executive education programs (+$3M non-tuition revenue) to reduce dependency.''',
            'bad': '''The institution has revenue from different student segments. International students provide significant revenue. Diversification may be beneficial.'''
        },
        'min_length': 150,
        'require_numbers': True
    },
    {
        'name': 'financial_aid_roi',
        'title': '🎓 Financial Aid Effectiveness & ROI',
        'phase': 2,
        'prompt_template': '''
Based on financial and academic data:

{context}

Analyze financial aid effectiveness and return on investment:

STEP 1: Review financial aid coverage, recipients, and amounts
STEP 2: Correlate aid with retention, performance, and outcomes
STEP 3: Calculate or estimate ROI (retention improvement vs. aid cost)
STEP 4: Recommend optimal aid allocation strategy

Requirements:
- Quantify total aid, coverage %, avg per recipient
- Show correlation with retention/success if data available
- Estimate ROI or build business case
- Recommend specific adjustments to aid strategy

OUTPUT 3-4 sentences:
''',
        'context_focus': ['business_discovery', 'statistical_discovery', 'predictive_discovery', 'domain_discovery'],
        'num_predict': 350,
        'num_ctx': 2048,
        'timeout': 25,
        'examples': {
            'good': '''Financial aid totals $8.1M (18% of tuition revenue) supporting 892 students ($9,080 average). Data shows aid recipients have 12% higher retention rate (93% vs. 81%), suggesting strong ROI: each $1M in aid generates $1.8M in retained revenue (4-year value). Recommendation: Expand strategic aid budget by $500K targeting 55 additional high-potential students, projected ROI of $990K over 4 years while improving access and diversity metrics.''',
            'bad': '''The institution provides financial aid to students. Aid recipients may have better retention. Financial aid is an important tool for enrollment.'''
        },
        'min_length': 150,
        'require_numbers': True
    },
    {
        'name': 'cost_optimization',
        'title': '⚙️ Cost Structure & Optimization',
        'phase': 2,
        'prompt_template': '''
Based on financial data and domain knowledge:

{context}

Analyze cost structure and identify optimization opportunities:

STEP 1: Review cost analysis from context (aid, operations, etc.)
STEP 2: Identify high-cost areas and efficiency opportunities
STEP 3: Benchmark against industry standards from domain knowledge
STEP 4: Recommend specific cost optimization tactics

Requirements:
- Quantify major cost categories
- Compare to industry benchmarks
- Identify inefficiencies or opportunities
- Suggest specific, actionable improvements

OUTPUT 3 sentences:
''',
        'context_focus': ['business_discovery', 'domain_discovery', 'intelligent_metrics'],
        'num_predict': 300,
        'num_ctx': 2048,
        'timeout': 20,
        'examples': {
            'good': '''Financial aid at 18% of tuition revenue aligns with industry benchmark (18-22%), suggesting appropriate investment in access. However, aid-per-recipient ($9,080) exceeds sector average by 12%, indicating opportunity for broader distribution at lower per-capita amounts to increase reach. Recommendation: Restructure aid packages to support 20% more students (+178 students) at slightly reduced average ($8,000), expanding access while maintaining $8.1M budget and improving enrollment diversity.''',
            'bad': '''Financial aid spending should be reviewed. The institution should look for ways to optimize costs while maintaining quality.'''
        },
        'min_length': 120,
        'require_numbers': True
    }
]
