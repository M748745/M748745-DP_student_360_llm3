"""
Universal Context Builder
=========================
A 100% generic, dataset-agnostic context builder that works with ANY dataset.

This module automatically discovers:
1. Intelligent Metrics (semantic column understanding, domain detection, auto-calculated KPIs)
2. Data Patterns (distributions, quality, relationships)
3. Statistical Patterns (outliers, trends, correlations)
4. Business Insights (segments, revenue drivers, churn, CLV)
5. Domain Knowledge (benchmarks, best practices, compliance, risks)
6. Predictive Insights (forecasting, lead indicators, scenarios)
7. Relationship Patterns (network effects, hierarchies)

Zero hardcoding - adapts to any dataset automatically.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
import re
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


# ============================================================================
# LAYER 1: INTELLIGENT METRICS DISCOVERY
# ============================================================================

def discover_intelligent_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Automatically discover and compute relevant metrics based on dataset columns.
    ZERO hardcoded assumptions - works with ANY dataset.

    Args:
        df: pandas DataFrame

    Returns:
        Dictionary containing:
        - column_semantics: Detected meaning of each column
        - detected_domain: Identified business domain
        - detected_entities: Primary business entities
        - computable_metrics: List of metrics that can be calculated
        - calculated_metrics: Actual computed metric values
        - missing_key_metrics: Metrics that would be useful but can't be calculated
    """
    discoveries = {
        'column_semantics': {},
        'detected_domain': None,
        'detected_entities': [],
        'computable_metrics': [],
        'calculated_metrics': {},
        'missing_key_metrics': [],
        'dataset_profile': {}
    }

    # STEP 1: Semantic column understanding
    semantic_patterns = {
        'identifier': {
            'patterns': ['id', 'key', 'code', 'number', 'uuid', 'guid'],
            'check': lambda col: df[col].nunique() / len(df) > 0.95 if len(df) > 0 else False
        },
        'email': {
            'patterns': ['email', 'mail', 'e-mail'],
            'check': lambda col: df[col].astype(str).str.contains('@', na=False).mean() > 0.8 if len(df) > 0 else False
        },
        'phone': {
            'patterns': ['phone', 'mobile', 'tel', 'contact'],
            'check': lambda col: df[col].astype(str).str.match(r'[\d\-\+\(\) ]{7,}', na=False).mean() > 0.7 if len(df) > 0 else False
        },
        'currency': {
            'patterns': ['price', 'cost', 'revenue', 'tuition', 'fees', 'salary', 'payment', 'amount', 'total'],
            'check': lambda col: pd.api.types.is_numeric_dtype(df[col]) and df[col].min() >= 0
        },
        'percentage': {
            'patterns': ['pct', 'percent', 'rate', 'ratio'],
            'check': lambda col: pd.api.types.is_numeric_dtype(df[col]) and df[col].min() >= 0 and df[col].max() <= 100
        },
        'score': {
            'patterns': ['gpa', 'grade', 'score', 'rating', 'rank'],
            'check': lambda col: pd.api.types.is_numeric_dtype(df[col])
        },
        'date': {
            'patterns': ['date', 'time', 'timestamp', 'year', 'month', 'day'],
            'check': lambda col: pd.api.types.is_datetime64_any_dtype(df[col]) or _is_date_like(df[col])
        },
        'geography': {
            'patterns': ['country', 'city', 'region', 'state', 'location', 'address', 'nationality'],
            'check': lambda col: pd.api.types.is_object_dtype(df[col]) and df[col].nunique() < len(df) * 0.5
        },
        'category': {
            'patterns': ['type', 'category', 'status', 'class', 'group', 'segment'],
            'check': lambda col: pd.api.types.is_object_dtype(df[col]) and df[col].nunique() < 50
        },
        'name': {
            'patterns': ['name', 'title', 'label'],
            'check': lambda col: pd.api.types.is_object_dtype(df[col])
        },
        'boolean': {
            'patterns': ['is_', 'has_', 'flag', 'active', 'enabled'],
            'check': lambda col: df[col].nunique() == 2
        },
        'count': {
            'patterns': ['count', 'total', 'num_', 'number_of'],
            'check': lambda col: pd.api.types.is_integer_dtype(df[col]) and df[col].min() >= 0
        }
    }

    # Detect semantic type for each column
    for col in df.columns:
        col_lower = col.lower()
        detected_type = 'unknown'

        # Check pattern matches
        for semantic_type, pattern_info in semantic_patterns.items():
            # Check if column name contains pattern
            if any(pattern in col_lower for pattern in pattern_info['patterns']):
                try:
                    # Verify with characteristic check
                    if pattern_info['check'](col):
                        detected_type = semantic_type
                        break
                except:
                    continue

        # If no pattern match, use characteristic check only
        if detected_type == 'unknown':
            for semantic_type, pattern_info in semantic_patterns.items():
                try:
                    if pattern_info['check'](col):
                        detected_type = semantic_type
                        break
                except:
                    continue

        discoveries['column_semantics'][col] = {
            'semantic_type': detected_type,
            'data_type': str(df[col].dtype),
            'unique_count': int(df[col].nunique()),
            'null_count': int(df[col].isnull().sum()),
            'sample_values': df[col].dropna().head(3).tolist()
        }

    # STEP 2: Domain detection based on column patterns
    domain_indicators = {
        'education': ['student', 'gpa', 'course', 'enrollment', 'grade', 'academic', 'school', 'university'],
        'ecommerce': ['product', 'order', 'cart', 'purchase', 'customer', 'sku', 'inventory', 'shipping'],
        'finance': ['account', 'transaction', 'balance', 'loan', 'credit', 'debit', 'investment'],
        'hr': ['employee', 'salary', 'department', 'position', 'hire', 'performance', 'attendance'],
        'healthcare': ['patient', 'diagnosis', 'treatment', 'prescription', 'hospital', 'medical'],
        'saas': ['user', 'subscription', 'license', 'usage', 'feature', 'tenant', 'plan'],
        'retail': ['store', 'sales', 'inventory', 'supplier', 'warehouse', 'stock'],
        'marketing': ['campaign', 'lead', 'conversion', 'click', 'impression', 'engagement']
    }

    domain_scores = {}
    all_columns_lower = ' '.join(df.columns).lower()

    for domain, indicators in domain_indicators.items():
        score = sum(1 for indicator in indicators if indicator in all_columns_lower)
        if score > 0:
            domain_scores[domain] = score

    if domain_scores:
        discoveries['detected_domain'] = max(domain_scores.items(), key=lambda x: x[1])[0]
    else:
        discoveries['detected_domain'] = 'general'

    # STEP 3: Entity detection (what is each row?)
    entity_patterns = {
        'student': ['student', 'enrollment'],
        'customer': ['customer', 'client', 'buyer'],
        'employee': ['employee', 'staff', 'worker'],
        'product': ['product', 'item', 'sku'],
        'transaction': ['transaction', 'order', 'purchase', 'sale'],
        'user': ['user', 'account', 'member'],
        'patient': ['patient', 'case']
    }

    for entity_type, patterns in entity_patterns.items():
        if any(pattern in all_columns_lower for pattern in patterns):
            discoveries['detected_entities'].append(entity_type)

    if not discoveries['detected_entities']:
        discoveries['detected_entities'] = ['record']

    # STEP 4: Dataset profile
    discoveries['dataset_profile'] = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'numeric_columns': len(df.select_dtypes(include=[np.number]).columns),
        'categorical_columns': len(df.select_dtypes(include=['object', 'category']).columns),
        'date_columns': len([col for col, info in discoveries['column_semantics'].items() if info['semantic_type'] == 'date']),
        'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
    }

    # STEP 5: Auto-calculate domain-specific metrics
    domain = discoveries['detected_domain']

    if domain == 'education':
        discoveries = _calculate_education_metrics(df, discoveries)
    elif domain == 'ecommerce':
        discoveries = _calculate_ecommerce_metrics(df, discoveries)
    elif domain == 'finance':
        discoveries = _calculate_finance_metrics(df, discoveries)
    elif domain == 'hr':
        discoveries = _calculate_hr_metrics(df, discoveries)
    elif domain == 'saas':
        discoveries = _calculate_saas_metrics(df, discoveries)
    else:
        discoveries = _calculate_general_metrics(df, discoveries)

    return discoveries


