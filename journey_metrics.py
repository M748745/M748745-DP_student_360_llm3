"""
Journey Metrics Calculation System
Calculates all metrics for 18 stories across 6 journeys using actual dataset

Each function:
- Takes DataFrame as input
- Calculates specific metrics for a story
- Returns dict with all calculated values
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
from journey_definitions import FINANCIAL_CONSTANTS


# ============================================================================
# HELPER FUNCTIONS - Common calculations used across stories
# ============================================================================

def safe_percentage(numerator: float, denominator: float) -> float:
    """Calculate percentage safely, avoiding division by zero"""
    return (numerator / denominator * 100) if denominator > 0 else 0.0

def safe_divide(numerator: float, denominator: float) -> float:
    """Divide safely, avoiding division by zero"""
    return (numerator / denominator) if denominator > 0 else 0.0

def safe_column_mean(df: pd.DataFrame, column: str, default=0.0) -> float:
    """Safely get column mean, returning default if column doesn't exist"""
    if column in df.columns:
        try:
            return round(df[column].mean(), 1) if not df[column].empty else default
        except:
            return default
    return default

def safe_column_sum(df: pd.DataFrame, column: str, default=0) -> float:
    """Safely get column sum, returning default if column doesn't exist"""
    if column in df.columns:
        try:
            return round(df[column].sum(), 0)
        except:
            return default
    return default

def safe_column_exists(df: pd.DataFrame, column: str) -> bool:
    """Check if column exists in dataframe"""
    return column in df.columns

def get_top_n_items(series: pd.Series, n: int = 5) -> List[Tuple[str, int, float]]:
    """
    Get top N items from a series with counts and percentages
    Returns: [(item, count, percentage), ...]
    """
    total = len(series)
    value_counts = series.value_counts()
    top_items = []

    for i, (item, count) in enumerate(value_counts.head(n).items()):
        pct = safe_percentage(count, total)
        top_items.append((str(item), int(count), round(pct, 1)))

    return top_items


# ============================================================================
# JOURNEY 1: ENROLLMENT & STUDENT COMPOSITION
# ============================================================================

def calculate_story_1_1_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Story 1.1: Student Body Snapshot & Enrollment Profile
    Metrics: total students, nationality diversity, visa status, gender distribution
    """
    metrics = {}

    # Total enrollment
    metrics['total_students'] = len(df)

    # Nationality analysis
    metrics['nationality_count'] = df['nationality'].nunique()
    metrics['uae_nationals_count'] = len(df[df['nationality'] == 'UAE'])
    metrics['uae_nationals_pct'] = safe_percentage(metrics['uae_nationals_count'], metrics['total_students'])
    metrics['international_count'] = metrics['total_students'] - metrics['uae_nationals_count']
    metrics['international_pct'] = safe_percentage(metrics['international_count'], metrics['total_students'])

    # Top 5 nationalities with counts and percentages
    metrics['top_nationalities'] = get_top_n_items(df['nationality'], 5)

    # Gender distribution
    gender_counts = df['gender'].value_counts()
    metrics['gender_distribution'] = {
        'male': int(gender_counts.get('M', 0)),
        'female': int(gender_counts.get('F', 0)),
        'male_pct': safe_percentage(gender_counts.get('M', 0), metrics['total_students']),
        'female_pct': safe_percentage(gender_counts.get('F', 0), metrics['total_students'])
    }

    # Visa status breakdown
    visa_counts = df['visa_status'].value_counts()
    metrics['visa_status_distribution'] = {}
    for visa_type, count in visa_counts.items():
        metrics['visa_status_distribution'][str(visa_type)] = {
            'count': int(count),
            'pct': safe_percentage(count, metrics['total_students'])
        }

    return metrics


def calculate_story_1_2_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Story 1.2: Academic Standing & Performance Distribution
    Metrics: GPA distribution, high performers, at-risk students, academic standing
    """
    metrics = {}

    # Overall GPA metrics
    metrics['average_gpa'] = round(df['cumulative_gpa'].mean(), 3)
    metrics['median_gpa'] = round(df['cumulative_gpa'].median(), 3)
    metrics['min_gpa'] = round(df['cumulative_gpa'].min(), 3)
    metrics['max_gpa'] = round(df['cumulative_gpa'].max(), 3)

    # Performance segments
    high_performers = df[df['cumulative_gpa'] >= 3.5]
    metrics['high_performers_count'] = len(high_performers)
    metrics['high_performers_pct'] = safe_percentage(len(high_performers), len(df))

    good_standing = df[(df['cumulative_gpa'] >= 2.5) & (df['cumulative_gpa'] < 3.5)]
    metrics['good_standing_count'] = len(good_standing)
    metrics['good_standing_pct'] = safe_percentage(len(good_standing), len(df))

    at_risk = df[df['cumulative_gpa'] < 2.5]
    metrics['at_risk_count'] = len(at_risk)
    metrics['at_risk_pct'] = safe_percentage(len(at_risk), len(df))

    # Probation analysis
    probation = df[df['cumulative_gpa'] < 2.0]
    metrics['probation_count'] = len(probation)
    metrics['probation_pct'] = safe_percentage(len(probation), len(df))

    # GPA by nationality (top 5)
    top_nationalities = df['nationality'].value_counts().head(5).index
    metrics['gpa_by_nationality'] = []
    for nationality in top_nationalities:
        nat_df = df[df['nationality'] == nationality]
        metrics['gpa_by_nationality'].append({
            'nationality': nationality,
            'avg_gpa': round(nat_df['cumulative_gpa'].mean(), 3),
            'count': len(nat_df)
        })

    return metrics


def calculate_story_1_3_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Story 1.3: Enrollment Type & Program Mix
    Metrics: full-time/part-time split, enrollment trends, program distribution
    """
    metrics = {}

    # Enrollment type breakdown
    enrollment_counts = df['enrollment_type'].value_counts()
    metrics['full_time_count'] = int(enrollment_counts.get('Full Time', 0))
    metrics['full_time_pct'] = safe_percentage(metrics['full_time_count'], len(df))
    metrics['part_time_count'] = int(enrollment_counts.get('Part Time', 0))
    metrics['part_time_pct'] = safe_percentage(metrics['part_time_count'], len(df))

    # Cohort analysis
    cohort_counts = df['cohort_year'].value_counts().sort_index()
    metrics['cohort_distribution'] = []
    for year, count in cohort_counts.items():
        metrics['cohort_distribution'].append({
            'year': str(year),
            'count': int(count),
            'pct': safe_percentage(count, len(df))
        })

    # Enrollment status
    status_counts = df['enrollment_enrollment_status'].value_counts()
    metrics['enrollment_status'] = {}
    for status, count in status_counts.items():
        metrics['enrollment_status'][str(status)] = {
            'count': int(count),
            'pct': safe_percentage(count, len(df))
        }

    # Credits analysis
    metrics['avg_credits_attempted'] = safe_column_mean(df, 'credits_attempted', 0.0)
    metrics['avg_degree_progress'] = safe_column_mean(df, 'degree_progress_pct', 0.0)

    return metrics


# ============================================================================
# JOURNEY 2: REVENUE & FINANCIAL STRATEGY
# ============================================================================

def calculate_story_2_1_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Story 2.1: Tuition Revenue & Pricing Strategy
    Metrics: total tuition revenue, tuition distribution, revenue per student
    """
    metrics = {}

    # Total tuition revenue
    metrics['total_tuition_revenue'] = df['enrollment_tuition_amount'].sum()
    metrics['total_tuition_revenue_millions'] = round(metrics['total_tuition_revenue'] / 1_000_000, 2)

    # Revenue per student
    metrics['avg_tuition_per_student'] = round(df['enrollment_tuition_amount'].mean(), 0)
    metrics['median_tuition_per_student'] = round(df['enrollment_tuition_amount'].median(), 0)

    # Tuition distribution analysis
    metrics['min_tuition'] = df['enrollment_tuition_amount'].min()
    metrics['max_tuition'] = df['enrollment_tuition_amount'].max()

    # Tuition by enrollment type
    tuition_by_type = df.groupby('enrollment_type')['enrollment_tuition_amount'].agg(['sum', 'mean', 'count'])
    metrics['tuition_by_enrollment_type'] = []
    for enroll_type, row in tuition_by_type.iterrows():
        metrics['tuition_by_enrollment_type'].append({
            'type': str(enroll_type),
            'total_revenue': round(row['sum'], 0),
            'avg_tuition': round(row['mean'], 0),
            'student_count': int(row['count']),
            'pct_of_total_revenue': safe_percentage(row['sum'], metrics['total_tuition_revenue'])
        })

    # Revenue by nationality (top 5)
    revenue_by_nationality = df.groupby('nationality')['enrollment_tuition_amount'].sum().sort_values(ascending=False).head(5)
    metrics['top_revenue_nationalities'] = []
    for nationality, revenue in revenue_by_nationality.items():
        count = len(df[df['nationality'] == nationality])
        metrics['top_revenue_nationalities'].append({
            'nationality': str(nationality),
            'total_revenue': round(revenue, 0),
            'student_count': count,
            'avg_revenue_per_student': round(safe_divide(revenue, count), 0),
            'pct_of_total': safe_percentage(revenue, metrics['total_tuition_revenue'])
        })

    # Benchmark comparison (assumed benchmark: AED 65,000 per student)
    expected_revenue = len(df) * FINANCIAL_CONSTANTS['TUITION_PER_STUDENT']
    metrics['expected_revenue_at_benchmark'] = expected_revenue
    metrics['revenue_variance'] = metrics['total_tuition_revenue'] - expected_revenue
    metrics['revenue_variance_pct'] = safe_percentage(metrics['revenue_variance'], expected_revenue)

    return metrics


