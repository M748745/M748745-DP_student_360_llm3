"""
Journey Definitions - Pre-defined structure for all 6 journeys
Approach 1: Hardcoded journey structure
Option B: LLM will generate narratives for each component
"""

# Financial Constants (configurable)
FINANCIAL_CONSTANTS = {
    'TUITION_PER_STUDENT': 65000,       # AED average
    'RECRUITMENT_COST': 7500,            # AED per student
    'DROPOUT_PREVENTION_COST': 3000,     # AED per intervention
    'EARLY_WARNING_SYSTEM_COST': 175000, # AED (range 150-200K)
    'HOUSING_REVENUE_PER_BED': 15000,    # AED annually
    'OPERATING_MARGIN_HOUSING': 0.85,    # 85%
    'CAPITAL_COST_PER_BED': 62500,       # AED (range 50-75K)

    # Benchmarks
    'AID_BENCHMARK_MIN': 15,             # % of revenue
    'AID_BENCHMARK_MAX': 35,             # % of revenue
    'HOUSING_OCCUPANCY_OPTIMAL': 90,     # %
    'UAE_NATIONAL_TARGET_MIN': 40,       # % (Vision 2030)
    'UAE_NATIONAL_TARGET_MAX': 50,       # %
    'HIGH_PERFORMER_TARGET': 35,         # % optimal
    'AT_RISK_TARGET_MAX': 15,            # % maximum acceptable

    # ROI Parameters
    'RETENTION_IMPROVEMENT_VALUE': 650000,  # AED per 1% improvement
    'INTERVENTION_SUCCESS_RATE': 0.60,      # 60% success rate
    'DROPOUT_PROBABILITY_CRITICAL': 0.70,   # 70% for GPA < 2.0
    'DROPOUT_PROBABILITY_HIGH': 0.50,       # 50% for GPA 2.0-2.49
    'DROPOUT_PROBABILITY_MODERATE': 0.20,   # 20% for GPA 2.5-2.99
}

# Journey 1: Enrollment & Student Composition
JOURNEY_1 = {
    'id': 'journey_1',
    'name': 'Journey 1: Enrollment & Student Composition',
    'subtitle': 'Understanding WHO we serve: Student demographics, market positioning, and institutional identity',
    'required_fields': ['nationality', 'visa_status', 'enrollment_type', 'cumulative_gpa'],
    'priority': 1,
    'stories': [
        {
            'id': 'story_1_1',
            'title': 'Story 1.1: Student Body Snapshot & Enrollment Profile',
            'subtitle': 'Current enrollment volume, demographic composition, and student profile overview',
            'focus_area': 'Total enrollment, nationality diversity, demographic composition',
            'required_fields': ['nationality', 'visa_status', 'gender'],
            'metrics_to_calculate': [
                'total_students',
                'nationality_count',
                'uae_nationals_count',
                'uae_nationals_pct',
                'international_count',
                'international_pct',
                'top_nationalities',
                'gender_distribution'
            ],
            'narrative_components': [
                'business_context',
                'opening_narrative',
                'data_insights',
                'business_impact',
                'findings_summary'
            ]
        },
        {
            'id': 'story_1_2',
            'title': 'Story 1.2: Market Positioning & Diversity Strategy',
            'subtitle': 'UAE vs International student performance, Vision 2030 alignment, and competitive positioning',
            'focus_area': 'Performance distribution, quality assessment, Vision 2030 alignment',
            'required_fields': ['cumulative_gpa'],
            'metrics_to_calculate': [
                'high_performers_count',
                'high_performers_pct',
                'steady_performers_count',
                'steady_performers_pct',
                'at_risk_count',
                'at_risk_pct',
                'performance_distribution'
            ],
            'narrative_components': [
                'opening_narrative',
                'data_insights',
                'business_impact',
                'findings_summary'
            ]
        },
        {
            'id': 'story_1_3',
            'title': 'Story 1.3: UAE National Performance & Vision 2030 Alignment',
            'subtitle': 'Emiratization targets, national student performance, and institutional contribution to national goals',
            'focus_area': 'UAE national academic performance, Vision 2030 compliance, comparative analysis',
            'required_fields': ['visa_status', 'cumulative_gpa', 'enrollment_enrollment_status'],
            'metrics_to_calculate': [
                'uae_gpa',
                'international_gpa',
                'gpa_difference',
                'uae_active_rate',
                'uae_high_performers',
                'vision_2030_gap'
            ],
            'narrative_components': [
                'opening_narrative',
                'data_insights',
                'business_impact',
                'findings_summary'
            ]
        }
    ]
}