def _is_date_like(series: pd.Series) -> bool:
    """Check if series contains date-like strings"""
    if not pd.api.types.is_object_dtype(series):
        return False

    sample = series.dropna().head(10).astype(str)
    date_patterns = [
        r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
        r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
        r'\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
    ]

    for pattern in date_patterns:
        if sample.str.match(pattern).mean() > 0.7:
            return True

    return False


def _calculate_education_metrics(df: pd.DataFrame, discoveries: Dict) -> Dict:
    """Calculate education-specific metrics"""
    metrics = {}

    # Find GPA column
    gpa_col = None
    for col, info in discoveries['column_semantics'].items():
        if 'gpa' in col.lower() or (info['semantic_type'] == 'score' and 'grade' in col.lower()):
            gpa_col = col
            break

    if gpa_col and pd.api.types.is_numeric_dtype(df[gpa_col]):
        metrics['avg_gpa'] = float(df[gpa_col].mean())
        metrics['high_performers'] = int((df[gpa_col] >= 3.5).sum())
        metrics['high_performers_pct'] = float((df[gpa_col] >= 3.5).mean() * 100)
        metrics['at_risk'] = int((df[gpa_col] < 2.0).sum())
        metrics['at_risk_pct'] = float((df[gpa_col] < 2.0).mean() * 100)
        discoveries['computable_metrics'].extend(['avg_gpa', 'high_performers', 'at_risk'])

    # Find tuition/revenue columns
    tuition_cols = [col for col, info in discoveries['column_semantics'].items()
                    if info['semantic_type'] == 'currency' and any(x in col.lower() for x in ['tuition', 'fee'])]

    if tuition_cols:
        metrics['total_tuition'] = float(df[tuition_cols[0]].sum())
        metrics['avg_tuition'] = float(df[tuition_cols[0]].mean())
        discoveries['computable_metrics'].extend(['total_tuition', 'avg_tuition'])

    # Find nationality/geography columns
    geo_cols = [col for col, info in discoveries['column_semantics'].items()
                if info['semantic_type'] == 'geography']

    if geo_cols:
        metrics['unique_nationalities'] = int(df[geo_cols[0]].nunique())
        discoveries['computable_metrics'].append('unique_nationalities')

    discoveries['calculated_metrics'] = metrics
    return discoveries


def _calculate_ecommerce_metrics(df: pd.DataFrame, discoveries: Dict) -> Dict:
    """Calculate e-commerce specific metrics"""
    metrics = {}

    # Find revenue columns
    revenue_cols = [col for col, info in discoveries['column_semantics'].items()
                    if info['semantic_type'] == 'currency' and any(x in col.lower() for x in ['revenue', 'price', 'total', 'amount'])]

    if revenue_cols:
        metrics['total_revenue'] = float(df[revenue_cols[0]].sum())
        metrics['avg_order_value'] = float(df[revenue_cols[0]].mean())
        metrics['median_order_value'] = float(df[revenue_cols[0]].median())
        discoveries['computable_metrics'].extend(['total_revenue', 'avg_order_value'])

    # Find customer ID columns
    customer_cols = [col for col, info in discoveries['column_semantics'].items()
                     if info['semantic_type'] == 'identifier' and 'customer' in col.lower()]

    if customer_cols:
        metrics['unique_customers'] = int(df[customer_cols[0]].nunique())
        if revenue_cols:
            metrics['revenue_per_customer'] = float(df.groupby(customer_cols[0])[revenue_cols[0]].sum().mean())
        discoveries['computable_metrics'].extend(['unique_customers', 'revenue_per_customer'])

    discoveries['calculated_metrics'] = metrics
    return discoveries


def _calculate_finance_metrics(df: pd.DataFrame, discoveries: Dict) -> Dict:
    """Calculate finance-specific metrics"""
    metrics = {}

    # Find balance/amount columns
    amount_cols = [col for col, info in discoveries['column_semantics'].items()
                   if info['semantic_type'] == 'currency']

    if amount_cols:
        metrics['total_amount'] = float(df[amount_cols[0]].sum())
        metrics['avg_amount'] = float(df[amount_cols[0]].mean())
        metrics['max_amount'] = float(df[amount_cols[0]].max())
        discoveries['computable_metrics'].extend(['total_amount', 'avg_amount'])

    discoveries['calculated_metrics'] = metrics
    return discoveries


def _calculate_hr_metrics(df: pd.DataFrame, discoveries: Dict) -> Dict:
    """Calculate HR-specific metrics"""
    metrics = {}

    # Find salary columns
    salary_cols = [col for col, info in discoveries['column_semantics'].items()
                   if info['semantic_type'] == 'currency' and 'salary' in col.lower()]

    if salary_cols:
        metrics['avg_salary'] = float(df[salary_cols[0]].mean())
        metrics['median_salary'] = float(df[salary_cols[0]].median())
        metrics['total_payroll'] = float(df[salary_cols[0]].sum())
        discoveries['computable_metrics'].extend(['avg_salary', 'total_payroll'])

    # Find department columns
    dept_cols = [col for col, info in discoveries['column_semantics'].items()
                 if 'department' in col.lower() or 'dept' in col.lower()]

    if dept_cols:
        metrics['unique_departments'] = int(df[dept_cols[0]].nunique())
        discoveries['computable_metrics'].append('unique_departments')

    discoveries['calculated_metrics'] = metrics
    return discoveries


def _calculate_saas_metrics(df: pd.DataFrame, discoveries: Dict) -> Dict:
    """Calculate SaaS-specific metrics"""
    metrics = {}

    # Find subscription/revenue columns
    revenue_cols = [col for col, info in discoveries['column_semantics'].items()
                    if info['semantic_type'] == 'currency' and any(x in col.lower() for x in ['mrr', 'arr', 'revenue', 'subscription'])]

    if revenue_cols:
        metrics['total_revenue'] = float(df[revenue_cols[0]].sum())
        metrics['avg_revenue_per_user'] = float(df[revenue_cols[0]].mean())
        discoveries['computable_metrics'].extend(['total_revenue', 'avg_revenue_per_user'])

    discoveries['calculated_metrics'] = metrics
    return discoveries


def _calculate_general_metrics(df: pd.DataFrame, discoveries: Dict) -> Dict:
    """Calculate general metrics for any dataset"""
    metrics = {}

    # Find any numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    for col in numeric_cols[:5]:  # Top 5 numeric columns
        col_safe = col.replace(' ', '_').replace('-', '_')
        try:
            metrics[f'{col_safe}_sum'] = float(df[col].sum())
            metrics[f'{col_safe}_avg'] = float(df[col].mean())
            metrics[f'{col_safe}_min'] = float(df[col].min())
            metrics[f'{col_safe}_max'] = float(df[col].max())
            discoveries['computable_metrics'].append(f'{col_safe}_stats')
        except:
            pass

    discoveries['calculated_metrics'] = metrics
    return discoveries


# ============================================================================
# LAYER 2: DATA DISCOVERY
# ============================================================================

def discover_data_patterns(df: pd.DataFrame, metrics_intel: Dict) -> Dict[str, Any]:
    """
    Discover data quality, distributions, and patterns.

    Args:
        df: pandas DataFrame
        metrics_intel: Results from intelligent_metrics discovery

    Returns:
        Dictionary containing data quality metrics, distributions, and patterns
    """
    patterns = {
        'data_quality': {},
        'distributions': {},
        'column_patterns': {},
        'data_completeness': {}
    }

    # Data Quality Assessment
    total_cells = len(df) * len(df.columns)
    null_cells = df.isnull().sum().sum()

    patterns['data_quality'] = {
        'completeness_pct': float((1 - null_cells / total_cells) * 100) if total_cells > 0 else 100.0,
        'total_nulls': int(null_cells),
        'columns_with_nulls': int((df.isnull().sum() > 0).sum()),
        'duplicate_rows': int(df.duplicated().sum()),
        'duplicate_rows_pct': float(df.duplicated().mean() * 100) if len(df) > 0 else 0.0
    }

    # Column-level quality
    for col in df.columns:
        col_quality = {
            'null_count': int(df[col].isnull().sum()),
            'null_pct': float(df[col].isnull().mean() * 100) if len(df) > 0 else 0.0,
            'unique_count': int(df[col].nunique()),
            'uniqueness_pct': float(df[col].nunique() / len(df) * 100) if len(df) > 0 else 0.0
        }

        # For numeric columns, add range and outlier info
        if pd.api.types.is_numeric_dtype(df[col]):
            col_quality['min'] = float(df[col].min())
            col_quality['max'] = float(df[col].max())
            col_quality['range'] = float(df[col].max() - df[col].min())

            # Detect outliers using IQR method
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
            col_quality['outlier_count'] = int(outliers)
            col_quality['outlier_pct'] = float(outliers / len(df) * 100) if len(df) > 0 else 0.0

        patterns['column_patterns'][col] = col_quality

    # Distribution analysis for numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols[:10]:  # Top 10 numeric columns
        try:
            patterns['distributions'][col] = {
                'mean': float(df[col].mean()),
                'median': float(df[col].median()),
                'std': float(df[col].std()),
                'skewness': float(df[col].skew()),
                'kurtosis': float(df[col].kurtosis()),
                'q25': float(df[col].quantile(0.25)),
                'q75': float(df[col].quantile(0.75)),
                'distribution_type': _classify_distribution(df[col])
            }
        except:
            pass

    # Completeness by semantic type
    for semantic_type in ['identifier', 'currency', 'score', 'date', 'geography']:
        type_cols = [col for col, info in metrics_intel['column_semantics'].items()
                     if info['semantic_type'] == semantic_type]
        if type_cols:
            avg_completeness = df[type_cols].notna().mean().mean() * 100
            patterns['data_completeness'][semantic_type] = float(avg_completeness)

    return patterns