def calculate_story_2_2_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Story 2.2: Financial Aid Strategy & Impact
    Metrics: total aid, aid distribution, discount rate, aid effectiveness
    """
    metrics = {}

    # Total financial aid
    metrics['total_aid_given'] = df['financial_aid_monetary_amount'].sum()
    metrics['total_aid_millions'] = round(metrics['total_aid_given'] / 1_000_000, 2)

    # Students receiving aid
    students_with_aid = df[df['financial_aid_monetary_amount'] > 0]
    metrics['students_with_aid_count'] = len(students_with_aid)
    metrics['students_with_aid_pct'] = safe_percentage(len(students_with_aid), len(df))

    # Aid statistics
    metrics['avg_aid_per_student'] = round(df['financial_aid_monetary_amount'].mean(), 0)
    metrics['avg_aid_per_recipient'] = round(students_with_aid['financial_aid_monetary_amount'].mean(), 0) if len(students_with_aid) > 0 else 0
    metrics['median_aid'] = round(df['financial_aid_monetary_amount'].median(), 0)
    metrics['max_aid'] = df['financial_aid_monetary_amount'].max()

    # Discount rate calculation
    total_tuition = df['enrollment_tuition_amount'].sum()
    metrics['tuition_discount_rate'] = safe_percentage(metrics['total_aid_given'], total_tuition)

    # Aid by nationality
    aid_by_nationality = df.groupby('nationality').agg({
        'financial_aid_monetary_amount': ['sum', 'mean', 'count']
    }).sort_values(('financial_aid_monetary_amount', 'sum'), ascending=False).head(5)

    metrics['aid_by_nationality'] = []
    for nationality in aid_by_nationality.index:
        nat_data = aid_by_nationality.loc[nationality]
        total_aid = nat_data[('financial_aid_monetary_amount', 'sum')]
        metrics['aid_by_nationality'].append({
            'nationality': str(nationality),
            'total_aid': round(total_aid, 0),
            'avg_aid': round(nat_data[('financial_aid_monetary_amount', 'mean')], 0),
            'student_count': int(nat_data[('financial_aid_monetary_amount', 'count')]),
            'pct_of_total_aid': safe_percentage(total_aid, metrics['total_aid_given'])
        })

    # Aid effectiveness (correlation with GPA)
    aid_students = df[df['financial_aid_monetary_amount'] > 0]
    no_aid_students = df[df['financial_aid_monetary_amount'] == 0]

    metrics['avg_gpa_with_aid'] = round(aid_students['cumulative_gpa'].mean(), 3) if len(aid_students) > 0 else 0
    metrics['avg_gpa_without_aid'] = round(no_aid_students['cumulative_gpa'].mean(), 3) if len(no_aid_students) > 0 else 0
    metrics['gpa_difference'] = metrics['avg_gpa_with_aid'] - metrics['avg_gpa_without_aid']

    # Benchmark comparison
    benchmark_min = FINANCIAL_CONSTANTS['AID_BENCHMARK_MIN']
    benchmark_max = FINANCIAL_CONSTANTS['AID_BENCHMARK_MAX']
    metrics['discount_vs_benchmark_min'] = metrics['tuition_discount_rate'] - benchmark_min
    metrics['discount_vs_benchmark_max'] = metrics['tuition_discount_rate'] - benchmark_max
    metrics['within_benchmark'] = benchmark_min <= metrics['tuition_discount_rate'] <= benchmark_max

    return metrics


def calculate_story_2_3_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Story 2.3: Revenue Collection & Outstanding Balances
    Metrics: total balance due, collection rate, payment patterns
    """
    metrics = {}

    # Check if required column exists
    if 'balance_due' not in df.columns:
        metrics['total_balance_due'] = 0
        metrics['total_balance_millions'] = 0
        metrics['students_with_balance_count'] = 0
        metrics['students_with_balance_pct'] = 0
        metrics['note'] = 'balance_due column not available in dataset'
        return metrics

    # Total outstanding balance
    metrics['total_balance_due'] = df['balance_due'].sum()
    metrics['total_balance_millions'] = round(metrics['total_balance_due'] / 1_000_000, 2)

    # Students with balances
    students_with_balance = df[df['balance_due'] > 0]
    metrics['students_with_balance_count'] = len(students_with_balance)
    metrics['students_with_balance_pct'] = safe_percentage(len(students_with_balance), len(df))

    # Balance statistics
    metrics['avg_balance_per_student'] = round(df['balance_due'].mean(), 0)
    metrics['avg_balance_per_debtor'] = round(students_with_balance['balance_due'].mean(), 0) if len(students_with_balance) > 0 else 0
    metrics['median_balance'] = round(df['balance_due'].median(), 0)
    metrics['max_balance'] = df['balance_due'].max()

    # Collection rate calculation
    total_tuition = df['enrollment_tuition_amount'].sum()
    total_aid = df['financial_aid_monetary_amount'].sum()
    net_tuition_owed = total_tuition - total_aid
    amount_collected = net_tuition_owed - metrics['total_balance_due']
    metrics['collection_rate'] = safe_percentage(amount_collected, net_tuition_owed)

    # Balance aging (categorize by size)
    metrics['balance_categories'] = {
        'under_10k': {
            'count': len(students_with_balance[students_with_balance['balance_due'] < 10000]),
            'total': students_with_balance[students_with_balance['balance_due'] < 10000]['balance_due'].sum()
        },
        'between_10k_50k': {
            'count': len(students_with_balance[(students_with_balance['balance_due'] >= 10000) & (students_with_balance['balance_due'] < 50000)]),
            'total': students_with_balance[(students_with_balance['balance_due'] >= 10000) & (students_with_balance['balance_due'] < 50000)]['balance_due'].sum()
        },
        'above_50k': {
            'count': len(students_with_balance[students_with_balance['balance_due'] >= 50000]),
            'total': students_with_balance[students_with_balance['balance_due'] >= 50000]['balance_due'].sum()
        }
    }

    # Balance by enrollment type
    balance_by_type = df.groupby('enrollment_type')['balance_due'].agg(['sum', 'mean', 'count'])
    metrics['balance_by_enrollment_type'] = []
    for enroll_type, row in balance_by_type.iterrows():
        metrics['balance_by_enrollment_type'].append({
            'type': str(enroll_type),
            'total_balance': round(row['sum'], 0),
            'avg_balance': round(row['mean'], 0),
            'student_count': int(row['count']),
            'pct_of_total_balance': safe_percentage(row['sum'], metrics['total_balance_due'])
        })

    # Risk assessment
    high_risk_students = df[df['balance_due'] > 50000]
    metrics['high_risk_count'] = len(high_risk_students)
    metrics['high_risk_total_balance'] = high_risk_students['balance_due'].sum()
    metrics['high_risk_pct_of_total'] = safe_percentage(metrics['high_risk_total_balance'], metrics['total_balance_due'])

    return metrics


