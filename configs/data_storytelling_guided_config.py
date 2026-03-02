"""
Data Storytelling AI Driven with Template Guidance Configuration
================================================================
Entity discovery and journey story generation.
"""

DATA_STORYTELLING_GUIDED_SECTIONS = [
    {
        'name': 'entity_discovery',
        'title': '🔍 Entity Discovery & Lifecycle Identification',
        'phase': 1,
        'prompt_template': '''
Based on this data:

{context}

Identify the primary business entity and its lifecycle following these steps:

STEP 1: Review detected entities and domain from context
STEP 2: Determine the entity's lifecycle stages (e.g., Enrollment→Active→Graduate for students)
STEP 3: Identify key transitions and milestones between stages
STEP 4: List measurable metrics at each stage

Requirements:
- Name the primary entity type
- List 4-6 lifecycle stages in chronological order
- Quantify population/count at each stage if data available
- Identify critical transitions (e.g., enrollment to retention)

OUTPUT as structured bullet list:
''',
        'context_focus': ['intelligent_metrics', 'relationship_discovery', 'domain_discovery'],
        'num_predict': 400,
        'num_ctx': 2048,
        'timeout': 25,
        'examples': {
            'good': '''**Primary Entity**: Student
**Lifecycle Stages**:
- Prospective (Inquiry/Application)
- Enrolled (First-Year Students: 650)
- Active (Continuing Students: 1,900)
- At-Risk (Retention Concern: 120, 5%)
- Graduating (Senior Class: 450)
- Alumni (Graduated)

**Critical Transitions**:
- Enrollment → Retention (First-year success rate: 95%)
- Active → At-Risk (Warning: GPA <2.0, financial stress)
- Active → Graduating (4-year completion: 65%)''',
            'bad': 'The data contains students at different stages of education.'
        },
        'min_length': 200,
        'require_numbers': True
    },
    {
        'name': 'journey_narrative',
        'title': '📖 Journey Narrative & Story Arc',
        'phase': 2,
        'prompt_template': '''
Based on entity discovery and comprehensive data analysis:

{context}

Create a compelling journey narrative following these steps:

STEP 1: Describe the typical entity journey from beginning to end
STEP 2: Highlight success patterns and common challenges at each stage
STEP 3: Identify drop-off points, bottlenecks, and optimization opportunities
STEP 4: Connect journey insights to business outcomes (revenue, satisfaction, brand)

Requirements:
- Tell a cohesive story with beginning, middle, end
- Include specific numbers, percentages, counts at each stage
- Identify 2-3 key risks or opportunities
- Be actionable and insight-driven

OUTPUT 4-6 paragraphs forming a complete story:
''',
        'context_focus': ['intelligent_metrics', 'business_discovery', 'predictive_discovery', 'statistical_discovery'],
        'num_predict': 600,
        'num_ctx': 2048,
        'timeout': 30,
        'examples': {
            'good': '''The student journey begins with 800 prospective students converting to 650 enrolled first-years (81% yield rate). These students bring $18.5M in tuition revenue and represent the future of the institution.

During the critical first year, 95% successfully transition to continuing status (1,900 active students), but 5% (120 students) become at-risk due to academic challenges or financial stress. This at-risk population represents $2.8M in immediate revenue risk and potential 4-year cascade impact of $8.4M.

The active student population maintains strong performance with average GPA of 3.12, significantly above the 3.0 industry benchmark. High performers (17%, 450 students) generate $12.5M in revenue and serve as brand ambassadors, while the broad middle (78%, 1,980 students) forms the stable revenue base at $55M annually.

As students approach graduation, 65% complete their 4-year programs on time (450 graduates), meeting industry benchmarks. However, the 35% extended timeline represents opportunity for improvement through better academic advising and support services.

**Key Opportunities**: (1) Reduce at-risk population from 5% to 3% through early warning systems ($1.4M revenue protection), (2) Improve 4-year completion from 65% to 70% (industry top quartile), (3) Expand high-performer recruitment to 20% (enhance brand reputation and rankings).''',
            'bad': '''Students go through different stages. Some succeed and others struggle. The institution has various programs to support students throughout their journey.'''
        },
        'min_length': 400,
        'require_numbers': True
    },
    {
        'name': 'journey_recommendations',
        'title': '💡 Journey Optimization Recommendations',
        'phase': 2,
        'prompt_template': '''
Based on journey analysis and insights:

{context}

Recommend specific journey optimizations following these steps:

STEP 1: Identify the highest-impact intervention points in the journey
STEP 2: For each intervention, specify:
   - Target stage and population
   - Specific action to take
   - Expected impact (retention %, revenue, satisfaction)
STEP 3: Prioritize by ROI and feasibility

Requirements:
- Start each with action verb (Implement, Launch, Optimize, Enhance)
- Specify target (stage, population size, criteria)
- Quantify expected impact
- Focus on highest-ROI opportunities

OUTPUT 3-4 numbered recommendations:
''',
        'context_focus': ['predictive_discovery', 'business_discovery', 'domain_discovery'],
        'num_predict': 450,
        'num_ctx': 2048,
        'timeout': 25,
        'examples': {
            'good': '''1. Implement first-year early warning system targeting students with GPA decline >0.3 in first semester (projected: 8% of enrollment, 204 students). Proactive intervention can improve retention by 15%, protecting $700K in annual revenue and improving 4-year graduation rates by 5%.

2. Launch peer mentoring program pairing at-risk students (120) with high performers (450). Research shows peer support improves retention by 12-18%. Expected: reduce at-risk population to 3% (60 students), retaining $1.4M in revenue annually.

3. Optimize graduation pathway advising for extended-timeline students (35% of cohort, 350 students). Better course sequencing and degree planning can improve 4-year completion from 65% to 70%, meeting top-quartile benchmarks and reducing institutional cost-per-graduate.

4. Enhance high-performer recruitment and retention programs, targeting growth from 17% to 20% (75 additional students). Benefits: $2.1M additional revenue, improved rankings, stronger brand reputation, enhanced peer effects for all students.''',
            'bad': '''1. Provide better support for struggling students
2. Improve graduation rates through advising
3. Recruit more high-performing students
4. Monitor student progress more closely'''
        },
        'min_length': 350,
        'require_numbers': True
    }
]