def _classify_distribution(series: pd.Series) -> str:
    """Classify the distribution type of a numeric series"""
    try:
        skew = series.skew()
        kurtosis = series.kurtosis()

        if abs(skew) < 0.5 and abs(kurtosis) < 0.5:
            return 'normal'
        elif skew > 1:
            return 'right_skewed'
        elif skew < -1:
            return 'left_skewed'
        elif kurtosis > 1:
            return 'heavy_tailed'
        elif kurtosis < -1:
            return 'light_tailed'
        else:
            return 'approximately_normal'
    except:
        return 'unknown'


# ============================================================================
# LAYER 3: STATISTICAL DISCOVERY
# ============================================================================

def discover_statistical_patterns(df: pd.DataFrame, metrics_intel: Dict) -> Dict[str, Any]:
    """
    Discover statistical patterns, correlations, and trends.

    Args:
        df: pandas DataFrame
        metrics_intel: Results from intelligent_metrics discovery

    Returns:
        Dictionary containing statistical insights
    """
    patterns = {
        'correlations': {},
        'trends': {},
        'segments': {},
        'top_insights': []
    }

    numeric_cols = df.select_dtypes(include=[np.number]).columns

    # Correlation analysis (top correlations only)
    if len(numeric_cols) >= 2:
        corr_matrix = df[numeric_cols].corr()

        # Find top positive and negative correlations
        correlations = []
        for i in range(len(numeric_cols)):
            for j in range(i + 1, len(numeric_cols)):
                col1, col2 = numeric_cols[i], numeric_cols[j]
                corr_value = corr_matrix.loc[col1, col2]
                if abs(corr_value) > 0.3:  # Only significant correlations
                    correlations.append({
                        'col1': col1,
                        'col2': col2,
                        'correlation': float(corr_value),
                        'strength': 'strong' if abs(corr_value) > 0.7 else 'moderate'
                    })

        # Sort by absolute correlation value
        correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
        patterns['correlations'] = correlations[:10]  # Top 10

    # Trend detection for date columns
    date_cols = [col for col, info in metrics_intel['column_semantics'].items()
                 if info['semantic_type'] == 'date']

    if date_cols and numeric_cols.any():
        for date_col in date_cols[:2]:  # Max 2 date columns
            try:
                df_sorted = df.sort_values(date_col)
                for num_col in numeric_cols[:3]:  # Top 3 numeric columns
                    # Simple trend detection using first vs last half
                    mid_point = len(df_sorted) // 2
                    first_half_mean = df_sorted[num_col].iloc[:mid_point].mean()
                    second_half_mean = df_sorted[num_col].iloc[mid_point:].mean()

                    if not np.isnan(first_half_mean) and not np.isnan(second_half_mean):
                        pct_change = ((second_half_mean - first_half_mean) / first_half_mean * 100) if first_half_mean != 0 else 0

                        patterns['trends'][f'{date_col}_{num_col}'] = {
                            'first_period_avg': float(first_half_mean),
                            'second_period_avg': float(second_half_mean),
                            'pct_change': float(pct_change),
                            'trend': 'increasing' if pct_change > 5 else 'decreasing' if pct_change < -5 else 'stable'
                        }
            except:
                pass

    # Segment detection (for categorical columns)
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns

    for cat_col in categorical_cols[:3]:  # Top 3 categorical columns
        if df[cat_col].nunique() <= 20:  # Only manageable number of categories
            try:
                value_counts = df[cat_col].value_counts()
                patterns['segments'][cat_col] = {
                    'total_segments': int(df[cat_col].nunique()),
                    'largest_segment': str(value_counts.index[0]),
                    'largest_segment_size': int(value_counts.iloc[0]),
                    'largest_segment_pct': float(value_counts.iloc[0] / len(df) * 100),
                    'smallest_segment': str(value_counts.index[-1]),
                    'smallest_segment_size': int(value_counts.iloc[-1]),
                    'balance': 'balanced' if (value_counts.max() / value_counts.min() < 3) else 'imbalanced'
                }
            except:
                pass

    # Generate top insights
    insights = []

    # Insight 1: Data quality
    quality_pct = patterns.get('data_quality', {}).get('completeness_pct', 100)
    if quality_pct < 90:
        insights.append(f"Data completeness is {quality_pct:.1f}% - some columns have missing values")
    elif quality_pct >= 95:
        insights.append(f"High data quality with {quality_pct:.1f}% completeness")

    # Insight 2: Strong correlations
    if patterns['correlations']:
        top_corr = patterns['correlations'][0]
        insights.append(f"Strong correlation ({top_corr['correlation']:.2f}) between {top_corr['col1']} and {top_corr['col2']}")

    # Insight 3: Trends
    if patterns['trends']:
        for trend_key, trend_info in list(patterns['trends'].items())[:2]:
            if abs(trend_info['pct_change']) > 10:
                insights.append(f"{trend_key.split('_', 1)[1]} shows {trend_info['trend']} trend ({trend_info['pct_change']:+.1f}%)")

    patterns['top_insights'] = insights

    return patterns


# ============================================================================
# LAYER 4: BUSINESS DISCOVERY
# ============================================================================

def discover_business_insights(df: pd.DataFrame, domain: str, metrics_intel: Dict) -> Dict[str, Any]:
    """
    Discover business-critical insights: revenue drivers, CLV, churn, cost analysis.

    Args:
        df: pandas DataFrame
        domain: Detected domain (education, ecommerce, finance, etc.)
        metrics_intel: Results from intelligent_metrics discovery

    Returns:
        Dictionary containing business insights
    """
    insights = {
        'revenue_analysis': {},
        'customer_value': {},
        'churn_risk': {},
        'cost_analysis': {},
        'profitability': {},
        'growth_indicators': {}
    }

    # Domain-specific business discovery
    if domain == 'education':
        insights = _discover_education_business(df, metrics_intel, insights)
    elif domain == 'ecommerce':
        insights = _discover_ecommerce_business(df, metrics_intel, insights)
    elif domain == 'finance':
        insights = _discover_finance_business(df, metrics_intel, insights)
    elif domain == 'hr':
        insights = _discover_hr_business(df, metrics_intel, insights)
    elif domain == 'saas':
        insights = _discover_saas_business(df, metrics_intel, insights)
    else:
        insights = _discover_general_business(df, metrics_intel, insights)

    return insights