def calculate_story_2_4_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Story 2.4: Housing Revenue & Occupancy Strategy
    Metrics: housing revenue, occupancy rate, revenue per bed
    """
    metrics = {}

    # Housing occupancy
    occupied_students = df[df['occupancy_status'] == 'Occupied']
    metrics['total_beds_occupied'] = len(occupied_students)
    metrics['occupancy_rate'] = safe_percentage(len(occupied_students), len(df))

    # Housing revenue from rent (optional field)
    if 'rent_amount' in df.columns:
        metrics['total_housing_revenue'] = df['rent_amount'].sum()
        metrics['total_housing_revenue_millions'] = round(metrics['total_housing_revenue'] / 1_000_000, 2)

        # Revenue per bed
        metrics['avg_rent_per_student'] = round(df['rent_amount'].mean(), 0)
        metrics['avg_rent_per_occupied_bed'] = round(occupied_students['rent_amount'].mean(), 0) if len(occupied_students) > 0 else 0
        metrics['median_rent'] = round(df['rent_amount'].median(), 0)
    else:
        metrics['total_housing_revenue'] = 0
        metrics['total_housing_revenue_millions'] = 0
        metrics['avg_rent_per_student'] = 0
        metrics['avg_rent_per_occupied_bed'] = 0
        metrics['median_rent'] = 0

    # Rent payment analysis (optional field)
    if 'rent_paid' in df.columns:
        metrics['total_rent_paid'] = df['rent_paid'].sum()
        metrics['rent_collection_rate'] = safe_percentage(metrics['total_rent_paid'], metrics['total_housing_revenue'])
        metrics['outstanding_rent'] = metrics['total_housing_revenue'] - metrics['total_rent_paid']
    else:
        metrics['total_rent_paid'] = 0
        metrics['rent_collection_rate'] = 0
        metrics['outstanding_rent'] = 0

    # Occupancy by gender
    occupancy_by_gender = occupied_students['gender'].value_counts()
    metrics['occupancy_by_gender'] = {}
    for gender, count in occupancy_by_gender.items():
        metrics['occupancy_by_gender'][str(gender)] = {
            'count': int(count),
            'pct': safe_percentage(count, len(occupied_students))
        }

    # Revenue potential vs actual
    total_possible_students = len(df)
    expected_housing_revenue = total_possible_students * FINANCIAL_CONSTANTS['HOUSING_REVENUE_PER_BED']
    metrics['potential_housing_revenue'] = expected_housing_revenue
    metrics['revenue_gap'] = expected_housing_revenue - metrics['total_housing_revenue']
    metrics['revenue_realization_rate'] = safe_percentage(metrics['total_housing_revenue'], expected_housing_revenue)

    # Operating margin estimation
    operating_costs = metrics['total_housing_revenue'] * (1 - FINANCIAL_CONSTANTS['OPERATING_MARGIN_HOUSING'])
    operating_profit = metrics['total_housing_revenue'] - operating_costs
    metrics['estimated_operating_profit'] = round(operating_profit, 0)
    metrics['estimated_operating_margin'] = safe_percentage(operating_profit, metrics['total_housing_revenue'])

    return metrics


# ============================================================================
# JOURNEY 3: STUDENT SERVICES & OPERATIONS
# ============================================================================

def calculate_story_3_1_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Story 3.1: Housing Utilization & Capacity Management
    Metrics: occupancy patterns, capacity utilization, room allocation
    """
    metrics = {}

    # Occupancy status breakdown
    occupancy_counts = df['occupancy_status'].value_counts()
    metrics['occupied_count'] = int(occupancy_counts.get('Occupied', 0))
    metrics['vacant_count'] = int(occupancy_counts.get('Vacant', 0))
    metrics['occupancy_rate'] = safe_percentage(metrics['occupied_count'], len(df))
    metrics['vacancy_rate'] = safe_percentage(metrics['vacant_count'], len(df))

    # Capacity utilization
    total_capacity = len(df)
    metrics['total_capacity'] = total_capacity
    metrics['utilized_capacity'] = metrics['occupied_count']
    metrics['unused_capacity'] = metrics['vacant_count']
    metrics['capacity_utilization_pct'] = metrics['occupancy_rate']

    # Room allocation analysis (optional field)
    occupied_df = df[df['occupancy_status'] == 'Occupied']
    if len(occupied_df) > 0 and 'room_number' in df.columns:
        metrics['rooms_in_use'] = occupied_df['room_number'].nunique()
        metrics['avg_students_per_room'] = round(safe_divide(len(occupied_df), metrics['rooms_in_use']), 2)
    else:
        metrics['rooms_in_use'] = 0
        metrics['avg_students_per_room'] = 0

    # Occupancy by nationality
    if len(occupied_df) > 0:
        occ_by_nat = occupied_df['nationality'].value_counts().head(5)
        metrics['occupancy_by_nationality'] = []
        for nat, count in occ_by_nat.items():
            metrics['occupancy_by_nationality'].append({
                'nationality': str(nat),
                'count': int(count),
                'pct_of_occupied': safe_percentage(count, len(occupied_df))
            })
    else:
        metrics['occupancy_by_nationality'] = []

    # Occupancy by enrollment type
    if len(occupied_df) > 0:
        occ_by_type = occupied_df['enrollment_type'].value_counts()
        metrics['occupancy_by_enrollment_type'] = {}
        for enroll_type, count in occ_by_type.items():
            metrics['occupancy_by_enrollment_type'][str(enroll_type)] = {
                'count': int(count),
                'pct': safe_percentage(count, len(occupied_df))
            }
    else:
        metrics['occupancy_by_enrollment_type'] = {}

    # Revenue impact of vacancy
    vacancy_cost = metrics['vacant_count'] * FINANCIAL_CONSTANTS['HOUSING_REVENUE_PER_BED']
    metrics['revenue_loss_from_vacancy'] = vacancy_cost
    metrics['potential_additional_revenue'] = vacancy_cost

    return metrics