# Journey 2: Revenue & Financial Strategy
JOURNEY_2 = {
    'id': 'journey_2',
    'name': 'Journey 2: Revenue & Financial Strategy',
    'subtitle': 'Understanding HOW we fund student success: Financial aid distribution, ROI, and fiscal sustainability',
    'required_fields': ['financial_aid_monetary_amount', 'enrollment_tuition_amount', 'cumulative_gpa'],
    'priority': 1,
    'stories': [
        {
            'id': 'story_2_1',
            'title': 'Story 2.1: Financial Aid Investment Overview',
            'subtitle': 'Total investment, recipient distribution, and strategic aid allocation',
            'focus_area': 'Financial aid investment volume, coverage, and distribution patterns',
            'required_fields': ['financial_aid_monetary_amount', 'enrollment_tuition_amount'],
            'metrics_to_calculate': [
                'total_aid',
                'total_students',
                'recipients',
                'coverage_rate',
                'avg_package',
                'median_package',
                'per_student_investment',
                'aid_distribution_tiers',
                'total_tuition',
                'net_revenue'
            ],
            'narrative_components': [
                'business_context',
                'opening_narrative',
                'data_insights',
                'business_impact',
                'findings_summary'
            ]
        },
        {
            'id': 'story_2_2',
            'title': 'Story 2.2: Aid Effectiveness & Student Outcomes',
            'subtitle': 'Measuring the impact of financial support on academic performance and retention',
            'focus_area': 'Aid impact on GPA, retention, and student success rates',
            'required_fields': ['financial_aid_monetary_amount', 'cumulative_gpa'],
            'metrics_to_calculate': [
                'aided_gpa',
                'non_aided_gpa',
                'gpa_difference',
                'aided_success_rate',
                'non_aided_success_rate',
                'retention_improvement_estimate',
                'cost_savings_estimate'
            ],
            'narrative_components': [
                'opening_narrative',
                'data_insights',
                'business_impact',
                'findings_summary'
            ]
        },
        {
            'id': 'story_2_3',
            'title': 'Story 2.3: Revenue Sustainability & Budget Optimization',
            'subtitle': 'Long-term financial sustainability and strategic budget allocation',
            'focus_area': 'Discount rate analysis, sustainability assessment, optimization scenarios',
            'required_fields': ['financial_aid_monetary_amount', 'enrollment_tuition_amount'],
            'metrics_to_calculate': [
                'discount_rate',
                'benchmark_comparison',
                'sustainability_status',
                'scenario_enrollment_decline_5pct',
                'scenario_aid_increase_10pct',
                'scenario_optimize_to_target',
                'recommended_adjustments'
            ],
            'narrative_components': [
                'opening_narrative',
                'data_insights',
                'business_impact',
                'scenario_analysis',
                'findings_summary',
                'action_plan'
            ]
        }
    ]
}

# Journey 3: Student Services & Operations
JOURNEY_3 = {
    'id': 'journey_3',
    'name': 'Journey 3: Student Services & Operations',
    'subtitle': 'Understanding HOW we support students: Housing operations, service delivery, and infrastructure investment',
    'required_fields': ['occupancy_status', 'cumulative_gpa'],
    'priority': 2,
    'stories': [
        {
            'id': 'story_3_1',
            'title': 'Story 3.1: Housing Operations & Capacity Management',
            'subtitle': 'Current occupancy, capacity utilization, and operational metrics',
            'focus_area': 'Housing occupancy rates, revenue generation, capacity analysis',
            'required_fields': ['occupancy_status'],
            'metrics_to_calculate': [
                'housed_students',
                'occupancy_rate',
                'housed_gpa',
                'total_rent_revenue',
                'revenue_per_bed',
                'capacity_gap'
            ],
            'narrative_components': [
                'business_context',
                'opening_narrative',
                'data_insights',
                'business_impact',
                'findings_summary'
            ]
        },
        {
            'id': 'story_3_2',
            'title': 'Story 3.2: Service Impact on Academic Performance',
            'subtitle': 'How housing and campus services drive student success and retention',
            'focus_area': 'Housing impact on GPA, retention, and student success',
            'required_fields': ['occupancy_status', 'cumulative_gpa'],
            'metrics_to_calculate': [
                'on_campus_gpa',
                'off_campus_gpa',
                'housing_gpa_advantage',
                'on_campus_high_performers',
                'off_campus_high_performers',
                'retention_benefit_estimate'
            ],
            'narrative_components': [
                'opening_narrative',
                'data_insights',
                'business_impact',
                'findings_summary'
            ]
        },
        {
            'id': 'story_3_3',
            'title': 'Story 3.3: Infrastructure ROI & Expansion Strategy',
            'subtitle': 'Investment analysis, capacity planning, and strategic expansion recommendations',
            'focus_area': 'Housing ROI, capital investment analysis, expansion planning',
            'required_fields': ['occupancy_status'],
            'metrics_to_calculate': [
                'annual_revenue',
                'operating_margin',
                'net_contribution',
                'roi_percentage',
                'payback_period',
                'expansion_opportunity',
                'expansion_roi_estimate'
            ],
            'narrative_components': [
                'opening_narrative',
                'data_insights',
                'business_impact',
                'scenario_analysis',
                'findings_summary',
                'action_plan'
            ]
        }
    ]
}