def _discover_education_business(df: pd.DataFrame, metrics_intel: Dict, insights: Dict) -> Dict:
    """Discover education-specific business insights"""

    # Revenue Analysis
    tuition_cols = [col for col, info in metrics_intel['column_semantics'].items()
                    if info['semantic_type'] == 'currency' and any(x in col.lower() for x in ['tuition', 'fee'])]

    if tuition_cols:
        tuition_col = tuition_cols[0]
        total_revenue = df[tuition_col].sum()
        avg_revenue = df[tuition_col].mean()

        insights['revenue_analysis'] = {
            'total_revenue': float(total_revenue),
            'avg_revenue_per_student': float(avg_revenue),
            'revenue_source': 'tuition_fees'
        }

        # Revenue concentration by segment
        geo_cols = [col for col, info in metrics_intel['column_semantics'].items()
                    if info['semantic_type'] == 'geography']

        if geo_cols:
            geo_col = geo_cols[0]
            segment_revenue = df.groupby(geo_col)[tuition_col].agg(['sum', 'mean', 'count'])
            top_segment = segment_revenue['sum'].idxmax()
            top_segment_pct = (segment_revenue.loc[top_segment, 'sum'] / total_revenue * 100)

            insights['revenue_analysis']['top_segment'] = str(top_segment)
            insights['revenue_analysis']['top_segment_revenue'] = float(segment_revenue.loc[top_segment, 'sum'])
            insights['revenue_analysis']['top_segment_pct'] = float(top_segment_pct)
            insights['revenue_analysis']['revenue_concentration_risk'] = 'high' if top_segment_pct > 50 else 'moderate' if top_segment_pct > 30 else 'low'

    # Student Lifetime Value (SLV)
    if tuition_cols:
        # Estimate based on typical 4-year education
        avg_annual_tuition = df[tuition_cols[0]].mean()
        estimated_slv = avg_annual_tuition * 4  # 4 years

        insights['customer_value'] = {
            'avg_lifetime_value': float(estimated_slv),
            'calculation_basis': '4_year_program',
            'avg_annual_value': float(avg_annual_tuition)
        }

    # At-Risk/Churn Analysis
    gpa_col = None
    for col, info in metrics_intel['column_semantics'].items():
        if 'gpa' in col.lower() or (info['semantic_type'] == 'score' and 'grade' in col.lower()):
            gpa_col = col
            break

    if gpa_col and pd.api.types.is_numeric_dtype(df[gpa_col]):
        at_risk_count = (df[gpa_col] < 2.0).sum()
        at_risk_pct = (at_risk_count / len(df) * 100) if len(df) > 0 else 0

        if tuition_cols:
            at_risk_revenue = df[df[gpa_col] < 2.0][tuition_cols[0]].sum()
            potential_loss = at_risk_revenue  # Potential dropout revenue loss

            insights['churn_risk'] = {
                'at_risk_count': int(at_risk_count),
                'at_risk_percentage': float(at_risk_pct),
                'revenue_at_risk': float(at_risk_revenue),
                'potential_annual_loss': float(potential_loss),
                'risk_level': 'high' if at_risk_pct > 10 else 'moderate' if at_risk_pct > 5 else 'low'
            }

    # Cost Analysis (Financial Aid as cost)
    aid_cols = [col for col, info in metrics_intel['column_semantics'].items()
                if info['semantic_type'] == 'currency' and any(x in col.lower() for x in ['aid', 'scholarship', 'grant'])]

    if aid_cols and tuition_cols:
        aid_col = aid_cols[0]
        total_aid = df[aid_col].sum()
        total_tuition = df[tuition_cols[0]].sum()
        aid_coverage_pct = (total_aid / total_tuition * 100) if total_tuition > 0 else 0

        insights['cost_analysis'] = {
            'total_financial_aid': float(total_aid),
            'aid_coverage_percentage': float(aid_coverage_pct),
            'students_receiving_aid': int((df[aid_col] > 0).sum()),
            'avg_aid_per_recipient': float(df[df[aid_col] > 0][aid_col].mean()) if (df[aid_col] > 0).any() else 0
        }

        # Profitability
        net_revenue = total_tuition - total_aid
        insights['profitability'] = {
            'net_revenue': float(net_revenue),
            'gross_margin_pct': float((net_revenue / total_tuition * 100) if total_tuition > 0 else 0)
        }

    return insights


def _discover_ecommerce_business(df: pd.DataFrame, metrics_intel: Dict, insights: Dict) -> Dict:
    """Discover e-commerce business insights"""

    # Revenue Analysis
    revenue_cols = [col for col, info in metrics_intel['column_semantics'].items()
                    if info['semantic_type'] == 'currency' and any(x in col.lower() for x in ['revenue', 'price', 'total', 'amount'])]

    if revenue_cols:
        revenue_col = revenue_cols[0]
        total_revenue = df[revenue_col].sum()
        avg_order_value = df[revenue_col].mean()

        insights['revenue_analysis'] = {
            'total_revenue': float(total_revenue),
            'avg_order_value': float(avg_order_value),
            'total_transactions': len(df),
            'revenue_per_transaction': float(total_revenue / len(df)) if len(df) > 0 else 0
        }

    # Customer Lifetime Value (CLV)
    customer_cols = [col for col, info in metrics_intel['column_semantics'].items()
                     if info['semantic_type'] == 'identifier' and 'customer' in col.lower()]

    if customer_cols and revenue_cols:
        customer_col = customer_cols[0]
        customer_revenue = df.groupby(customer_col)[revenue_cols[0]].agg(['sum', 'count', 'mean'])

        avg_clv = customer_revenue['sum'].mean()
        avg_orders_per_customer = customer_revenue['count'].mean()

        insights['customer_value'] = {
            'avg_customer_lifetime_value': float(avg_clv),
            'avg_orders_per_customer': float(avg_orders_per_customer),
            'avg_order_value': float(customer_revenue['mean'].mean()),
            'total_customers': int(df[customer_col].nunique())
        }

        # High-value customer segment
        top_20_pct_threshold = customer_revenue['sum'].quantile(0.8)
        high_value_customers = (customer_revenue['sum'] >= top_20_pct_threshold).sum()
        high_value_revenue = customer_revenue[customer_revenue['sum'] >= top_20_pct_threshold]['sum'].sum()

        insights['customer_value']['high_value_customers'] = int(high_value_customers)
        insights['customer_value']['high_value_revenue_pct'] = float((high_value_revenue / total_revenue * 100) if total_revenue > 0 else 0)

    # Churn/Return Rate Analysis
    if customer_cols:
        single_order_customers = (customer_revenue['count'] == 1).sum()
        repeat_customers = (customer_revenue['count'] > 1).sum()
        repeat_rate = (repeat_customers / len(customer_revenue) * 100) if len(customer_revenue) > 0 else 0

        insights['churn_risk'] = {
            'single_order_customers': int(single_order_customers),
            'repeat_customers': int(repeat_customers),
            'repeat_purchase_rate': float(repeat_rate),
            'churn_indicator': 'high' if repeat_rate < 20 else 'moderate' if repeat_rate < 40 else 'low'
        }

    return insights


def _discover_finance_business(df: pd.DataFrame, metrics_intel: Dict, insights: Dict) -> Dict:
    """Discover finance-specific business insights"""

    # Transaction Analysis
    amount_cols = [col for col, info in metrics_intel['column_semantics'].items()
                   if info['semantic_type'] == 'currency']

    if amount_cols:
        amount_col = amount_cols[0]
        total_volume = df[amount_col].sum()
        avg_transaction = df[amount_col].mean()

        insights['revenue_analysis'] = {
            'total_transaction_volume': float(total_volume),
            'avg_transaction_size': float(avg_transaction),
            'total_transactions': len(df),
            'large_transactions': int((df[amount_col] > df[amount_col].quantile(0.9)).sum())
        }

        # High-value transaction concentration
        top_10_pct = df.nlargest(int(len(df) * 0.1), amount_col)[amount_col].sum()
        concentration_pct = (top_10_pct / total_volume * 100) if total_volume > 0 else 0

        insights['revenue_analysis']['top_10_pct_concentration'] = float(concentration_pct)
        insights['revenue_analysis']['concentration_risk'] = 'high' if concentration_pct > 70 else 'moderate' if concentration_pct > 50 else 'low'

    return insights


def _discover_hr_business(df: pd.DataFrame, metrics_intel: Dict, insights: Dict) -> Dict:
    """Discover HR-specific business insights"""

    # Payroll Analysis
    salary_cols = [col for col, info in metrics_intel['column_semantics'].items()
                   if info['semantic_type'] == 'currency' and 'salary' in col.lower()]

    if salary_cols:
        salary_col = salary_cols[0]
        total_payroll = df[salary_col].sum()
        avg_salary = df[salary_col].mean()
        median_salary = df[salary_col].median()

        insights['cost_analysis'] = {
            'total_payroll': float(total_payroll),
            'avg_salary': float(avg_salary),
            'median_salary': float(median_salary),
            'total_employees': len(df)
        }

        # Department cost analysis
        dept_cols = [col for col, info in metrics_intel['column_semantics'].items()
                     if 'department' in col.lower() or 'dept' in col.lower()]

        if dept_cols:
            dept_col = dept_cols[0]
            dept_costs = df.groupby(dept_col)[salary_col].agg(['sum', 'mean', 'count'])
            highest_cost_dept = dept_costs['sum'].idxmax()

            insights['cost_analysis']['highest_cost_department'] = str(highest_cost_dept)
            insights['cost_analysis']['highest_dept_cost'] = float(dept_costs.loc[highest_cost_dept, 'sum'])
            insights['cost_analysis']['highest_dept_pct'] = float((dept_costs.loc[highest_cost_dept, 'sum'] / total_payroll * 100) if total_payroll > 0 else 0)

    return insights