def calculate_story_3_2_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Story 3.2: Student Support Services Utilization
    Metrics: service needs by student segment, support patterns
    """
    metrics = {}

    # At-risk student identification
    at_risk = df[df['cumulative_gpa'] < 2.5]
    metrics['at_risk_students_count'] = len(at_risk)
    metrics['at_risk_students_pct'] = safe_percentage(len(at_risk), len(df))

    # High-need segments
    probation = df[df['cumulative_gpa'] < 2.0]
    metrics['probation_students_count'] = len(probation)
    metrics['probation_students_pct'] = safe_percentage(len(probation), len(df))

    # Financial need (students with high balances)
    financial_need = df[df['balance_due'] > 30000]
    metrics['high_balance_students_count'] = len(financial_need)
    metrics['high_balance_students_pct'] = safe_percentage(len(financial_need), len(df))

    # Combined risk (low GPA + high balance)
    combined_risk = df[(df['cumulative_gpa'] < 2.5) & (df['balance_due'] > 30000)]
    metrics['combined_risk_count'] = len(combined_risk)
    metrics['combined_risk_pct'] = safe_percentage(len(combined_risk), len(df))

    # Support needs by nationality
    metrics['support_needs_by_nationality'] = []
    top_nationalities = df['nationality'].value_counts().head(5).index
    for nat in top_nationalities:
        nat_df = df[df['nationality'] == nat]
        nat_at_risk = len(nat_df[nat_df['cumulative_gpa'] < 2.5])
        metrics['support_needs_by_nationality'].append({
            'nationality': str(nat),
            'total_students': len(nat_df),
            'at_risk_count': nat_at_risk,
            'at_risk_pct': safe_percentage(nat_at_risk, len(nat_df))
        })

    # Estimated support costs
    metrics['estimated_tutoring_cost'] = len(at_risk) * FINANCIAL_CONSTANTS['DROPOUT_PREVENTION_COST']
    metrics['estimated_financial_counseling_cost'] = len(financial_need) * 1000  # Estimated cost per student

    return metrics


def calculate_story_3_3_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Story 3.3: Operational Efficiency & Resource Allocation
    Metrics: resource utilization, cost per student, operational metrics
    """
    metrics = {}

    # Student-to-resource ratios
    total_students = len(df)
    metrics['total_students'] = total_students

    # Full-time vs part-time for resource planning
    ft_count = len(df[df['enrollment_type'] == 'Full Time'])
    pt_count = len(df[df['enrollment_type'] == 'Part Time'])

    # FTE calculation (part-time counted as 0.5)
    metrics['full_time_equivalent'] = ft_count + (pt_count * 0.5)
    metrics['fte_ratio'] = round(safe_divide(metrics['full_time_equivalent'], total_students), 3)

    # Housing utilization
    occupied = len(df[df['occupancy_status'] == 'Occupied'])
    metrics['housing_utilization_rate'] = safe_percentage(occupied, total_students)

    # Resource allocation by cohort
    metrics['students_by_cohort'] = []
    cohort_counts = df['cohort_year'].value_counts().sort_index()
    for year, count in cohort_counts.items():
        cohort_df = df[df['cohort_year'] == year]
        metrics['students_by_cohort'].append({
            'cohort_year': str(year),
            'count': int(count),
            'pct': safe_percentage(count, total_students),
            'avg_progress': round(cohort_df['degree_progress_pct'].mean(), 1)
        })

    # Operational cost estimates
    cost_per_student = 45000  # Estimated operational cost per student
    metrics['estimated_total_operational_cost'] = total_students * cost_per_student
    metrics['estimated_cost_per_fte'] = round(safe_divide(metrics['estimated_total_operational_cost'], metrics['full_time_equivalent']), 0)

    # Efficiency metrics
    tuition_revenue = df['enrollment_tuition_amount'].sum() if 'enrollment_tuition_amount' in df.columns else 0
    rent_revenue = df['rent_amount'].sum() if 'rent_amount' in df.columns else 0
    total_revenue = tuition_revenue + rent_revenue
    total_aid = df['financial_aid_monetary_amount'].sum() if 'financial_aid_monetary_amount' in df.columns else 0
    net_revenue = total_revenue - total_aid

    metrics['net_revenue'] = net_revenue
    metrics['net_revenue_per_student'] = round(safe_divide(net_revenue, total_students), 0)
    metrics['net_revenue_per_fte'] = round(safe_divide(net_revenue, metrics['full_time_equivalent']), 0)

    # Resource concentration
    metrics['avg_credits_per_student'] = round(df['credits_attempted'].mean(), 1)
    metrics['avg_degree_completion'] = round(df['degree_progress_pct'].mean(), 1)

    return metrics


# ============================================================================
# JOURNEY 4: ACADEMIC PERFORMANCE & OUTCOMES
# ============================================================================

def calculate_story_4_1_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Story 4.1: Overall Academic Performance
    Metrics: GPA distribution, academic excellence, performance trends
    """
    metrics = {}

    # Overall GPA statistics
    metrics['average_gpa'] = round(df['cumulative_gpa'].mean(), 3)
    metrics['median_gpa'] = round(df['cumulative_gpa'].median(), 3)
    metrics['std_dev_gpa'] = round(df['cumulative_gpa'].std(), 3)
    metrics['min_gpa'] = round(df['cumulative_gpa'].min(), 3)
    metrics['max_gpa'] = round(df['cumulative_gpa'].max(), 3)

    # Performance distribution
    excellent = df[df['cumulative_gpa'] >= 3.75]
    high = df[(df['cumulative_gpa'] >= 3.5) & (df['cumulative_gpa'] < 3.75)]
    good = df[(df['cumulative_gpa'] >= 3.0) & (df['cumulative_gpa'] < 3.5)]
    satisfactory = df[(df['cumulative_gpa'] >= 2.5) & (df['cumulative_gpa'] < 3.0)]
    at_risk = df[(df['cumulative_gpa'] >= 2.0) & (df['cumulative_gpa'] < 2.5)]
    probation = df[df['cumulative_gpa'] < 2.0]

    metrics['performance_distribution'] = {
        'excellent_3.75+': {'count': len(excellent), 'pct': safe_percentage(len(excellent), len(df))},
        'high_3.5-3.75': {'count': len(high), 'pct': safe_percentage(len(high), len(df))},
        'good_3.0-3.5': {'count': len(good), 'pct': safe_percentage(len(good), len(df))},
        'satisfactory_2.5-3.0': {'count': len(satisfactory), 'pct': safe_percentage(len(satisfactory), len(df))},
        'at_risk_2.0-2.5': {'count': len(at_risk), 'pct': safe_percentage(len(at_risk), len(df))},
        'probation_below_2.0': {'count': len(probation), 'pct': safe_percentage(len(probation), len(df))}
    }

    # Academic excellence
    metrics['honors_eligible_count'] = len(df[df['cumulative_gpa'] >= 3.5])
    metrics['honors_eligible_pct'] = safe_percentage(metrics['honors_eligible_count'], len(df))

    # Performance by enrollment type
    metrics['gpa_by_enrollment_type'] = []
    for enroll_type in df['enrollment_type'].unique():
        type_df = df[df['enrollment_type'] == enroll_type]
        metrics['gpa_by_enrollment_type'].append({
            'type': str(enroll_type),
            'avg_gpa': round(type_df['cumulative_gpa'].mean(), 3),
            'median_gpa': round(type_df['cumulative_gpa'].median(), 3),
            'count': len(type_df)
        })

    # Grade point analysis
    metrics['avg_grade_point'] = round(df['grade_point'].mean(), 2)
    metrics['total_quality_points'] = round(df['grade_point'].sum(), 0)

    return metrics


def calculate_story_4_2_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Story 4.2: Academic Progress & Degree Completion
    Metrics: degree progress, completion rates, credit accumulation
    """
    metrics = {}

    # Overall progress
    metrics['avg_degree_progress_pct'] = round(df['degree_progress_pct'].mean(), 1)
    metrics['median_degree_progress'] = round(df['degree_progress_pct'].median(), 1)

    # Progress segments
    near_completion = df[df['degree_progress_pct'] >= 75]
    on_track = df[(df['degree_progress_pct'] >= 50) & (df['degree_progress_pct'] < 75)]
    mid_progress = df[(df['degree_progress_pct'] >= 25) & (df['degree_progress_pct'] < 50)]
    early_stage = df[df['degree_progress_pct'] < 25]

    metrics['progress_distribution'] = {
        'near_completion_75+': {'count': len(near_completion), 'pct': safe_percentage(len(near_completion), len(df))},
        'on_track_50-75': {'count': len(on_track), 'pct': safe_percentage(len(on_track), len(df))},
        'mid_progress_25-50': {'count': len(mid_progress), 'pct': safe_percentage(len(mid_progress), len(df))},
        'early_stage_0-25': {'count': len(early_stage), 'pct': safe_percentage(len(early_stage), len(df))}
    }

    # Credit accumulation
    metrics['avg_credits_attempted'] = round(df['credits_attempted'].mean(), 1)
    metrics['median_credits_attempted'] = round(df['credits_attempted'].median(), 1)
    metrics['total_credits_attempted'] = df['credits_attempted'].sum()

    # Progress by cohort
    metrics['progress_by_cohort'] = []
    for cohort in sorted(df['cohort_year'].unique()):
        cohort_df = df[df['cohort_year'] == cohort]
        metrics['progress_by_cohort'].append({
            'cohort_year': str(cohort),
            'avg_progress': round(cohort_df['degree_progress_pct'].mean(), 1),
            'avg_credits': round(cohort_df['credits_attempted'].mean(), 1),
            'count': len(cohort_df)
        })

    # Time to completion estimate
    # Assuming 120 credits for degree, calculate average pace
    students_with_progress = df[df['degree_progress_pct'] > 0]
    if len(students_with_progress) > 0:
        avg_progress_rate = students_with_progress['degree_progress_pct'].mean() / 100
        metrics['estimated_avg_time_to_completion_years'] = round(1 / avg_progress_rate, 1) if avg_progress_rate > 0 else 0
    else:
        metrics['estimated_avg_time_to_completion_years'] = 0

    # At-risk for non-completion (low progress + low GPA)
    at_risk_completion = df[(df['degree_progress_pct'] < 25) & (df['cumulative_gpa'] < 2.5)]
    metrics['at_risk_completion_count'] = len(at_risk_completion)
    metrics['at_risk_completion_pct'] = safe_percentage(len(at_risk_completion), len(df))

    return metrics


