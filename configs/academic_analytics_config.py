"""
Academic Analytics Tab Configuration
====================================
Defines sections for academic performance analysis.
"""

ACADEMIC_ANALYTICS_SECTIONS = [
    {
        'name': 'gpa_distribution_analysis',
        'title': '📊 GPA Distribution Analysis',
        'phase': 1,
        'prompt_template': '''
Based on this academic data:

{context}

Analyze the GPA distribution following these steps:

STEP 1: Review GPA statistics (mean, median, std deviation, distribution type)
STEP 2: Compare to industry benchmarks (avg GPA, high performer %, at-risk %)
STEP 3: Identify patterns (normal distribution, skewness, outliers)
STEP 4: Assess academic quality and risk indicators

Requirements:
- Include specific numbers (mean GPA, percentages, counts)
- Compare to benchmarks from context
- Identify concerning patterns or positive trends
- Be specific about what the distribution reveals

OUTPUT a 3-4 sentence analysis:
''',
        'context_focus': ['intelligent_metrics', 'statistical_discovery', 'domain_discovery'],
        'num_predict': 300,
        'num_ctx': 2048,
        'timeout': 20,
        'examples': {
            'good': 'The GPA distribution shows a mean of 3.12 with slight left-skew (-0.3), indicating strong overall performance. With 17% high-performers (GPA≥3.5) compared to the 15% industry average, academic quality exceeds benchmarks. Only 5% are at-risk (GPA<2.0), better than the 8% industry average, suggesting effective academic support systems.',
            'bad': 'GPA varies across students. Some have high GPAs and others have low GPAs. There is a distribution of grades in the dataset.'
        },
        'min_length': 150,
        'require_numbers': True
    },
    {
        'name': 'performance_segments',
        'title': '🎯 Performance Segment Analysis',
        'phase': 1,
        'prompt_template': '''
Based on this academic data:

{context}

Analyze student performance segments following these steps:

STEP 1: Identify the main performance segments (high performers, average, at-risk)
STEP 2: Calculate size and percentage of each segment
STEP 3: Assess revenue/enrollment implications of each segment
STEP 4: Identify actionable insights for each segment

Requirements:
- Quantify each segment (count, percentage, revenue impact)
- Explain why each segment matters strategically
- Be specific about risks and opportunities
- Connect to business outcomes

OUTPUT 3-4 bullet points, one per segment:
''',
        'context_focus': ['intelligent_metrics', 'business_discovery', 'statistical_discovery'],
        'num_predict': 400,
        'num_ctx': 2048,
        'timeout': 25,
        'examples': {
            'good': '''- High Performers (450 students, 17%): Generate $12.5M in tuition revenue and serve as brand ambassadors. Retention focus: honors programs, research opportunities, competitive scholarships.
- Average Students (1,980 students, 78%): Core revenue base at $55M annually. Risk: vulnerable to competition. Strategy: enhance student experience, career services, engagement programs.
- At-Risk Students (120 students, 5%): Represent $2.8M revenue at risk and 4-year cascade risk of $8.4M. Immediate action: early warning system, tutoring, financial aid review, academic coaching.''',
            'bad': '''- Some students perform well
- Most students are average
- Some students need help'''
        },
        'min_length': 300,
        'require_numbers': True
    },
    {
        'name': 'intervention_recommendations',
        'title': '💡 Targeted Intervention Strategies',
        'phase': 2,
        'prompt_template': '''
Based on this academic data and performance analysis:

{context}

Recommend targeted academic interventions following these steps:

STEP 1: Identify the most critical academic challenges from the data
STEP 2: For each challenge, determine:
   - Who needs intervention (which segment, how many students)
   - What intervention would be most effective
   - Expected impact (retention improvement, GPA improvement)
STEP 3: Prioritize by impact and feasibility
STEP 4: Quantify expected outcomes

Requirements:
- Start each with action verb (Implement, Launch, Expand, Create)
- Specify target population (segment, count, criteria)
- Quantify expected impact (% improvement, $ value, students affected)
- Be actionable and specific

OUTPUT 3-4 numbered recommendations:
''',
        'context_focus': ['intelligent_metrics', 'business_discovery', 'predictive_discovery', 'domain_discovery'],
        'num_predict': 450,
        'num_ctx': 2048,
        'timeout': 25,
        'examples': {
            'good': '''1. Implement early warning system targeting students with first-semester GPA decline >0.3 (est. 204 students, 8%). Proactive academic coaching + tutoring can improve retention by 15%, securing $700K in revenue and improving 4-year graduation rates by 5%.
2. Launch peer tutoring program for average performers (GPA 2.5-3.5, 1,500 students). Data shows peer effects improve GPA by 0.2-0.3 points. Expected: 200 students move to high-performer category, enhancing reputation and rankings.
3. Create intensive support cohort for at-risk students (120 students, $2.8M revenue risk). Combine academic coaching, financial aid review, and course load adjustment. Target: reduce at-risk population by 30% (36 students, $840K retained revenue).''',
            'bad': '''1. Help students who are struggling with their grades
2. Provide more tutoring services to students
3. Monitor student performance more closely'''
        },
        'min_length': 350,
        'require_numbers': True
    },
    {
        'name': 'success_predictors',
        'title': '🔮 Success Predictors & Early Indicators',
        'phase': 2,
        'prompt_template': '''
Based on this academic data and predictive insights:

{context}

Identify success predictors and early warning indicators following these steps:

STEP 1: Review lead indicators from context (what predicts success/failure)
STEP 2: Identify measurable early warning signals in your data
STEP 3: Recommend monitoring metrics and trigger thresholds
STEP 4: Suggest proactive interventions tied to each indicator

Requirements:
- List 3-4 specific, measurable early indicators
- Include threshold values that trigger action
- Explain why each indicator matters (predictive power)
- Suggest specific intervention for each

OUTPUT as bulleted list:
''',
        'context_focus': ['predictive_discovery', 'intelligent_metrics', 'statistical_discovery', 'domain_discovery'],
        'num_predict': 400,
        'num_ctx': 2048,
        'timeout': 25,
        'examples': {
            'good': '''- First-Semester GPA: Strongest predictor of 4-year graduation. Monitor threshold: <2.5. Students below 2.5 have 65% dropout risk. Intervention: Immediate academic coaching + course load review.
- GPA Decline >0.3 points: Indicates student struggling with transition. Occurs in 8% of students, 4x dropout risk. Intervention: Trigger alert to advisor within 48 hours, mandatory check-in.
- Course Withdrawal Pattern: 2+ withdrawals in first year signals disengagement. Affects 6% of students, 50% retention risk. Intervention: Meet with dean, explore major fit, review support services.
- Financial Aid Decline: Reduction in aid correlates with stress and withdrawal. Monitor changes >$2K. Intervention: Financial counseling, emergency grant review, payment plan options.''',
            'bad': '''- Monitor GPA for early warning
- Watch for students who withdraw from courses
- Keep track of financial aid changes
- Pay attention to student engagement'''
        },
        'min_length': 300,
        'require_numbers': True
    }
]