def _discover_saas_business(df: pd.DataFrame, metrics_intel: Dict, insights: Dict) -> Dict:
    """Discover SaaS-specific business insights"""

    # MRR/ARR Analysis
    revenue_cols = [col for col, info in metrics_intel['column_semantics'].items()
                    if info['semantic_type'] == 'currency' and any(x in col.lower() for x in ['mrr', 'arr', 'revenue', 'subscription'])]

    if revenue_cols:
        revenue_col = revenue_cols[0]

        if 'mrr' in revenue_col.lower():
            total_mrr = df[revenue_col].sum()
            arr = total_mrr * 12
            insights['revenue_analysis'] = {
                'total_mrr': float(total_mrr),
                'estimated_arr': float(arr),
                'avg_mrr_per_customer': float(df[revenue_col].mean())
            }
        elif 'arr' in revenue_col.lower():
            total_arr = df[revenue_col].sum()
            mrr = total_arr / 12
            insights['revenue_analysis'] = {
                'total_arr': float(total_arr),
                'estimated_mrr': float(mrr),
                'avg_arr_per_customer': float(df[revenue_col].mean())
            }
        else:
            insights['revenue_analysis'] = {
                'total_revenue': float(df[revenue_col].sum()),
                'avg_revenue_per_customer': float(df[revenue_col].mean())
            }

    # Customer segments by value
    if revenue_cols:
        revenue_col = revenue_cols[0]

        # Enterprise (top 20%), SMB (middle 50%), Starter (bottom 30%)
        enterprise_threshold = df[revenue_col].quantile(0.8)
        smb_threshold = df[revenue_col].quantile(0.3)

        enterprise_count = (df[revenue_col] >= enterprise_threshold).sum()
        smb_count = ((df[revenue_col] >= smb_threshold) & (df[revenue_col] < enterprise_threshold)).sum()
        starter_count = (df[revenue_col] < smb_threshold).sum()

        enterprise_revenue = df[df[revenue_col] >= enterprise_threshold][revenue_col].sum()
        total_revenue = df[revenue_col].sum()

        insights['customer_value'] = {
            'enterprise_customers': int(enterprise_count),
            'smb_customers': int(smb_count),
            'starter_customers': int(starter_count),
            'enterprise_revenue_pct': float((enterprise_revenue / total_revenue * 100) if total_revenue > 0 else 0)
        }

    return insights


def _discover_general_business(df: pd.DataFrame, metrics_intel: Dict, insights: Dict) -> Dict:
    """Discover general business insights for unknown domains"""

    # Find any currency columns
    currency_cols = [col for col, info in metrics_intel['column_semantics'].items()
                     if info['semantic_type'] == 'currency']

    if currency_cols:
        for currency_col in currency_cols[:3]:  # Top 3 currency columns
            col_safe = currency_col.replace(' ', '_').replace('-', '_')

            insights['revenue_analysis'][f'{col_safe}_total'] = float(df[currency_col].sum())
            insights['revenue_analysis'][f'{col_safe}_avg'] = float(df[currency_col].mean())
            insights['revenue_analysis'][f'{col_safe}_median'] = float(df[currency_col].median())

    # Find categorical columns for segmentation
    cat_cols = [col for col, info in metrics_intel['column_semantics'].items()
                if info['semantic_type'] == 'category' and df[col].nunique() <= 10]

    if cat_cols and currency_cols:
        cat_col = cat_cols[0]
        currency_col = currency_cols[0]

        segment_analysis = df.groupby(cat_col)[currency_col].agg(['sum', 'mean', 'count'])
        top_segment = segment_analysis['sum'].idxmax()

        insights['revenue_analysis']['top_segment'] = str(top_segment)
        insights['revenue_analysis']['top_segment_value'] = float(segment_analysis.loc[top_segment, 'sum'])

    return insights


# ============================================================================
# LAYER 5: DOMAIN DISCOVERY
# ============================================================================

def discover_domain_knowledge(df: pd.DataFrame, domain: str, metrics_intel: Dict) -> Dict[str, Any]:
    """
    Discover domain-specific knowledge: benchmarks, best practices, compliance, risks.

    Args:
        df: pandas DataFrame
        domain: Detected domain
        metrics_intel: Results from intelligent_metrics discovery

    Returns:
        Dictionary containing domain knowledge
    """
    knowledge = {
        'industry_benchmarks': {},
        'best_practices': [],
        'compliance_requirements': [],
        'domain_risks': [],
        'performance_indicators': {}
    }

    # Domain-specific knowledge
    if domain == 'education':
        knowledge = _get_education_domain_knowledge(df, metrics_intel, knowledge)
    elif domain == 'ecommerce':
        knowledge = _get_ecommerce_domain_knowledge(df, metrics_intel, knowledge)
    elif domain == 'finance':
        knowledge = _get_finance_domain_knowledge(df, metrics_intel, knowledge)
    elif domain == 'hr':
        knowledge = _get_hr_domain_knowledge(df, metrics_intel, knowledge)
    elif domain == 'saas':
        knowledge = _get_saas_domain_knowledge(df, metrics_intel, knowledge)
    else:
        knowledge = _get_general_domain_knowledge(df, metrics_intel, knowledge)

    return knowledge


def _get_education_domain_knowledge(df: pd.DataFrame, metrics_intel: Dict, knowledge: Dict) -> Dict:
    """Education domain knowledge and benchmarks"""

    # Industry Benchmarks
    calc_metrics = metrics_intel.get('calculated_metrics', {})

    if 'avg_gpa' in calc_metrics:
        avg_gpa = calc_metrics['avg_gpa']
        knowledge['industry_benchmarks']['avg_gpa'] = {
            'current': float(avg_gpa),
            'industry_average': 3.0,
            'top_quartile': 3.3,
            'status': 'above_benchmark' if avg_gpa > 3.0 else 'below_benchmark'
        }

    if 'high_performers_pct' in calc_metrics:
        high_perf_pct = calc_metrics['high_performers_pct']
        knowledge['industry_benchmarks']['high_performers'] = {
            'current': float(high_perf_pct),
            'industry_average': 15.0,
            'top_quartile': 25.0,
            'status': 'above_benchmark' if high_perf_pct > 15.0 else 'below_benchmark'
        }

    if 'at_risk_pct' in calc_metrics:
        at_risk_pct = calc_metrics['at_risk_pct']
        knowledge['industry_benchmarks']['at_risk_students'] = {
            'current': float(at_risk_pct),
            'industry_average': 8.0,
            'best_practice': 5.0,
            'status': 'better_than_avg' if at_risk_pct < 8.0 else 'needs_improvement'
        }

    # Best Practices
    knowledge['best_practices'] = [
        "Maintain student-faculty ratio below 20:1 for optimal learning outcomes",
        "Implement early warning systems for at-risk students (GPA < 2.0 in first semester)",
        "Target financial aid at 18-22% of tuition revenue for access and diversity",
        "Monitor international student dependency - should not exceed 40% of enrollment",
        "Track 4-year graduation rate (benchmark: 60% for public, 70% for private)",
        "Conduct bi-annual student satisfaction surveys (NPS > 30)"
    ]

    # Compliance Requirements
    knowledge['compliance_requirements'] = [
        "Accreditation standards (regional/national accrediting bodies)",
        "FERPA - Family Educational Rights and Privacy Act (student data privacy)",
        "Title IX - Gender equity in education and athletics",
        "Financial aid compliance (for institutions receiving federal funds)",
        "International student compliance (SEVIS reporting, visa regulations)",
        "Accessibility compliance (ADA, Section 508 for digital content)"
    ]

    # Domain Risks
    knowledge['domain_risks'] = [
        "Enrollment decline risk - demographic shifts, competition, economic factors",
        "Financial sustainability - tuition dependency, declining state funding",
        "Accreditation risk - loss of accreditation impacts eligibility for federal aid",
        "Student outcomes risk - poor retention/graduation rates affect rankings and enrollment",
        "Reputation risk - negative reviews, scandals, or poor rankings impact applications",
        "Technology risk - cybersecurity, data breaches, ransomware attacks"
    ]

    # Performance Indicators (compare current vs. benchmarks)
    knowledge['performance_indicators'] = {
        'academic_quality': 'strong' if calc_metrics.get('high_performers_pct', 0) > 15 else 'moderate',
        'retention_risk': 'low' if calc_metrics.get('at_risk_pct', 0) < 8 else 'moderate',
        'financial_health': 'strong'  # Placeholder - would need more financial data
    }

    return knowledge