def calculate_story_4_3_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Story 4.3: Performance Gaps & Equity Analysis
    Metrics: performance by demographics, equity gaps, intervention needs
    """
    metrics = {}

    # Overall baseline
    overall_avg_gpa = df['cumulative_gpa'].mean()
    metrics['overall_avg_gpa'] = round(overall_avg_gpa, 3)

    # Performance by nationality
    metrics['gpa_by_nationality'] = []
    top_nationalities = df['nationality'].value_counts().head(5).index
    for nat in top_nationalities:
        nat_df = df[df['nationality'] == nat]
        nat_avg_gpa = nat_df['cumulative_gpa'].mean()
        gap = nat_avg_gpa - overall_avg_gpa

        metrics['gpa_by_nationality'].append({
            'nationality': str(nat),
            'avg_gpa': round(nat_avg_gpa, 3),
            'count': len(nat_df),
            'gap_from_overall': round(gap, 3),
            'at_risk_count': len(nat_df[nat_df['cumulative_gpa'] < 2.5]),
            'at_risk_pct': safe_percentage(len(nat_df[nat_df['cumulative_gpa'] < 2.5]), len(nat_df))
        })

    # UAE vs International performance gap
    uae_students = df[df['nationality'] == 'UAE']
    intl_students = df[df['nationality'] != 'UAE']

    metrics['uae_avg_gpa'] = round(uae_students['cumulative_gpa'].mean(), 3) if len(uae_students) > 0 else 0
    metrics['intl_avg_gpa'] = round(intl_students['cumulative_gpa'].mean(), 3) if len(intl_students) > 0 else 0
    metrics['uae_intl_gpa_gap'] = round(metrics['uae_avg_gpa'] - metrics['intl_avg_gpa'], 3)

    # Performance by gender
    metrics['gpa_by_gender'] = []
    for gender in df['gender'].unique():
        gender_df = df[df['gender'] == gender]
        gender_avg_gpa = gender_df['cumulative_gpa'].mean()
        gap = gender_avg_gpa - overall_avg_gpa

        metrics['gpa_by_gender'].append({
            'gender': str(gender),
            'avg_gpa': round(gender_avg_gpa, 3),
            'count': len(gender_df),
            'gap_from_overall': round(gap, 3)
        })

    # Performance by financial aid status
    with_aid = df[df['financial_aid_monetary_amount'] > 0]
    without_aid = df[df['financial_aid_monetary_amount'] == 0]

    metrics['avg_gpa_with_aid'] = round(with_aid['cumulative_gpa'].mean(), 3) if len(with_aid) > 0 else 0
    metrics['avg_gpa_without_aid'] = round(without_aid['cumulative_gpa'].mean(), 3) if len(without_aid) > 0 else 0
    metrics['aid_gpa_gap'] = round(metrics['avg_gpa_with_aid'] - metrics['avg_gpa_without_aid'], 3)

    # Equity concern areas (segments significantly below average)
    metrics['equity_concerns'] = []
    threshold_gap = -0.3  # Segments 0.3 GPA points below average

    for nat_data in metrics['gpa_by_nationality']:
        if nat_data['gap_from_overall'] < threshold_gap:
            metrics['equity_concerns'].append({
                'segment': f"{nat_data['nationality']} students",
                'avg_gpa': nat_data['avg_gpa'],
                'gap': nat_data['gap_from_overall'],
                'students_affected': nat_data['count']
            })

    return metrics


# ============================================================================
# JOURNEY 5: RETENTION & SUCCESS
# ============================================================================

def calculate_story_5_1_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Story 5.1: Retention Patterns & Trends
    Metrics: retention rates, enrollment status, cohort persistence
    """
    metrics = {}

    # Enrollment status breakdown
    status_counts = df['enrollment_enrollment_status'].value_counts()
    metrics['active_count'] = int(status_counts.get('Active', 0))
    metrics['active_pct'] = safe_percentage(metrics['active_count'], len(df))

    # Enrollment status distribution
    metrics['enrollment_status_distribution'] = {}
    for status, count in status_counts.items():
        metrics['enrollment_status_distribution'][str(status)] = {
            'count': int(count),
            'pct': safe_percentage(count, len(df))
        }

    # Cohort persistence
    metrics['cohort_retention'] = []
    for cohort in sorted(df['cohort_year'].unique()):
        cohort_df = df[df['cohort_year'] == cohort]
        active_in_cohort = len(cohort_df[cohort_df['enrollment_enrollment_status'] == 'Active'])

        metrics['cohort_retention'].append({
            'cohort_year': str(cohort),
            'total_students': len(cohort_df),
            'active_students': active_in_cohort,
            'retention_rate': safe_percentage(active_in_cohort, len(cohort_df)),
            'avg_progress': round(cohort_df['degree_progress_pct'].mean(), 1)
        })

    # Full-time vs part-time retention
    metrics['retention_by_enrollment_type'] = []
    for enroll_type in df['enrollment_type'].unique():
        type_df = df[df['enrollment_type'] == enroll_type]
        active_count = len(type_df[type_df['enrollment_enrollment_status'] == 'Active'])

        metrics['retention_by_enrollment_type'].append({
            'type': str(enroll_type),
            'total_students': len(type_df),
            'active_students': active_count,
            'retention_rate': safe_percentage(active_count, len(type_df))
        })

    # At-risk for dropout (low GPA + low progress)
    at_risk_dropout = df[(df['cumulative_gpa'] < 2.0) | (df['degree_progress_pct'] < 15)]
    metrics['at_risk_dropout_count'] = len(at_risk_dropout)
    metrics['at_risk_dropout_pct'] = safe_percentage(len(at_risk_dropout), len(df))

    return metrics