# Journey 4: Academic Performance & Outcomes
JOURNEY_4 = {
    'id': 'journey_4',
    'name': 'Journey 4: Academic Performance & Outcomes',
    'subtitle': 'Understanding HOW students perform: Academic achievement, program effectiveness, and learning outcomes',
    'required_fields': ['cumulative_gpa', 'enrollment_type', 'cohort_year'],
    'priority': 1,
    'stories': [
        {
            'id': 'story_4_1',
            'title': 'Story 4.1: Performance Distribution & Achievement Tiers',
            'subtitle': 'Academic achievement levels, GPA distribution, and student performance segments',
            'focus_area': 'Overall GPA distribution, performance tiers, achievement analysis',
            'required_fields': ['cumulative_gpa'],
            'metrics_to_calculate': [
                'avg_gpa',
                'high_performers',
                'honors_students',
                'good_standing',
                'at_risk',
                'critical_risk',
                'performance_distribution'
            ],
            'narrative_components': [
                'business_context',
                'opening_narrative',
                'data_insights',
                'business_impact',
                'findings_summary'
            ]
        },
        {
            'id': 'story_4_2',
            'title': 'Story 4.2: Program Performance & Academic Outcomes',
            'subtitle': 'Performance by academic program, major effectiveness, and program-level success rates',
            'focus_area': 'Program-level GPA comparison, quality assessment',
            'required_fields': ['enrollment_type', 'cumulative_gpa'],
            'metrics_to_calculate': [
                'program_performance',
                'top_program',
                'lowest_program',
                'performance_gap',
                'program_enrollment_distribution'
            ],
            'narrative_components': [
                'opening_narrative',
                'data_insights',
                'business_impact',
                'findings_summary'
            ]
        },
        {
            'id': 'story_4_3',
            'title': 'Story 4.3: Performance Drivers & Improvement Strategies',
            'subtitle': 'Identifying factors that drive academic success and actionable improvement initiatives',
            'focus_area': 'Performance drivers, cohort trends, intervention opportunities',
            'required_fields': ['cumulative_gpa', 'occupancy_status', 'cohort_year'],
            'metrics_to_calculate': [
                'housing_impact',
                'cohort_trends',
                'at_risk_intervention_cost',
                'potential_dropouts_preventable',
                'intervention_roi'
            ],
            'narrative_components': [
                'opening_narrative',
                'data_insights',
                'business_impact',
                'findings_summary',
                'action_plan'
            ]
        }
    ]
}

# Journey 5: Retention & Success
JOURNEY_5 = {
    'id': 'journey_5',
    'name': 'Journey 5: Retention & Success',
    'subtitle': 'Understanding WHO stays and succeeds: Retention patterns, completion rates, and student persistence',
    'required_fields': ['cumulative_gpa', 'cohort_year', 'enrollment_enrollment_status'],
    'priority': 1,
    'stories': [
        {
            'id': 'story_5_1',
            'title': 'Story 5.1: Retention Rates & Persistence Patterns',
            'subtitle': 'Student persistence across years, retention indicators, and cohort progression analysis',
            'focus_area': 'Retention rates, good standing rates, cohort persistence',
            'required_fields': ['cumulative_gpa', 'cohort_year'],
            'metrics_to_calculate': [
                'good_standing_count',
                'good_standing_pct',
                'at_risk_count',
                'persistence_rate_proxy',
                'expected_annual_attrition',
                'revenue_at_risk'
            ],
            'narrative_components': [
                'business_context',
                'opening_narrative',
                'data_insights',
                'business_impact',
                'findings_summary'
            ]
        },
        {
            'id': 'story_5_2',
            'title': 'Story 5.2: Success Factors & Completion Drivers',
            'subtitle': 'Identifying characteristics and behaviors that predict student success and timely completion',
            'focus_area': 'Success predictors, housing advantage, performance factors',
            'required_fields': ['cumulative_gpa', 'occupancy_status'],
            'metrics_to_calculate': [
                'on_campus_success_rate',
                'off_campus_success_rate',
                'housing_success_advantage',
                'success_by_gpa_tier',
                'intervention_opportunity'
            ],
            'narrative_components': [
                'opening_narrative',
                'data_insights',
                'business_impact',
                'findings_summary'
            ]
        },
        {
            'id': 'story_5_3',
            'title': 'Story 5.3: Intervention Strategies & Support Programs',
            'subtitle': 'Designing data-driven intervention programs to maximize retention and student success',
            'focus_area': 'Tiered intervention design, investment requirements, ROI modeling',
            'required_fields': ['cumulative_gpa'],
            'metrics_to_calculate': [
                'tier1_students',
                'tier1_cost',
                'tier2_students',
                'tier2_cost',
                'tier3_students',
                'tier3_cost',
                'total_intervention_cost',
                'expected_students_saved',
                'revenue_protected',
                'intervention_roi'
            ],
            'narrative_components': [
                'opening_narrative',
                'data_insights',
                'business_impact',
                'intervention_design',
                'findings_summary',
                'action_plan'
            ]
        }
    ]
}