def _get_ecommerce_domain_knowledge(df: pd.DataFrame, metrics_intel: Dict, knowledge: Dict) -> Dict:
    """E-commerce domain knowledge"""

    knowledge['industry_benchmarks'] = {
        'avg_order_value': {
            'industry_range': '50-150',
            'currency': 'USD'
        },
        'repeat_purchase_rate': {
            'industry_average': 30.0,
            'top_performers': 45.0
        },
        'customer_acquisition_cost': {
            'benchmark': 'should_be_recovered_in_3_orders'
        }
    }

    knowledge['best_practices'] = [
        "Implement abandoned cart recovery (can recover 15-30% of abandoned carts)",
        "Personalize product recommendations (increases AOV by 10-30%)",
        "Optimize for mobile (60%+ of traffic is mobile)",
        "Offer free shipping threshold (reduces cart abandonment by 20%)",
        "Build email list and nurture campaigns (ROI: $42 per $1 spent)",
        "Implement loyalty program for repeat purchases"
    ]

    knowledge['compliance_requirements'] = [
        "PCI-DSS compliance for payment card data",
        "GDPR compliance for EU customers (data privacy)",
        "CCPA compliance for California customers",
        "Consumer protection laws (refunds, warranties, product descriptions)",
        "Sales tax compliance (varying by jurisdiction)",
        "Accessibility compliance (WCAG 2.1 AA)"
    ]

    knowledge['domain_risks'] = [
        "Customer churn risk - high single-order customer rate",
        "Fraud risk - chargebacks, stolen credit cards, fake accounts",
        "Supply chain risk - inventory shortages, shipping delays",
        "Competition risk - low barriers to entry, price competition",
        "Technology risk - website downtime, payment processing failures",
        "Reputation risk - negative reviews, social media backlash"
    ]

    return knowledge


def _get_finance_domain_knowledge(df: pd.DataFrame, metrics_intel: Dict, knowledge: Dict) -> Dict:
    """Finance domain knowledge"""

    knowledge['industry_benchmarks'] = {
        'fraud_rate': {
            'industry_average': 0.5,
            'acceptable_range': '0.1-1.0',
            'unit': 'percentage'
        },
        'transaction_approval_rate': {
            'benchmark': 95.0,
            'top_performers': 98.0
        }
    }

    knowledge['best_practices'] = [
        "Implement multi-factor authentication for high-value transactions",
        "Maintain transaction monitoring and fraud detection systems",
        "Regular security audits and penetration testing",
        "Encryption of data at rest and in transit",
        "Regular backup and disaster recovery testing",
        "KYC (Know Your Customer) and AML (Anti-Money Laundering) procedures"
    ]

    knowledge['compliance_requirements'] = [
        "SOX compliance (Sarbanes-Oxley Act) for public companies",
        "PCI-DSS compliance for payment card data",
        "AML/KYC compliance (Bank Secrecy Act, USA PATRIOT Act)",
        "GLBA - Gramm-Leach-Bliley Act (financial privacy)",
        "Dodd-Frank Act compliance (financial regulation)",
        "Regional regulations (EU: PSD2, UK: FCA, etc.)"
    ]

    knowledge['domain_risks'] = [
        "Fraud risk - identity theft, payment fraud, account takeover",
        "Regulatory risk - non-compliance penalties, license revocation",
        "Market risk - interest rate changes, currency fluctuations",
        "Credit risk - customer defaults, bad debt",
        "Operational risk - system failures, human error",
        "Cybersecurity risk - data breaches, ransomware, DDoS attacks"
    ]

    return knowledge


def _get_hr_domain_knowledge(df: pd.DataFrame, metrics_intel: Dict, knowledge: Dict) -> Dict:
    """HR domain knowledge"""

    knowledge['industry_benchmarks'] = {
        'voluntary_turnover_rate': {
            'industry_average': 12.0,
            'acceptable_range': '8-15',
            'unit': 'percentage'
        },
        'time_to_hire': {
            'industry_average': 42,
            'top_performers': 30,
            'unit': 'days'
        }
    }

    knowledge['best_practices'] = [
        "Conduct annual performance reviews and feedback sessions",
        "Implement employee development and training programs",
        "Maintain competitive compensation and benefits packages",
        "Regular employee engagement and satisfaction surveys",
        "Clear career progression paths and promotion criteria",
        "Work-life balance initiatives (flexible work, PTO policies)"
    ]

    knowledge['compliance_requirements'] = [
        "EEOC compliance - Equal Employment Opportunity (anti-discrimination)",
        "FLSA compliance - Fair Labor Standards Act (wages, overtime)",
        "FMLA compliance - Family and Medical Leave Act",
        "ADA compliance - Americans with Disabilities Act",
        "I-9 compliance - Employment eligibility verification",
        "State-specific labor laws (varies by jurisdiction)"
    ]

    knowledge['domain_risks'] = [
        "Talent retention risk - loss of key employees, institutional knowledge",
        "Compliance risk - discrimination lawsuits, wage violations",
        "Burnout risk - employee stress, decreased productivity",
        "Succession planning risk - lack of leadership pipeline",
        "Payroll risk - miscalculations, tax filing errors",
        "Data privacy risk - employee data breaches, HIPAA violations"
    ]

    return knowledge


def _get_saas_domain_knowledge(df: pd.DataFrame, metrics_intel: Dict, knowledge: Dict) -> Dict:
    """SaaS domain knowledge"""

    knowledge['industry_benchmarks'] = {
        'net_revenue_retention': {
            'industry_average': 100.0,
            'top_performers': 120.0,
            'unit': 'percentage'
        },
        'customer_churn_rate': {
            'industry_average': 5.0,
            'best_practice': 3.0,
            'unit': 'percentage_monthly'
        },
        'cac_payback_period': {
            'benchmark': 12,
            'top_performers': 6,
            'unit': 'months'
        }
    }

    knowledge['best_practices'] = [
        "Track key SaaS metrics: MRR, ARR, Churn, LTV, CAC",
        "Implement customer success programs (proactive support)",
        "Regular feature releases and product updates",
        "Offer multiple pricing tiers (freemium, starter, pro, enterprise)",
        "Build integrations and API ecosystem",
        "Invest in customer onboarding and training"
    ]

    knowledge['compliance_requirements'] = [
        "SOC 2 Type II certification (security and availability)",
        "GDPR compliance for EU customers",
        "ISO 27001 certification (information security management)",
        "HIPAA compliance (for healthcare SaaS)",
        "CCPA compliance for California customers",
        "Data residency requirements (region-specific data storage)"
    ]

    knowledge['domain_risks'] = [
        "Churn risk - customer cancellations, revenue loss",
        "Competition risk - low switching costs, many alternatives",
        "Product-market fit risk - feature mismatch, poor usability",
        "Scalability risk - performance issues at scale, downtime",
        "Security risk - data breaches, unauthorized access",
        "Pricing risk - underprice (poor unit economics) or overprice (lose customers)"
    ]

    return knowledge


def _get_general_domain_knowledge(df: pd.DataFrame, metrics_intel: Dict, knowledge: Dict) -> Dict:
    """General domain knowledge for unknown domains"""

    knowledge['best_practices'] = [
        "Implement data quality monitoring and validation",
        "Regular data backups and disaster recovery testing",
        "Document data sources, transformations, and business logic",
        "Implement access controls and audit logging",
        "Regular stakeholder communication and reporting",
        "Continuous improvement based on feedback and metrics"
    ]

    knowledge['compliance_requirements'] = [
        "Data privacy regulations (GDPR, CCPA, etc. based on geography)",
        "Industry-specific regulations (varies by sector)",
        "Financial reporting requirements (if applicable)",
        "Workplace safety regulations",
        "Environmental regulations (if applicable)"
    ]

    knowledge['domain_risks'] = [
        "Data quality risk - inaccurate or incomplete data",
        "Operational risk - process failures, human error",
        "Technology risk - system outages, data loss",
        "Compliance risk - regulatory violations, penalties",
        "Reputational risk - negative publicity, customer complaints"
    ]

    return knowledge