def calculate_story_5_2_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Story 5.2: Student Success Indicators
    Metrics: success markers, achievement rates, milestone completion
    """
    metrics = {}

    # High achievers (GPA >= 3.5 + Progress >= 50%)
    high_achievers = df[(df['cumulative_gpa'] >= 3.5) & (df['degree_progress_pct'] >= 50)]
    metrics['high_achievers_count'] = len(high_achievers)
    metrics['high_achievers_pct'] = safe_percentage(len(high_achievers), len(df))

    # On-track students (GPA >= 2.5 + Progress on pace)
    on_track = df[(df['cumulative_gpa'] >= 2.5) & (df['degree_progress_pct'] >= 25)]
    metrics['on_track_count'] = len(on_track)
    metrics['on_track_pct'] = safe_percentage(len(on_track), len(df))

    # Academic honors eligibility
    honors = df[df['cumulative_gpa'] >= 3.5]
    metrics['honors_eligible_count'] = len(honors)
    metrics['honors_eligible_pct'] = safe_percentage(len(honors), len(df))

    # Dean's list (GPA >= 3.75)
    deans_list = df[df['cumulative_gpa'] >= 3.75]
    metrics['deans_list_count'] = len(deans_list)
    metrics['deans_list_pct'] = safe_percentage(len(deans_list), len(df))

    # Credit accumulation success
    high_credit_earners = df[df['credits_attempted'] >= 90]
    metrics['high_credit_earners_count'] = len(high_credit_earners)
    metrics['high_credit_earners_pct'] = safe_percentage(len(high_credit_earners), len(df))

    # Combined success metric (high GPA + high progress + high credits)
    comprehensive_success = df[(df['cumulative_gpa'] >= 3.5) &
                               (df['degree_progress_pct'] >= 75) &
                               (df['credits_attempted'] >= 90)]
    metrics['comprehensive_success_count'] = len(comprehensive_success)
    metrics['comprehensive_success_pct'] = safe_percentage(len(comprehensive_success), len(df))

    # Success by nationality
    metrics['success_by_nationality'] = []
    top_nationalities = df['nationality'].value_counts().head(5).index
    for nat in top_nationalities:
        nat_df = df[df['nationality'] == nat]
        nat_high_achievers = len(nat_df[(nat_df['cumulative_gpa'] >= 3.5) & (nat_df['degree_progress_pct'] >= 50)])

        metrics['success_by_nationality'].append({
            'nationality': str(nat),
            'total_students': len(nat_df),
            'high_achievers': nat_high_achievers,
            'success_rate': safe_percentage(nat_high_achievers, len(nat_df))
        })

    return metrics


def calculate_story_5_3_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Story 5.3: Intervention & Support Impact
    Metrics: intervention needs, support effectiveness, risk mitigation
    """
    metrics = {}

    # Students needing intervention
    academic_intervention = df[df['cumulative_gpa'] < 2.5]
    metrics['academic_intervention_needed'] = len(academic_intervention)
    metrics['academic_intervention_pct'] = safe_percentage(len(academic_intervention), len(df))

    # Critical intervention (probation)
    critical_intervention = df[df['cumulative_gpa'] < 2.0]
    metrics['critical_intervention_needed'] = len(critical_intervention)
    metrics['critical_intervention_pct'] = safe_percentage(len(critical_intervention), len(df))

    # Financial intervention (high balances)
    financial_intervention = df[df['balance_due'] > 30000]
    metrics['financial_intervention_needed'] = len(financial_intervention)
    metrics['financial_intervention_pct'] = safe_percentage(len(financial_intervention), len(df))

    # Multi-factor risk (academic + financial)
    multi_risk = df[(df['cumulative_gpa'] < 2.5) & (df['balance_due'] > 30000)]
    metrics['multi_risk_students'] = len(multi_risk)
    metrics['multi_risk_pct'] = safe_percentage(len(multi_risk), len(df))

    # Estimated intervention costs
    metrics['estimated_academic_support_cost'] = len(academic_intervention) * FINANCIAL_CONSTANTS['DROPOUT_PREVENTION_COST']
    metrics['estimated_critical_support_cost'] = len(critical_intervention) * (FINANCIAL_CONSTANTS['DROPOUT_PREVENTION_COST'] * 2)
    metrics['total_estimated_intervention_cost'] = metrics['estimated_academic_support_cost'] + metrics['estimated_critical_support_cost']

    # ROI of intervention (prevent dropout = save tuition revenue)
    # Assume 30% of at-risk students would drop out without intervention
    potential_dropouts = len(academic_intervention) * 0.3
    saved_revenue = potential_dropouts * FINANCIAL_CONSTANTS['TUITION_PER_STUDENT']
    intervention_roi = safe_divide(saved_revenue - metrics['total_estimated_intervention_cost'],
                                   metrics['total_estimated_intervention_cost']) * 100

    metrics['potential_dropouts_prevented'] = round(potential_dropouts, 0)
    metrics['estimated_saved_revenue'] = round(saved_revenue, 0)
    metrics['intervention_roi_pct'] = round(intervention_roi, 1)

    # Success of aid recipients (as proxy for intervention effectiveness)
    aid_recipients = df[df['financial_aid_monetary_amount'] > 0]
    successful_aid_recipients = len(aid_recipients[aid_recipients['cumulative_gpa'] >= 2.5])
    metrics['aid_recipients_successful'] = successful_aid_recipients
    metrics['aid_success_rate'] = safe_percentage(successful_aid_recipients, len(aid_recipients))

    # Priority intervention list by cohort
    metrics['intervention_priority_by_cohort'] = []
    for cohort in sorted(df['cohort_year'].unique()):
        cohort_df = df[df['cohort_year'] == cohort]
        cohort_at_risk = len(cohort_df[cohort_df['cumulative_gpa'] < 2.5])

        metrics['intervention_priority_by_cohort'].append({
            'cohort_year': str(cohort),
            'total_students': len(cohort_df),
            'at_risk_count': cohort_at_risk,
            'at_risk_pct': safe_percentage(cohort_at_risk, len(cohort_df)),
            'priority_level': 'High' if safe_percentage(cohort_at_risk, len(cohort_df)) > 30 else 'Medium' if safe_percentage(cohort_at_risk, len(cohort_df)) > 15 else 'Low'
        })

    return metrics


# ============================================================================
# JOURNEY 6: RISK MANAGEMENT & MITIGATION
# ============================================================================