# Journey 6: Risk Management & Mitigation
JOURNEY_6 = {
    'id': 'journey_6',
    'name': 'Journey 6: Risk Management & Mitigation',
    'subtitle': 'Understanding WHERE risks exist: Academic vulnerabilities, financial exposure, and operational threats',
    'required_fields': ['cumulative_gpa', 'financial_aid_monetary_amount', 'enrollment_tuition_amount', 'nationality', 'enrollment_type'],
    'priority': 2,
    'stories': [
        {
            'id': 'story_6_1',
            'title': 'Story 6.1: Academic Risk Identification & Early Warning',
            'subtitle': 'Identifying students at academic risk, quantifying exposure, and establishing early warning triggers',
            'focus_area': 'Academic risk assessment, revenue exposure, early warning system design',
            'required_fields': ['cumulative_gpa'],
            'metrics_to_calculate': [
                'critical_risk_count',
                'high_risk_count',
                'moderate_risk_count',
                'total_at_risk',
                'revenue_at_risk',
                'expected_dropouts',
                'expected_revenue_loss',
                'early_warning_roi'
            ],
            'narrative_components': [
                'business_context',
                'opening_narrative',
                'data_insights',
                'business_impact',
                'findings_summary'
            ]
        },
        {
            'id': 'story_6_2',
            'title': 'Story 6.2: Financial Risk & Revenue Vulnerability',
            'subtitle': 'Assessing financial aid sustainability, tuition dependency, and revenue concentration risks',
            'focus_area': 'Financial sustainability, discount rate risk, scenario analysis',
            'required_fields': ['financial_aid_monetary_amount', 'enrollment_tuition_amount'],
            'metrics_to_calculate': [
                'total_aid_committed',
                'discount_rate',
                'high_aid_students',
                'high_aid_exposure',
                'net_tuition_revenue',
                'scenario_5pct_decline',
                'scenario_10pct_aid_increase'
            ],
            'narrative_components': [
                'opening_narrative',
                'data_insights',
                'business_impact',
                'scenario_analysis',
                'findings_summary'
            ]
        },
        {
            'id': 'story_6_3',
            'title': 'Story 6.3: Operational Risk & Mitigation Strategies',
            'subtitle': 'Identifying operational vulnerabilities, capacity constraints, and implementing risk mitigation strategies',
            'focus_area': 'Concentration risks, operational vulnerabilities, composite risk scoring',
            'required_fields': ['enrollment_type', 'nationality', 'occupancy_status'],
            'metrics_to_calculate': [
                'program_concentration',
                'geo_concentration',
                'housing_capacity_gap',
                'academic_risk_score',
                'financial_risk_score',
                'operational_risk_score',
                'composite_risk_score',
                'mitigation_investment_required'
            ],
            'narrative_components': [
                'opening_narrative',
                'data_insights',
                'business_impact',
                'mitigation_strategies',
                'findings_summary',
                'action_plan'
            ]
        }
    ]
}

# Master Journey Registry
ALL_JOURNEYS = [
    JOURNEY_1,
    JOURNEY_2,
    JOURNEY_3,
    JOURNEY_4,
    JOURNEY_5,
    JOURNEY_6
]

def get_journey_by_id(journey_id: str) -> dict:
    """Get journey definition by ID"""
    for journey in ALL_JOURNEYS:
        if journey['id'] == journey_id:
            return journey
    return None

def get_all_journeys() -> list:
    """Get all journey definitions"""
    return ALL_JOURNEYS

def validate_dataset_for_journey(df, journey: dict) -> dict:
    """
    Validate if dataset has required fields for a journey
    Returns: {
        'feasible': bool,
        'missing_fields': list,
        'confidence': float (0-100)
    }
    """
    required = journey['required_fields']
    available = set(df.columns)

    missing = [field for field in required if field not in available]
    available_count = len(required) - len(missing)
    confidence = (available_count / len(required)) * 100 if required else 0

    return {
        'feasible': len(missing) == 0,
        'missing_fields': missing,
        'confidence': confidence,
        'available_pct': confidence
    }