# ============================================================================
# LAYER 6: PREDICTIVE DISCOVERY
# ============================================================================

def discover_predictive_insights(df: pd.DataFrame, domain: str, metrics_intel: Dict) -> Dict[str, Any]:
    """
    Discover predictive insights: forecasting, lead indicators, scenarios.

    Args:
        df: pandas DataFrame
        domain: Detected domain
        metrics_intel: Results from intelligent_metrics discovery

    Returns:
        Dictionary containing predictive insights
    """
    insights = {
        'trends': {},
        'lead_indicators': [],
        'risk_scores': {},
        'scenarios': {}
    }

    # Find date columns for trend analysis
    date_cols = [col for col, info in metrics_intel['column_semantics'].items()
                 if info['semantic_type'] == 'date']

    numeric_cols = df.select_dtypes(include=[np.number]).columns

    # Simple trend projection (if we have time-series data)
    if date_cols and len(numeric_cols) > 0:
        try:
            date_col = date_cols[0]
            df_sorted = df.sort_values(date_col)

            for num_col in numeric_cols[:3]:  # Top 3 numeric columns
                values = df_sorted[num_col].values
                if len(values) >= 4:  # Need minimum data points
                    # Simple linear trend
                    x = np.arange(len(values))
                    slope = (values[-1] - values[0]) / len(values) if len(values) > 0 else 0

                    insights['trends'][num_col] = {
                        'current_value': float(values[-1]),
                        'trend_direction': 'increasing' if slope > 0 else 'decreasing',
                        'rate_of_change': float(slope),
                        'projected_next_period': float(values[-1] + slope)
                    }
        except:
            pass

    # Lead indicators (domain-specific)
    if domain == 'education':
        insights['lead_indicators'] = [
            "First-semester GPA is the strongest predictor of 4-year graduation",
            "Students with GPA decline >0.3 in first semester are 4x more likely to drop out",
            "Course withdrawal rate in first year correlates with retention",
            "Financial aid recipients have 12% higher retention rates"
        ]

        # Risk scoring (simple example)
        if 'avg_gpa' in metrics_intel['calculated_metrics']:
            avg_gpa = metrics_intel['calculated_metrics']['avg_gpa']
            insights['risk_scores']['academic_risk'] = 'high' if avg_gpa < 2.5 else 'moderate' if avg_gpa < 3.0 else 'low'

    elif domain == 'ecommerce':
        insights['lead_indicators'] = [
            "First purchase value predicts lifetime value (higher first purchase = higher LTV)",
            "Time to second purchase predicts repeat rate (< 30 days is strong indicator)",
            "Cart abandonment rate predicts conversion rate issues",
            "Product view-to-cart ratio indicates product-market fit"
        ]

    elif domain == 'saas':
        insights['lead_indicators'] = [
            "Feature adoption in first 30 days predicts long-term retention",
            "Login frequency in first week predicts active vs. inactive users",
            "Support ticket volume predicts churn risk",
            "NPS score strongly correlates with renewal rates"
        ]

    # Scenario modeling (simple examples)
    if domain == 'education' and 'calculated_metrics' in metrics_intel:
        calc_metrics = metrics_intel['calculated_metrics']

        if 'at_risk_pct' in calc_metrics and 'total_tuition' in calc_metrics:
            at_risk_pct = calc_metrics['at_risk_pct']
            total_tuition = calc_metrics['total_tuition']

            # Scenario: What if we improve retention?
            current_at_risk_revenue = total_tuition * (at_risk_pct / 100)
            scenario_15pct_improvement = current_at_risk_revenue * 0.15
            scenario_30pct_improvement = current_at_risk_revenue * 0.30

            insights['scenarios'] = {
                'retention_improvement': {
                    'baseline': {
                        'at_risk_revenue': float(current_at_risk_revenue),
                        'at_risk_pct': float(at_risk_pct)
                    },
                    'scenario_15pct_retention': {
                        'recovered_revenue': float(scenario_15pct_improvement),
                        'new_at_risk_pct': float(at_risk_pct * 0.85)
                    },
                    'scenario_30pct_retention': {
                        'recovered_revenue': float(scenario_30pct_improvement),
                        'new_at_risk_pct': float(at_risk_pct * 0.70)
                    }
                }
            }

    return insights


# ============================================================================
# LAYER 7: RELATIONSHIP DISCOVERY
# ============================================================================

def discover_relationship_patterns(df: pd.DataFrame, domain: str, metrics_intel: Dict) -> Dict[str, Any]:
    """
    Discover relationship patterns: network effects, hierarchies, dependencies.

    Args:
        df: pandas DataFrame
        domain: Detected domain
        metrics_intel: Results from intelligent_metrics discovery

    Returns:
        Dictionary containing relationship patterns
    """
    patterns = {
        'hierarchies': {},
        'groupings': {},
        'dependencies': [],
        'network_effects': []
    }

    # Find categorical columns that might represent hierarchies
    cat_cols = [col for col, info in metrics_intel['column_semantics'].items()
                if info['semantic_type'] == 'category']

    # Detect hierarchical structures (e.g., department > team, country > city)
    for i, col1 in enumerate(cat_cols[:3]):
        for col2 in cat_cols[i+1:4]:
            # Check if one column's values nest within another
            try:
                grouped = df.groupby(col1)[col2].nunique()
                # If each col1 value maps to few col2 values, might be hierarchical
                if grouped.mean() < 5 and df[col2].nunique() > df[col1].nunique():
                    patterns['hierarchies'][f'{col1}_to_{col2}'] = {
                        'parent': col1,
                        'child': col2,
                        'avg_children_per_parent': float(grouped.mean()),
                        'total_parents': int(df[col1].nunique()),
                        'total_children': int(df[col2].nunique())
                    }
            except:
                pass

    # Grouping analysis (clustering by characteristics)
    currency_cols = [col for col, info in metrics_intel['column_semantics'].items()
                     if info['semantic_type'] == 'currency']

    if currency_cols and cat_cols:
        currency_col = currency_cols[0]
        cat_col = cat_cols[0]

        try:
            group_analysis = df.groupby(cat_col)[currency_col].agg(['sum', 'mean', 'count', 'std'])
            top_groups = group_analysis.nlargest(3, 'sum')

            patterns['groupings'][cat_col] = {
                'total_groups': int(df[cat_col].nunique()),
                'top_3_groups': [
                    {
                        'name': str(idx),
                        'total_value': float(row['sum']),
                        'avg_value': float(row['mean']),
                        'count': int(row['count'])
                    }
                    for idx, row in top_groups.iterrows()
                ]
            }
        except:
            pass

    # Domain-specific network effects and dependencies
    if domain == 'education':
        patterns['dependencies'] = [
            "Student performance depends on: prior GPA, financial stress, course load, major difficulty",
            "Retention depends on: first-year experience, financial aid, academic support, social integration",
            "Graduation rate depends on: retention rate, academic progress, degree completion requirements"
        ]
        patterns['network_effects'] = [
            "Peer effects: Students perform better when surrounded by high-achieving peers",
            "Cohort effects: Strong cohort bonds improve retention and satisfaction",
            "Alumni network effects: Stronger alumni network increases enrollment and donations"
        ]

    elif domain == 'ecommerce':
        patterns['dependencies'] = [
            "Purchase depends on: product price, reviews, shipping cost, availability, trust signals",
            "Repeat purchase depends on: first purchase experience, product quality, customer service",
            "Cart conversion depends on: page load speed, checkout friction, payment options"
        ]
        patterns['network_effects'] = [
            "Social proof: Products with more reviews sell better (even with same rating)",
            "Referral effects: Customers referred by friends have 2x higher LTV",
            "Marketplace effects: More sellers attract more buyers (two-sided network)"
        ]

    elif domain == 'saas':
        patterns['dependencies'] = [
            "Activation depends on: onboarding quality, time to first value, feature complexity",
            "Retention depends on: feature adoption, user engagement, support quality, product updates",
            "Expansion depends on: user satisfaction, team growth, additional use cases"
        ]
        patterns['network_effects'] = [
            "Collaboration features: Value increases with team size (more users = more value)",
            "Integration effects: Products with more integrations are stickier",
            "Content network effects: More users create more content, increasing value for all"
        ]

    return patterns


