"""
Housing Insights Configuration
==============================
Housing patterns, occupancy, and impact on student success.
"""

HOUSING_INSIGHTS_SECTIONS = [
    {
        'name': 'occupancy_analysis',
        'title': '🏠 Occupancy & Utilization Analysis',
        'phase': 1,
        'prompt_template': '''
Based on housing data:

{context}

Analyze housing occupancy and utilization:

STEP 1: Identify housing types and distribution (on-campus, off-campus, commuter)
STEP 2: Calculate occupancy rates and utilization percentages
STEP 3: Identify underutilized or overutilized housing segments
STEP 4: Assess financial and operational implications

Requirements:
- Quantify each housing type (count, percentage)
- Calculate utilization rates if capacity data available
- Identify optimization opportunities
- Estimate revenue or cost impact

OUTPUT 3-4 sentences with specific numbers:
''',
        'context_focus': ['intelligent_metrics', 'statistical_discovery', 'business_discovery'],
        'num_predict': 300,
        'num_ctx': 2048,
        'timeout': 20,
        'examples': {
            'good': '''Housing distribution shows 40% on-campus (1,020 students), 35% off-campus (893 students), and 25% commuter (637 students). On-campus housing operates at 85% capacity, indicating room for 180 additional students ($1.8M potential revenue at $10K per student). Off-campus students represent a missed revenue opportunity but may indicate housing capacity constraints or preference for independence.''',
            'bad': '''Students live in different types of housing. Some live on campus and others off campus. There are also commuter students.'''
        },
        'min_length': 150,
        'require_numbers': True
    },
    {
        'name': 'housing_performance_correlation',
        'title': '📊 Housing-Performance Correlation',
        'phase': 2,
        'prompt_template': '''
Based on housing and academic data:

{context}

Analyze correlation between housing type and student success:

STEP 1: Review correlations between housing and GPA/retention from context
STEP 2: Compare outcomes by housing type (performance metrics)
STEP 3: Assess correlation vs. causation factors
STEP 4: Make data-driven housing strategy recommendations

Requirements:
- Cite correlation values if available
- Compare GPA/retention by housing type
- Explain potential causal factors (proximity, community, support)
- Recommend housing policies based on findings

OUTPUT 3-4 sentences:
''',
        'context_focus': ['statistical_discovery', 'intelligent_metrics', 'relationship_discovery', 'predictive_discovery'],
        'num_predict': 350,
        'num_ctx': 2048,
        'timeout': 25,
        'examples': {
            'good': '''On-campus students show 8% higher retention rate (94% vs. 86%) and 0.25 higher average GPA (3.21 vs. 2.96) compared to off-campus/commuter students. This correlation likely reflects community engagement, proximity to academic resources, and structured support systems. Housing policy recommendation: Increase on-campus capacity by 180 beds (85%→95% utilization) to capture $1.8M revenue while improving retention by projected 20 students annually ($460K additional 4-year value).''',
            'bad': '''Students who live on campus tend to perform better than those who live off campus. Housing location may affect academic success.'''
        },
        'min_length': 150,
        'require_numbers': True
    }
]