def calculate_story_6_1_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Story 6.1: Financial Risk Assessment
    Metrics: revenue at risk, collection risks, financial exposure
    """
    metrics = {}

    # Total financial exposure
    metrics['total_balance_due'] = df['balance_due'].sum()
    metrics['total_balance_millions'] = round(metrics['total_balance_due'] / 1_000_000, 2)

    # High-risk financial students
    high_risk_balance = df[df['balance_due'] > 50000]
    metrics['high_risk_count'] = len(high_risk_balance)
    metrics['high_risk_pct'] = safe_percentage(len(high_risk_balance), len(df))
    metrics['high_risk_total_exposure'] = high_risk_balance['balance_due'].sum()
    metrics['high_risk_exposure_pct'] = safe_percentage(metrics['high_risk_total_exposure'], metrics['total_balance_due'])

    # Revenue at risk by segment
    at_risk_academic = df[df['cumulative_gpa'] < 2.0]
    metrics['revenue_at_risk_academic'] = at_risk_academic['balance_due'].sum()
    metrics['revenue_at_risk_academic_millions'] = round(metrics['revenue_at_risk_academic'] / 1_000_000, 2)

    # Potential revenue loss (students likely to drop out)
    high_dropout_risk = df[(df['cumulative_gpa'] < 2.0) | (df['balance_due'] > 50000)]
    future_tuition_at_risk = len(high_dropout_risk) * FINANCIAL_CONSTANTS['TUITION_PER_STUDENT'] * 0.5  # Assume half a year lost
    metrics['potential_dropout_count'] = len(high_dropout_risk)
    metrics['future_revenue_at_risk'] = future_tuition_at_risk
    metrics['future_revenue_at_risk_millions'] = round(future_tuition_at_risk / 1_000_000, 2)

    # Collection risk tiers
    metrics['collection_risk_tiers'] = {
        'low_risk_under_10k': {
            'count': len(df[(df['balance_due'] > 0) & (df['balance_due'] < 10000)]),
            'total_balance': df[(df['balance_due'] > 0) & (df['balance_due'] < 10000)]['balance_due'].sum()
        },
        'medium_risk_10k_50k': {
            'count': len(df[(df['balance_due'] >= 10000) & (df['balance_due'] < 50000)]),
            'total_balance': df[(df['balance_due'] >= 10000) & (df['balance_due'] < 50000)]['balance_due'].sum()
        },
        'high_risk_above_50k': {
            'count': len(high_risk_balance),
            'total_balance': metrics['high_risk_total_exposure']
        }
    }

    # Bad debt provision estimate (5% of total balance due)
    metrics['estimated_bad_debt_provision'] = metrics['total_balance_due'] * 0.05
    metrics['estimated_bad_debt_millions'] = round(metrics['estimated_bad_debt_provision'] / 1_000_000, 2)

    return metrics


def calculate_story_6_2_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Story 6.2: Academic Risk & Retention Threats
    Metrics: academic risk levels, dropout probability, intervention urgency
    """
    metrics = {}

    # Academic risk segmentation
    critical_risk = df[df['cumulative_gpa'] < 2.0]
    high_risk = df[(df['cumulative_gpa'] >= 2.0) & (df['cumulative_gpa'] < 2.5)]
    moderate_risk = df[(df['cumulative_gpa'] >= 2.5) & (df['cumulative_gpa'] < 3.0)]

    metrics['critical_risk_count'] = len(critical_risk)
    metrics['critical_risk_pct'] = safe_percentage(len(critical_risk), len(df))
    metrics['high_risk_count'] = len(high_risk)
    metrics['high_risk_pct'] = safe_percentage(len(high_risk), len(df))
    metrics['moderate_risk_count'] = len(moderate_risk)
    metrics['moderate_risk_pct'] = safe_percentage(len(moderate_risk), len(df))

    # Compound risk factors
    # Factor 1: Low GPA + Low progress
    low_gpa_low_progress = df[(df['cumulative_gpa'] < 2.5) & (df['degree_progress_pct'] < 25)]
    metrics['compound_risk_academic'] = len(low_gpa_low_progress)
    metrics['compound_risk_academic_pct'] = safe_percentage(len(low_gpa_low_progress), len(df))

    # Factor 2: Low GPA + High balance
    low_gpa_high_balance = df[(df['cumulative_gpa'] < 2.5) & (df['balance_due'] > 30000)]
    metrics['compound_risk_financial'] = len(low_gpa_high_balance)
    metrics['compound_risk_financial_pct'] = safe_percentage(len(low_gpa_high_balance), len(df))

    # Triple threat: Low GPA + Low progress + High balance
    triple_threat = df[(df['cumulative_gpa'] < 2.5) &
                       (df['degree_progress_pct'] < 25) &
                       (df['balance_due'] > 30000)]
    metrics['triple_threat_count'] = len(triple_threat)
    metrics['triple_threat_pct'] = safe_percentage(len(triple_threat), len(df))

    # Dropout probability estimation
    # Critical risk: 60% dropout probability
    # High risk: 30% dropout probability
    # Moderate risk: 10% dropout probability
    estimated_dropouts = (len(critical_risk) * 0.6) + (len(high_risk) * 0.3) + (len(moderate_risk) * 0.1)
    metrics['estimated_dropouts'] = round(estimated_dropouts, 0)
    metrics['estimated_dropout_rate'] = safe_percentage(estimated_dropouts, len(df))

    # Revenue impact of potential dropouts
    revenue_loss_from_dropouts = estimated_dropouts * FINANCIAL_CONSTANTS['TUITION_PER_STUDENT']
    metrics['estimated_revenue_loss_from_dropouts'] = revenue_loss_from_dropouts
    metrics['estimated_revenue_loss_millions'] = round(revenue_loss_from_dropouts / 1_000_000, 2)

    # Intervention capacity needed
    total_at_risk = len(critical_risk) + len(high_risk)
    metrics['students_needing_immediate_intervention'] = total_at_risk
    metrics['intervention_capacity_needed_pct'] = safe_percentage(total_at_risk, len(df))

    return metrics