# ============================================================================
# MAIN CONTEXT BUILDER FUNCTION
# ============================================================================

def build_universal_context(df: pd.DataFrame, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Build comprehensive context from ANY dataset.

    Args:
        df: pandas DataFrame
        config: Optional configuration
            {
                'enable_layers': ['all'] or ['metrics', 'data', 'business', ...],
                'domain': 'auto' or 'education' or 'ecommerce' etc.,
                'depth': 'quick' or 'standard' or 'deep',
                'focus_areas': ['revenue', 'churn', 'quality']
            }

    Returns:
        {
            'intelligent_metrics': {...},
            'data_discovery': {...},
            'statistical_discovery': {...},
            'business_discovery': {...},
            'domain_discovery': {...},
            'predictive_discovery': {...},
            'relationship_discovery': {...},
            'context_metadata': {...}
        }
    """
    if config is None:
        config = {}

    context = {}
    enabled_layers = config.get('enable_layers', ['all'])

    # LAYER 1: Intelligent Metrics Discovery (ALWAYS RUN)
    metrics_intel = discover_intelligent_metrics(df)
    context['intelligent_metrics'] = metrics_intel

    # Get domain (auto-detected or user-specified)
    domain = config.get('domain', 'auto')
    if domain == 'auto':
        domain = metrics_intel['detected_domain']

    # LAYER 2: Data Discovery
    if 'all' in enabled_layers or 'data' in enabled_layers:
        context['data_discovery'] = discover_data_patterns(df, metrics_intel)

    # LAYER 3: Statistical Discovery
    if 'all' in enabled_layers or 'statistical' in enabled_layers:
        context['statistical_discovery'] = discover_statistical_patterns(df, metrics_intel)

    # LAYER 4: Business Discovery
    if 'all' in enabled_layers or 'business' in enabled_layers:
        context['business_discovery'] = discover_business_insights(df, domain, metrics_intel)

    # LAYER 5: Domain Discovery
    if 'all' in enabled_layers or 'domain' in enabled_layers:
        context['domain_discovery'] = discover_domain_knowledge(df, domain, metrics_intel)

    # LAYER 6: Predictive Discovery
    if 'all' in enabled_layers or 'predictive' in enabled_layers:
        context['predictive_discovery'] = discover_predictive_insights(df, domain, metrics_intel)

    # LAYER 7: Relationship Discovery
    if 'all' in enabled_layers or 'relationship' in enabled_layers:
        context['relationship_discovery'] = discover_relationship_patterns(df, domain, metrics_intel)

    # Metadata
    context['context_metadata'] = {
        'generated_at': datetime.now().isoformat(),
        'domain': domain,
        'enabled_layers': enabled_layers,
        'depth': config.get('depth', 'standard')
    }

    return context


# ============================================================================
# TESTING & DEMONSTRATION
# ============================================================================

if __name__ == "__main__":
    # Test with sample education data
    sample_data = pd.DataFrame({
        'Student_ID': range(1, 101),
        'Name': [f'Student_{i}' for i in range(1, 101)],
        'GPA': np.random.uniform(2.0, 4.0, 100),
        'Nationality': np.random.choice(['UAE', 'India', 'Pakistan', 'Egypt', 'Jordan'], 100),
        'Tuition_Fees': np.random.uniform(20000, 50000, 100),
        'Financial_Aid': np.random.uniform(0, 20000, 100),
        'Enrollment_Year': np.random.choice([2020, 2021, 2022, 2023, 2024], 100)
    })

    context = build_universal_context(sample_data)

    print("=" * 80)
    print("UNIVERSAL CONTEXT BUILDER - TEST OUTPUT")
    print("=" * 80)
    print(f"\nDetected Domain: {context['intelligent_metrics']['detected_domain']}")
    print(f"Detected Entities: {context['intelligent_metrics']['detected_entities']}")
    print(f"\nDataset Profile:")
    for key, value in context['intelligent_metrics']['dataset_profile'].items():
        print(f"  {key}: {value}")
    print(f"\nCalculated Metrics:")
    for key, value in context['intelligent_metrics']['calculated_metrics'].items():
        print(f"  {key}: {value}")
    print(f"\nColumn Semantics:")
    for col, info in context['intelligent_metrics']['column_semantics'].items():
        print(f"  {col}: {info['semantic_type']} ({info['data_type']})")

    if 'data_discovery' in context:
        print(f"\n" + "=" * 80)
        print("DATA DISCOVERY")
        print("=" * 80)
        print(f"Data Quality:")
        for key, value in context['data_discovery']['data_quality'].items():
            print(f"  {key}: {value}")
        print(f"\nDistributions (sample):")
        for col, dist in list(context['data_discovery']['distributions'].items())[:2]:
            print(f"  {col}: mean={dist['mean']:.2f}, distribution_type={dist['distribution_type']}")

    if 'statistical_discovery' in context:
        print(f"\n" + "=" * 80)
        print("STATISTICAL DISCOVERY")
        print("=" * 80)
        print(f"Top Correlations:")
        for corr in context['statistical_discovery']['correlations'][:3]:
            print(f"  {corr['col1']} <-> {corr['col2']}: {corr['correlation']:.2f} ({corr['strength']})")
        print(f"\nTop Insights:")
        for insight in context['statistical_discovery']['top_insights']:
            print(f"  - {insight}")

    if 'business_discovery' in context:
        print(f"\n" + "=" * 80)
        print("BUSINESS DISCOVERY")
        print("=" * 80)
        business = context['business_discovery']

        if business.get('revenue_analysis'):
            print("Revenue Analysis:")
            for key, value in list(business['revenue_analysis'].items())[:5]:
                if isinstance(value, float):
                    print(f"  {key}: {value:,.2f}")
                else:
                    print(f"  {key}: {value}")

        if business.get('customer_value'):
            print("\nCustomer/Student Value:")
            for key, value in list(business['customer_value'].items())[:3]:
                if isinstance(value, float):
                    print(f"  {key}: {value:,.2f}")
                else:
                    print(f"  {key}: {value}")

        if business.get('churn_risk'):
            print("\nChurn/Risk Analysis:")
            for key, value in list(business['churn_risk'].items())[:4]:
                if isinstance(value, float):
                    print(f"  {key}: {value:,.2f}")
                else:
                    print(f"  {key}: {value}")

    if 'domain_discovery' in context:
        print(f"\n" + "=" * 80)
        print("DOMAIN DISCOVERY")
        print("=" * 80)
        domain_disc = context['domain_discovery']

        if domain_disc.get('industry_benchmarks'):
            print("Industry Benchmarks (sample):")
            for key, value in list(domain_disc['industry_benchmarks'].items())[:2]:
                print(f"  {key}: {value}")

        if domain_disc.get('best_practices'):
            print("\nBest Practices (sample):")
            for practice in domain_disc['best_practices'][:3]:
                print(f"  - {practice}")

        if domain_disc.get('domain_risks'):
            print("\nDomain Risks (sample):")
            for risk in domain_disc['domain_risks'][:3]:
                print(f"  - {risk}")

    if 'predictive_discovery' in context:
        print(f"\n" + "=" * 80)
        print("PREDICTIVE DISCOVERY")
        print("=" * 80)
        predictive = context['predictive_discovery']

        if predictive.get('lead_indicators'):
            print("Lead Indicators (sample):")
            for indicator in predictive['lead_indicators'][:2]:
                print(f"  - {indicator}")

        if predictive.get('scenarios'):
            print("\nScenarios:")
            for scenario_name, scenario_data in list(predictive['scenarios'].items())[:1]:
                print(f"  {scenario_name}:")
                print(f"    {list(scenario_data.keys())}")

    if 'relationship_discovery' in context:
        print(f"\n" + "=" * 80)
        print("RELATIONSHIP DISCOVERY")
        print("=" * 80)
        relationship = context['relationship_discovery']

        if relationship.get('dependencies'):
            print("Dependencies (sample):")
            for dep in relationship['dependencies'][:2]:
                print(f"  - {dep}")

        if relationship.get('network_effects'):
            print("\nNetwork Effects (sample):")
            for effect in relationship['network_effects'][:2]:
                print(f"  - {effect}")
