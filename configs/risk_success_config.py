"""
Risk & Success Analysis Configuration
=====================================
At-risk patterns, success predictors, intervention effectiveness.
"""

RISK_SUCCESS_SECTIONS = [
    {
        'name': 'risk_identification',
        'title': '⚠️ At-Risk Student Identification',
        'phase': 1,
        'prompt_template': '''
Based on academic and risk data:

{context}

Identify at-risk student population and patterns:

STEP 1: Quantify at-risk population (count, percentage, criteria)
STEP 2: Compare to industry benchmarks
STEP 3: Identify risk factors and patterns from data
STEP 4: Assess revenue and reputational implications

Requirements:
- Specify at-risk definition and criteria
- Quantify population (count, %, revenue at risk)
- Compare to 8% industry average
- Calculate potential revenue impact (annual + 4-year cascade)

OUTPUT 3-4 sentences with specific numbers:
''',
        'context_focus': ['intelligent_metrics', 'business_discovery', 'domain_discovery', 'predictive_discovery'],
        'num_predict': 300,
        'num_ctx': 2048,
        'timeout': 20,
        'examples': {
            'good': '''At-risk population (GPA <2.0) comprises 120 students (5% of enrollment), better than the 8% industry average. However, this represents $2.8M in immediate revenue risk and potential 4-year cascade impact of $8.4M if cohort-based programs are disrupted. Early warning indicators show an additional 204 students (8%) with first-semester GPA decline >0.3, flagging them as emerging risk (4x higher dropout probability). Combined risk exposure: 324 students, $7.5M annual revenue, $22M four-year value.''',
            'bad': '''Some students are at risk of academic failure. This group should be monitored and supported. The institution has programs to help struggling students.'''
        },
        'min_length': 150,
        'require_numbers': True
    },
    {
        'name': 'success_predictors',
        'title': '🎯 Success Predictors & Early Indicators',
        'phase': 1,
        'prompt_template': '''
Based on predictive insights and statistical patterns:

{context}

Identify success predictors and early warning indicators:

STEP 1: Review lead indicators from context (strongest predictors)
STEP 2: Identify measurable early signals in your data
STEP 3: Specify threshold values that trigger action
STEP 4: Rank by predictive power and actionability

Requirements:
- List 3-4 specific, measurable early indicators
- Include threshold values (e.g., GPA <2.5, decline >0.3)
- Explain predictive power (correlation, risk multiplier)
- Suggest monitoring frequency and triggers

OUTPUT as bulleted list with thresholds:
''',
        'context_focus': ['predictive_discovery', 'intelligent_metrics', 'statistical_discovery', 'domain_discovery'],
        'num_predict': 400,
        'num_ctx': 2048,
        'timeout': 25,
        'examples': {
            'good': '''- **First-Semester GPA**: Strongest predictor of 4-year graduation. Threshold: <2.5 triggers advisor alert. Students below 2.5 have 65% dropout risk vs. 5% baseline. Monitor: Weekly in first semester.

- **GPA Decline >0.3 Points**: Indicates struggling with transition/course difficulty. Threshold: 0.3-point decline semester-over-semester. Affects 8% of students, creates 4x dropout risk. Monitor: End of each grading period, automatic flag.

- **Course Withdrawal Pattern**: Multiple withdrawals signal disengagement. Threshold: 2+ withdrawals in first year. Affects 6% of students, 50% retention risk. Monitor: Real-time during add/drop and withdrawal periods.

- **Financial Aid Changes**: Aid reduction >$2K correlates with stress and withdrawal. Threshold: $2,000+ reduction year-over-year. Monitor: At financial aid award notification, during appeals process.''',
            'bad': '''- Monitor student GPA for early warning signs
- Watch for students withdrawing from courses
- Track financial aid changes that might affect students
- Pay attention to overall student engagement'''
        },
        'min_length': 300,
        'require_numbers': True
    },
    {
        'name': 'intervention_strategy',
        'title': '🚀 Intervention & Support Strategy',
        'phase': 2,
        'prompt_template': '''
Based on risk analysis and best practices:

{context}

Design targeted intervention strategy:

STEP 1: Match interventions to risk factors and populations
STEP 2: Prioritize by impact and feasibility
STEP 3: Specify intervention details (who, what, when, expected impact)
STEP 4: Recommend implementation timeline

Requirements:
- Start each with action verb (Implement, Launch, Deploy)
- Specify target population (segment, count, criteria)
- Describe specific intervention (program, support, system)
- Quantify expected impact (retention %, students saved, revenue protected)

OUTPUT 3-4 numbered interventions:
''',
        'context_focus': ['predictive_discovery', 'business_discovery', 'domain_discovery', 'intelligent_metrics'],
        'num_predict': 450,
        'num_ctx': 2048,
        'timeout': 25,
        'examples': {
            'good': '''1. **Implement Early Warning System** targeting students with first-semester GPA decline >0.3 (204 students, 8% of enrollment). Automated alerts trigger within 48 hours, mandatory advisor check-in within 1 week. Expected impact: 15% retention improvement (31 students saved annually, $714K protected over 4 years).

2. **Launch Intensive Support Cohort** for at-risk students (GPA <2.0, 120 students, $2.8M revenue risk). Combine weekly academic coaching, peer tutoring, study skills workshops, and financial aid review. Expected impact: 30% risk reduction (36 students, $830K annual revenue, $3.3M four-year protection).

3. **Deploy Peer Mentoring Program** pairing at-risk students with high performers (120 mentees, 120 mentors from 450 high-performer pool). Research shows peer support improves retention by 12-18%. Expected impact: 18 additional students retained ($414K four-year value), enhanced community for both groups.

4. **Create Financial Stress Rapid Response** for students experiencing aid reductions >$2K (est. 80 students annually). Emergency grant review, payment plan options, on-campus work opportunities within 72 hours. Expected impact: 10% retention improvement among this group (8 students, $184K protected annually).''',
            'bad': '''1. Provide better academic support for struggling students
2. Create programs to help at-risk students succeed
3. Monitor student progress more frequently
4. Offer financial counseling when needed'''
        },
        'min_length': 350,
        'require_numbers': True
    },
    {
        'name': 'success_amplification',
        'title': '⭐ Success Amplification Strategy',
        'phase': 2,
        'prompt_template': '''
Based on success patterns and high-performer data:

{context}

Design strategy to amplify and replicate success:

STEP 1: Identify success patterns (what makes high performers succeed)
STEP 2: Determine how to replicate these patterns for broader population
STEP 3: Recommend programs leveraging peer effects and role models
STEP 4: Estimate scaling impact

Requirements:
- Identify characteristics of successful students
- Recommend ways to scale success (peer effects, programs, culture)
- Quantify target populations and expected outcomes
- Connect to institutional goals (reputation, rankings, outcomes)

OUTPUT 2-3 strategies:
''',
        'context_focus': ['intelligent_metrics', 'relationship_discovery', 'predictive_discovery', 'domain_discovery'],
        'num_predict': 400,
        'num_ctx': 2048,
        'timeout': 25,
        'examples': {
            'good': '''1. **Scale Honors Program**: High performers (450 students, 17%, GPA ≥3.5) show strongest retention (98%) and graduation (88% in 4 years). Expand honors eligibility from 17% to 20% (+75 students) through merit scholarships and program enhancements. Expected: $2.1M additional revenue, improved rankings, enhanced brand. Peer effects benefit entire student body (research shows high-achiever proximity improves outcomes by 0.1-0.2 GPA points).

2. **Leverage Alumni Success Network**: Graduating class (450 students) represents institutional brand ambassadors. Create structured alumni mentorship connecting 900 current students with recent graduates (2:1 ratio). Research shows professional networking increases satisfaction (NPS +12 points) and enrollment referrals (+8% yield). Expected: 50 additional enrollments annually from referrals ($1.15M revenue).''',
            'bad': '''1. Expand programs for high-achieving students to include more participants
2. Create mentorship connections between successful students and others'''
        },
        'min_length': 250,
        'require_numbers': True
    }
]