def calculate_story_6_3_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Story 6.3: Mitigation Strategies & ROI
    Metrics: intervention costs, expected outcomes, ROI of risk mitigation
    """
    metrics = {}

    # Intervention population
    critical_risk = len(df[df['cumulative_gpa'] < 2.0])
    high_risk = len(df[(df['cumulative_gpa'] >= 2.0) & (df['cumulative_gpa'] < 2.5)])
    financial_risk = len(df[df['balance_due'] > 30000])

    metrics['critical_risk_students'] = critical_risk
    metrics['high_risk_students'] = high_risk
    metrics['financial_risk_students'] = financial_risk

    # Intervention costs
    # Critical risk: intensive support (2x cost)
    # High risk: standard support (1x cost)
    # Early warning system: one-time cost

    critical_cost = critical_risk * FINANCIAL_CONSTANTS['DROPOUT_PREVENTION_COST'] * 2
    high_cost = high_risk * FINANCIAL_CONSTANTS['DROPOUT_PREVENTION_COST']
    early_warning_cost = FINANCIAL_CONSTANTS['EARLY_WARNING_SYSTEM_COST']

    metrics['critical_intervention_cost'] = critical_cost
    metrics['high_intervention_cost'] = high_cost
    metrics['early_warning_system_cost'] = early_warning_cost
    metrics['total_intervention_cost'] = critical_cost + high_cost + early_warning_cost
    metrics['total_intervention_cost_millions'] = round(metrics['total_intervention_cost'] / 1_000_000, 2)

    # Expected outcomes with intervention
    # Assume interventions reduce dropout by:
    # - Critical: from 60% to 30% (50% reduction)
    # - High: from 30% to 10% (67% reduction)

    dropouts_without_intervention = (critical_risk * 0.6) + (high_risk * 0.3)
    dropouts_with_intervention = (critical_risk * 0.3) + (high_risk * 0.1)
    dropouts_prevented = dropouts_without_intervention - dropouts_with_intervention

    metrics['expected_dropouts_without_intervention'] = round(dropouts_without_intervention, 0)
    metrics['expected_dropouts_with_intervention'] = round(dropouts_with_intervention, 0)
    metrics['dropouts_prevented'] = round(dropouts_prevented, 0)

    # Revenue saved from preventing dropouts
    # Each prevented dropout saves 2 years of tuition on average
    revenue_saved = dropouts_prevented * FINANCIAL_CONSTANTS['TUITION_PER_STUDENT'] * 2
    metrics['revenue_saved'] = revenue_saved
    metrics['revenue_saved_millions'] = round(revenue_saved / 1_000_000, 2)

    # ROI calculation
    roi = safe_divide(revenue_saved - metrics['total_intervention_cost'], metrics['total_intervention_cost']) * 100
    metrics['intervention_roi_pct'] = round(roi, 1)
    metrics['net_benefit'] = revenue_saved - metrics['total_intervention_cost']
    metrics['net_benefit_millions'] = round(metrics['net_benefit'] / 1_000_000, 2)

    # Scenario analysis
    metrics['scenarios'] = {
        'pessimistic': {
            'description': '30% dropout prevention success',
            'dropouts_prevented': round(dropouts_prevented * 0.3, 0),
            'revenue_saved': round(revenue_saved * 0.3, 0),
            'roi_pct': round(safe_divide((revenue_saved * 0.3) - metrics['total_intervention_cost'], metrics['total_intervention_cost']) * 100, 1)
        },
        'realistic': {
            'description': '50% dropout prevention success',
            'dropouts_prevented': round(dropouts_prevented * 0.5, 0),
            'revenue_saved': round(revenue_saved * 0.5, 0),
            'roi_pct': round(safe_divide((revenue_saved * 0.5) - metrics['total_intervention_cost'], metrics['total_intervention_cost']) * 100, 1)
        },
        'optimistic': {
            'description': '70% dropout prevention success',
            'dropouts_prevented': round(dropouts_prevented * 0.7, 0),
            'revenue_saved': round(revenue_saved * 0.7, 0),
            'roi_pct': round(safe_divide((revenue_saved * 0.7) - metrics['total_intervention_cost'], metrics['total_intervention_cost']) * 100, 1)
        }
    }

    # Break-even analysis
    break_even_dropouts = metrics['total_intervention_cost'] / (FINANCIAL_CONSTANTS['TUITION_PER_STUDENT'] * 2)
    metrics['break_even_dropouts_prevented'] = round(break_even_dropouts, 1)
    metrics['break_even_success_rate_pct'] = safe_percentage(break_even_dropouts, dropouts_prevented)

    return metrics


# ============================================================================
# MAIN CALCULATOR ORCHESTRATOR
# ============================================================================

def calculate_all_journey_metrics(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    Calculate all metrics for all 18 stories across 6 journeys

    Args:
        df: Student dataset DataFrame

    Returns:
        Dictionary with structure:
        {
            'journey_1': {
                'story_1_1': {...metrics...},
                'story_1_2': {...metrics...},
                'story_1_3': {...metrics...}
            },
            'journey_2': {...},
            ...
        }
    """
    # Safety check for empty dataset
    if df is None or len(df) == 0:
        print("⚠️ Warning: Empty dataset provided. Returning empty metrics.")
        return {
            'journey_1': {'story_1_1': {'error': 'Empty dataset'}, 'story_1_2': {'error': 'Empty dataset'}, 'story_1_3': {'error': 'Empty dataset'}},
            'journey_2': {'story_2_1': {'error': 'Empty dataset'}, 'story_2_2': {'error': 'Empty dataset'}, 'story_2_3': {'error': 'Empty dataset'}, 'story_2_4': {'error': 'Empty dataset'}},
            'journey_3': {'story_3_1': {'error': 'Empty dataset'}, 'story_3_2': {'error': 'Empty dataset'}, 'story_3_3': {'error': 'Empty dataset'}},
            'journey_4': {'story_4_1': {'error': 'Empty dataset'}, 'story_4_2': {'error': 'Empty dataset'}, 'story_4_3': {'error': 'Empty dataset'}},
            'journey_5': {'story_5_1': {'error': 'Empty dataset'}, 'story_5_2': {'error': 'Empty dataset'}, 'story_5_3': {'error': 'Empty dataset'}},
            'journey_6': {'story_6_1': {'error': 'Empty dataset'}, 'story_6_2': {'error': 'Empty dataset'}, 'story_6_3': {'error': 'Empty dataset'}}
        }

    all_metrics = {}

    # Helper function to safely calculate story metrics
    def safe_calculate(calc_func, story_id):
        try:
            return calc_func(df)
        except ZeroDivisionError as e:
            print(f"⚠️ Warning: Division by zero in {story_id}. Using empty metrics.")
            return {'error': f'Division by zero: {str(e)}'}
        except KeyError as e:
            # Column doesn't exist - this is expected for datasets with different schemas
            # Return empty metrics without printing warning (less noise)
            return {'error': f'Missing column: {str(e)}', 'note': 'Column not in dataset'}
        except Exception as e:
            # Only print warning for unexpected errors, not missing columns
            if 'KeyError' not in str(type(e).__name__):
                print(f"⚠️ Warning: Error calculating {story_id}: {str(e)}")
            return {'error': str(e)}

    # Journey 1: Enrollment & Student Composition
    all_metrics['journey_1'] = {
        'story_1_1': safe_calculate(calculate_story_1_1_metrics, 'story_1_1'),
        'story_1_2': safe_calculate(calculate_story_1_2_metrics, 'story_1_2'),
        'story_1_3': safe_calculate(calculate_story_1_3_metrics, 'story_1_3')
    }

    # Journey 2: Revenue & Financial Strategy
    all_metrics['journey_2'] = {
        'story_2_1': safe_calculate(calculate_story_2_1_metrics, 'story_2_1'),
        'story_2_2': safe_calculate(calculate_story_2_2_metrics, 'story_2_2'),
        'story_2_3': safe_calculate(calculate_story_2_3_metrics, 'story_2_3'),
        'story_2_4': safe_calculate(calculate_story_2_4_metrics, 'story_2_4')
    }

    # Journey 3: Student Services & Operations
    all_metrics['journey_3'] = {
        'story_3_1': safe_calculate(calculate_story_3_1_metrics, 'story_3_1'),
        'story_3_2': safe_calculate(calculate_story_3_2_metrics, 'story_3_2'),
        'story_3_3': safe_calculate(calculate_story_3_3_metrics, 'story_3_3')
    }

    # Journey 4: Academic Performance & Outcomes
    all_metrics['journey_4'] = {
        'story_4_1': safe_calculate(calculate_story_4_1_metrics, 'story_4_1'),
        'story_4_2': safe_calculate(calculate_story_4_2_metrics, 'story_4_2'),
        'story_4_3': safe_calculate(calculate_story_4_3_metrics, 'story_4_3')
    }

    # Journey 5: Retention & Success
    all_metrics['journey_5'] = {
        'story_5_1': safe_calculate(calculate_story_5_1_metrics, 'story_5_1'),
        'story_5_2': safe_calculate(calculate_story_5_2_metrics, 'story_5_2'),
        'story_5_3': safe_calculate(calculate_story_5_3_metrics, 'story_5_3')
    }

    # Journey 6: Risk Management & Mitigation
    all_metrics['journey_6'] = {
        'story_6_1': safe_calculate(calculate_story_6_1_metrics, 'story_6_1'),
        'story_6_2': safe_calculate(calculate_story_6_2_metrics, 'story_6_2'),
        'story_6_3': safe_calculate(calculate_story_6_3_metrics, 'story_6_3')
    }

    return all_metrics


def calculate_journey_metrics(df: pd.DataFrame, journey_id: str) -> Dict[str, Any]:
    """
    Calculate metrics for a specific journey

    Args:
        df: Student dataset DataFrame
        journey_id: Journey identifier (e.g., 'journey_1')

    Returns:
        Dictionary with all story metrics for the journey
    """
    all_metrics = calculate_all_journey_metrics(df)
    return all_metrics.get(journey_id, {})


def calculate_story_metrics(df: pd.DataFrame, journey_id: str, story_id: str) -> Dict[str, Any]:
    """
    Calculate metrics for a specific story

    Args:
        df: Student dataset DataFrame
        journey_id: Journey identifier (e.g., 'journey_1')
        story_id: Story identifier (e.g., 'story_1_1')

    Returns:
        Dictionary with all metrics for the story
    """
    journey_metrics = calculate_journey_metrics(df, journey_id)
    return journey_metrics.get(story_id, {})
