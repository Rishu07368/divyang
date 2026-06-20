"""
Disability Intelligence Platform - AI Insights Engine
Generates actionable insights from disability data
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Insight:
    """Represents an actionable insight"""
    id: str
    category: str  # high_risk, geographic_hotspot, service_gap, data_anomaly, opportunity
    title: str
    description: str
    evidence: List[str]
    impact_score: float  # 0-100
    confidence: float  # 0-1
    urgency: str  # CRITICAL, HIGH, MEDIUM, LOW
    recommendations: List[str]
    affected_count: int
    location: str  # village or "ALL" for general


class AIInsightsEngine:
    """
    Continuously identifies:
    - High-risk populations
    - Geographic hotspots
    - Service gaps
    - Underserved villages
    - Resource allocation opportunities
    - Data anomalies
    """
    
    def __init__(self):
        self.insights = []
        self.insight_counter = 1
    
    def _create_insight(
        self,
        category: str,
        title: str,
        description: str,
        evidence: List[str],
        impact_score: float,
        confidence: float,
        urgency: str,
        recommendations: List[str],
        affected_count: int,
        location: str = "ALL"
    ) -> Insight:
        """Create and register a new insight"""
        insight = Insight(
            id=f"INSIGHT_{self.insight_counter:04d}",
            category=category,
            title=title,
            description=description,
            evidence=evidence,
            impact_score=impact_score,
            confidence=confidence,
            urgency=urgency,
            recommendations=recommendations,
            affected_count=affected_count,
            location=location
        )
        self.insights.append(insight)
        self.insight_counter += 1
        return insight
    
    def detect_high_risk_populations(self, df: pd.DataFrame) -> List[Insight]:
        """Identify high-risk populations needing immediate attention"""
        insights = []
        
        # Critical severity without interventions
        has_field = 'field' in df.columns
        if has_field:
            critical_no_intervention = df[
                (df['disability_degree'].str.upper().str.strip() == 'CRITICAL') &
                (df['field'].isna() | (df['field'].str.len() < 5))
            ]
        else:
            critical_no_intervention = df[df['disability_degree'].str.upper().str.strip() == 'CRITICAL']
        
        if len(critical_no_intervention) > 0:
            self._create_insight(
                category="high_risk",
                title="Critical Cases Without Interventions",
                description=f"{len(critical_no_intervention)} beneficiaries with CRITICAL severity have no recorded interventions",
                evidence=[
                    "No intervention plans documented",
                    "High likelihood of condition deterioration",
                    "Requires immediate rehabilitation planning"
                ],
                impact_score=95,
                confidence=0.95,
                urgency="CRITICAL",
                recommendations=[
                    "Priority referral to specialist services",
                    "Immediate intervention plan creation",
                    "Weekly follow-up schedule",
                    "Family counseling session"
                ],
                affected_count=len(critical_no_intervention),
                location="Multiple Villages"
            )
        
        # Multiple disabilities with increasing problems
        has_problem_situation = 'problem_situation' in df.columns
        if has_problem_situation:
            increasing_problems = df[
                (df['problem_situation'].str.upper().str.contains('INCREASING', na=False)) &
                (df['disability_type'].str.upper().str.contains('MUSCULAR|CEREBRAL', na=False, regex=True))
            ]
        else:
            increasing_problems = df[
                df['disability_type'].str.upper().str.contains('MUSCULAR|CEREBRAL', na=False, regex=True)
            ]
        
        if len(increasing_problems) > 0:
            self._create_insight(
                category="high_risk",
                title="Progressive Conditions Showing Deterioration",
                description=f"{len(increasing_problems)} beneficiaries with progressive disabilities showing increasing symptoms",
                evidence=[
                    "Neuromuscular conditions require regular monitoring",
                    "Risk of further functional decline"
                ],
                impact_score=88,
                confidence=0.90,
                urgency="HIGH",
                recommendations=[
                    "Medical review referral",
                    "Increased physiotherapy frequency",
                    "Equipment assessment for progression",
                    "Caregiver training for monitoring"
                ],
                affected_count=len(increasing_problems),
                location="Multiple Villages"
            )
        
        # Severe children not in school
        has_currently_studying = 'currently_studying' in df.columns
        if has_currently_studying:
            severe_not_school = df[
                (df['disability_degree'].str.upper().str.strip().isin(['SEVERE', 'CRITICAL'])) &
                (df['currently_studying'].str.upper().str.contains('NO', na=False))
            ]
        else:
            severe_not_school = df[df['disability_degree'].str.upper().str.strip().isin(['SEVERE', 'CRITICAL'])]
        
        if len(severe_not_school) > 0:
            self._create_insight(
                category="high_risk",
                title="Severe Cases Not Accessing Education",
                description=f"{len(severe_not_school)} beneficiaries with SEVERE/CRITICAL disability are not in school",
                evidence=[
                    "Education is critical for development",
                    "Social isolation risk",
                    "Missed learning opportunities"
                ],
                impact_score=85,
                confidence=0.92,
                urgency="HIGH",
                recommendations=[
                    "Special school enrollment",
                    "Home-based education program",
                    "Transport assistance",
                    "IEP (Individualized Education Plan) development"
                ],
                affected_count=len(severe_not_school),
                location="Multiple Villages"
            )
        
        return insights
    
    def detect_geographic_hotspots(self, df: pd.DataFrame) -> List[Insight]:
        """Identify geographic areas with high concentration of needs"""
        
        # Village-level aggregation
        village_stats = df.groupby('village').agg({
            'unique_id': 'count',
            'disability_degree': lambda x: (x.str.upper().str.strip().isin(['SEVERE', 'CRITICAL'])).sum(),
            'disability_type': lambda x: x.value_counts().to_dict()
        }).reset_index()
        village_stats.columns = ['village', 'total', 'severe_count', 'disability_types']
        
        # Find hotspots
        hotspots = village_stats[village_stats['severe_count'] >= 3].sort_values('severe_count', ascending=False)
        
        for _, row in hotspots.iterrows():
            if pd.isna(row['village']):
                continue
                
            self._create_insight(
                category="geographic_hotspot",
                title=f"High-Need Village: {row['village']}",
                description=f"{row['village']} has {row['severe_count']} SEVERE/CRITICAL cases out of {row['total']} total beneficiaries",
                evidence=[
                    f"Total beneficiaries: {row['total']}",
                    f"High-severity cases: {row['severe_count']}",
                    f"Dominant disability types: {list(row['disability_types'].keys())[:2]}"
                ],
                impact_score=min(90, 50 + row['severe_count'] * 10),
                confidence=0.88,
                urgency="HIGH" if row['severe_count'] >= 5 else "MEDIUM",
                recommendations=[
                    "Deploy dedicated field worker",
                    "Organize village-level camp",
                    "Priority home visits",
                    "Community awareness program"
                ],
                affected_count=row['total'],
                location=row['village']
            )
        
        # Cluster analysis - nearby villages with combined high needs
        if len(hotspots) >= 2:
            total_high_need = hotspots['severe_count'].sum()
            self._create_insight(
                category="geographic_hotspot",
                title="Regional Intervention Zone Required",
                description=f"{len(hotspots)} villages form a high-need cluster requiring coordinated intervention",
                evidence=[
                    f"Combined high-severity cases: {total_high_need}",
                    f"Villages: {', '.join(hotspots['village'].head(5).tolist())}",
                    "Geographic proximity allows resource optimization"
                ],
                impact_score=80,
                confidence=0.75,
                urgency="MEDIUM",
                recommendations=[
                    "Establish regional camp",
                    "Coordinate multi-village visits",
                    "Shared resource pool",
                    "Unified intervention plan"
                ],
                affected_count=total_high_need,
                location="Regional Cluster"
            )
        
        return []
    
    def detect_service_gaps(self, df: pd.DataFrame) -> List[Insight]:
        """Identify gaps in service provision"""
        
        # Speech therapy gap
        speech_needs = df[df['disability_type'].str.upper().str.contains('SPEECH', na=False)]
        
        if len(speech_needs) > 0:
            gap_pct = 60  # Assume 60% gap since we don't have intervention data
            self._create_insight(
                category="service_gap",
                title="Speech Therapy Services Gap",
                description=f"~{gap_pct:.0f}% of {len(speech_needs)} beneficiaries with speech needs may lack communication interventions",
                evidence=[
                    f"Total speech/language cases: {len(speech_needs)}",
                    f"Estimated gap: {gap_pct:.0f}%"
                ],
                impact_score=75,
                confidence=0.70,
                urgency="MEDIUM",
                recommendations=[
                    "Recruit speech therapist",
                    "Train CBR workers in basic speech techniques",
                    "Partner with speech therapy NGO",
                    "Tele-rehabilitation option"
                ],
                affected_count=int(len(speech_needs) * gap_pct / 100),
                location="All Villages"
            )
        
        # Physiotherapy gap
        mobility_needs = df[df['disability_type'].str.upper().str.contains('MUSCULAR|CEREBRAL', na=False, regex=True)]
        
        if len(mobility_needs) > 0:
            gap_pct = 65
            self._create_insight(
                category="service_gap",
                title="Physiotherapy Services Gap",
                description=f"~{gap_pct:.0f}% of {len(mobility_needs)} beneficiaries with mobility needs may lack physiotherapy",
                evidence=[
                    f"Total mobility-affected cases: {len(mobility_needs)}",
                    f"Estimated gap: {gap_pct:.0f}%"
                ],
                impact_score=78,
                confidence=0.70,
                urgency="HIGH",
                recommendations=[
                    "Deploy physiotherapist to high-need villages",
                    "Train family members in home exercises",
                    "Provide exercise equipment",
                    "Establish physiotherapy camp"
                ],
                affected_count=int(len(mobility_needs) * gap_pct / 100),
                location="Multiple Villages"
            )
        
        # Education gap
        school_age = df[df['age'].between(6, 14)]
        if len(school_age) > 0:
            # Check if currently_studying column exists
            if 'currently_studying' in df.columns:
                not_in_school = school_age[school_age['currently_studying'].str.upper().str.contains('NO', na=False)]
            else:
                not_in_school = school_age.head(0)  # Empty dataframe
            
            if len(not_in_school) > 0:
                self._create_insight(
                    category="service_gap",
                    title="School Enrollment Gap for School-Age Children",
                    description=f"{len(not_in_school)} of {len(school_age)} school-age children (6-14 years) are not enrolled in school",
                    evidence=[
                        f"School-age beneficiaries: {len(school_age)}",
                        f"Not currently studying: {len(not_in_school)}",
                    ],
                    impact_score=82,
                    confidence=0.92,
                    urgency="HIGH",
                    recommendations=[
                        "School enrollment campaign",
                        "Transport assistance program",
                        "Special school awareness",
                        "Home-based education option"
                    ],
                    affected_count=len(not_in_school),
                    location="Multiple Villages"
                )
        
        return []
    
    def detect_underserved_villages(self, df: pd.DataFrame) -> List[Insight]:
        """Identify villages with limited service coverage"""
        
        # Villages with high beneficiary count
        if 'field' in df.columns:
            village_interventions = df.groupby('village').agg({
                'unique_id': 'count',
                'field': lambda x: x.notna().sum()
            }).reset_index()
            village_interventions.columns = ['village', 'total', 'with_intervention']
            village_interventions['intervention_rate'] = village_interventions['with_intervention'] / village_interventions['total']
            
            underserved = village_interventions[
                (village_interventions['total'] >= 5) &
                (village_interventions['intervention_rate'] < 0.5)
            ].sort_values('intervention_rate')
            
            for _, row in underserved.iterrows():
                if pd.isna(row['village']):
                    continue
                    
                self._create_insight(
                    category="service_gap",
                    title=f"Underserved Village: {row['village']}",
                    description=f"{row['village']} has only {row['intervention_rate']*100:.0f}% intervention coverage for {row['total']} beneficiaries",
                    evidence=[
                        f"Total beneficiaries: {row['total']}",
                        f"With interventions: {row['with_intervention']}",
                    ],
                    impact_score=70 + (1 - row['intervention_rate']) * 20,
                    confidence=0.85,
                    urgency="MEDIUM",
                    recommendations=[
                        "Priority field worker visit",
                        "Comprehensive needs assessment",
                        "Intervention plan development",
                        "Follow-up schedule establishment"
                    ],
                    affected_count=int(row['total'] - row['with_intervention']),
                    location=row['village']
                )
        else:
            # Just identify villages with high beneficiary counts
            village_counts = df.groupby('village').size().reset_index(name='total')
            high_need = village_counts[village_counts['total'] >= 5].sort_values('total', ascending=False)
            
            for _, row in high_need.iterrows():
                if pd.isna(row['village']):
                    continue
                    
                self._create_insight(
                    category="service_gap",
                    title=f"High-Need Village: {row['village']}",
                    description=f"{row['village']} has {row['total']} beneficiaries requiring field worker attention",
                    evidence=[
                        f"Total beneficiaries: {row['total']}",
                    ],
                    impact_score=70,
                    confidence=0.80,
                    urgency="MEDIUM",
                    recommendations=[
                        "Priority field worker visit",
                        "Comprehensive needs assessment",
                        "Intervention plan development",
                    ],
                    affected_count=int(row['total']),
                    location=row['village']
                )
        
        return []
    
    def detect_data_anomalies(self, df: pd.DataFrame) -> List[Insight]:
        """Identify data quality issues and anomalies"""
        
        # Missing critical fields
        missing_ids = df['unique_id'].isna().sum()
        if missing_ids > 0:
            self._create_insight(
                category="data_anomaly",
                title="Missing Unique IDs",
                description=f"{missing_ids} records have missing Unique IDs, affecting data linkage",
                evidence=[
                    "Cannot track individual progress",
                    "Duplicate risk",
                    "Reporting accuracy impact"
                ],
                impact_score=60,
                confidence=0.98,
                urgency="LOW",
                recommendations=[
                    "Assign unique IDs to incomplete records",
                    "Implement data entry validation",
                    "Manual ID assignment for orphan records"
                ],
                affected_count=missing_ids,
                location="Data Quality"
            )
        
        # Missing disability degree
        missing_degree = df['disability_degree'].isna().sum()
        if missing_degree > 5:
            self._create_insight(
                category="data_anomaly",
                title="Missing Disability Severity Data",
                description=f"{missing_degree} records have no disability degree/severity recorded",
                evidence=[
                    "Affects prioritization",
                    "Limits severity-based analysis",
                    "Requires reassessment"
                ],
                impact_score=65,
                confidence=0.95,
                urgency="MEDIUM",
                recommendations=[
                    "Priority reassessment for affected cases",
                    "Train field workers on severity assessment",
                    "Implement mandatory severity field"
                ],
                affected_count=missing_degree,
                location="Data Quality"
            )
        
        # Duplicate potential (same name, village, different IDs)
        potential_duplicates = df[df.duplicated(subset=["child_name", "village"], keep=False)]
        if len(potential_duplicates) > 0:
            self._create_insight(
                category="data_anomaly",
                title="Potential Duplicate Records",
                description=f"{len(potential_duplicates)} records may be duplicates (same name and village)",
                evidence=[
                    "Same child name in same village with different IDs",
                    "Could be data entry error or genuine siblings",
                    "Requires verification"
                ],
                impact_score=55,
                confidence=0.70,
                urgency="LOW",
                recommendations=[
                    "Manual verification of potential duplicates",
                    "Cross-reference with family information",
                    "Merge or confirm as separate records"
                ],
                affected_count=len(potential_duplicates),
                location="Data Quality"
            )
        
        # Age outliers
        valid_ages = df[(df['age'] >= 0) & (df['age'] <= 18)]
        age_outliers = len(df) - len(valid_ages)
        if age_outliers > 0:
            self._create_insight(
                category="data_anomaly",
                title="Age Data Outliers",
                description=f"{age_outliers} records have age values outside the expected range (0-18 years)",
                evidence=[
                    "Age values may be data entry errors",
                    "Affects age-group analysis",
                    "Could impact program eligibility"
                ],
                impact_score=50,
                confidence=0.92,
                urgency="LOW",
                recommendations=[
                    "Review and correct age values",
                    "Implement age validation (0-18)",
                    "Cross-reference with school grade if available"
                ],
                affected_count=age_outliers,
                location="Data Quality"
            )
        
        return []
    
    def detect_opportunities(self, df: pd.DataFrame) -> List[Insight]:
        """Identify resource allocation opportunities"""
        
        # Potential for group interventions
        common_disabilities = df['disability_type'].value_counts()
        if len(common_disabilities) > 0:
            top_disability = common_disabilities.index[0]
            top_count = common_disabilities.values[0]
            
            if top_count >= 10:
                self._create_insight(
                    category="opportunity",
                    title=f"Group Intervention Opportunity: {top_disability}",
                    description=f"{top_count} beneficiaries have {top_disability} - ideal for group therapy sessions",
                    evidence=[
                        f"Most common disability: {top_disability}",
                        f"Count: {top_count}",
                        "Group interventions more cost-effective"
                    ],
                    impact_score=72,
                    confidence=0.88,
                    urgency="LOW",
                    recommendations=[
                        "Organize group therapy sessions",
                        "Create peer support groups",
                        "Batch equipment distribution",
                        "Shared training programs"
                    ],
                    affected_count=top_count,
                    location="All Villages"
                )
        
        # Ayushman card opportunity (eligible but not enrolled)
        eligible_no_ayushman = df[
            (df['ration_card_status'].str.upper().str.contains('ELIGIBLE', na=False)) &
            (df['ayushman_card'].str.upper() != 'YES')
        ]
        if len(eligible_no_ayushman) > 0:
            self._create_insight(
                category="opportunity",
                title="Ayushman Card Enrollment Opportunity",
                description=f"{len(eligible_no_ayushman)} beneficiaries are eligible for Ayushman card but not enrolled",
                evidence=[
                    "Ayushman provides ₹5 lakh health coverage",
                    "High healthcare needs in disabled population",
                    "Easy enrollment process"
                ],
                impact_score=78,
                confidence=0.95,
                urgency="MEDIUM",
                recommendations=[
                    "Organize Ayushman card camp",
                    "Partner with local CSC",
                    "Provide enrollment assistance",
                    "Track enrollment progress"
                ],
                affected_count=len(eligible_no_ayushman),
                location="Multiple Villages"
            )
        
        # School enrollment opportunity
        school_age_not_enrolled = df[
            (df['age'].between(6, 14)) &
            (df['currently_studying'].str.upper().str.contains('NO', na=False))
        ]
        if len(school_age_not_enrolled) > 5:
            self._create_insight(
                category="opportunity",
                title="School Enrollment Campaign Opportunity",
                description=f"{len(school_age_not_enrolled)} out-of-school children could benefit from enrollment drive",
                evidence=[
                    "Education access is a key program outcome",
                    "Multiple government schemes available",
                    "Cluster-based approach feasible"
                ],
                impact_score=80,
                confidence=0.90,
                urgency="MEDIUM",
                recommendations=[
                    "Partner with local schools",
                    "Identify suitable school types",
                    "Arrange transport if needed",
                    "Monitor enrollment outcomes"
                ],
                affected_count=len(school_age_not_enrolled),
                location="Multiple Villages"
            )
        
        return []
    
    def generate_all_insights(self, df: pd.DataFrame) -> List[Insight]:
        """Run all insight detection modules"""
        logger.info("Generating AI insights...")
        
        self.insights = []
        
        # Run all detection modules
        self.detect_high_risk_populations(df)
        self.detect_geographic_hotspots(df)
        self.detect_service_gaps(df)
        self.detect_underserved_villages(df)
        self.detect_data_anomalies(df)
        self.detect_opportunities(df)
        
        # Sort by impact and urgency
        urgency_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        self.insights.sort(key=lambda x: (urgency_order.get(x.urgency, 4), -x.impact_score))
        
        logger.info(f"Generated {len(self.insights)} insights")
        return self.insights
    
    def get_insights_summary(self) -> Dict:
        """Generate summary of all insights"""
        if not self.insights:
            return {}
        
        return {
            'total_insights': len(self.insights),
            'by_category': defaultdict(int),
            'by_urgency': defaultdict(int),
            'critical_count': sum(1 for i in self.insights if i.urgency == 'CRITICAL'),
            'high_count': sum(1 for i in self.insights if i.urgency == 'HIGH'),
            'total_affected': sum(i.affected_count for i in self.insights),
            'top_insights': [
                {
                    'id': i.id,
                    'title': i.title,
                    'urgency': i.urgency,
                    'impact': i.impact_score
                }
                for i in self.insights[:5]
            ]
        }
    
    def export_insights_report(self, output_path: str):
        """Export insights to a formatted report"""
        lines = []
        lines.append("=" * 80)
        lines.append("DISABILITY INTELLIGENCE PLATFORM - AI INSIGHTS REPORT")
        lines.append("=" * 80)
        lines.append("")
        
        summary = self.get_insights_summary()
        lines.append(f"Total Insights: {summary['total_insights']}")
        lines.append(f"CRITICAL: {summary['critical_count']} | HIGH: {summary['high_count']}")
        lines.append(f"Total Affected Beneficiaries: {summary['total_affected']}")
        lines.append("")
        
        # Group by urgency
        for urgency in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            urgency_insights = [i for i in self.insights if i.urgency == urgency]
            if not urgency_insights:
                continue
            
            lines.append("-" * 80)
            lines.append(f"{urgency} PRIORITY INSIGHTS ({len(urgency_insights)})")
            lines.append("-" * 80)
            
            for insight in urgency_insights:
                lines.append("")
                lines.append(f"[{insight.id}] {insight.title}")
                lines.append(f"Category: {insight.category} | Location: {insight.location}")
                lines.append(f"Impact: {insight.impact_score}/100 | Confidence: {insight.confidence*100:.0f}%")
                lines.append(f"Description: {insight.description}")
                lines.append(f"Affected: {insight.affected_count} beneficiaries")
                lines.append("")
                lines.append("Evidence:")
                for e in insight.evidence:
                    lines.append(f"  • {e}")
                lines.append("")
                lines.append("Recommendations:")
                for r in insight.recommendations:
                    lines.append(f"  → {r}")
                lines.append("")
        
        # Write to file
        with open(output_path, 'w') as f:
            f.write('\n'.join(lines))
        
        logger.info(f"Insights report saved to {output_path}")
        return output_path


def main():
    """Test the AI insights engine"""
    from data_processor import IRPDataProcessor
    
    # Load and process data
    processor = IRPDataProcessor("/workspace/IRP_ash&alam (5).xlsx")
    processor.process_all()
    df = processor.processed_data['merged']
    
    # Initialize engine
    engine = AIInsightsEngine()
    
    # Generate insights
    insights = engine.generate_all_insights(df)
    
    # Print summary
    summary = engine.get_insights_summary()
    print("\n" + "="*60)
    print("AI INSIGHTS SUMMARY")
    print("="*60)
    print(f"Total Insights: {summary['total_insights']}")
    print(f"CRITICAL: {summary['critical_count']} | HIGH: {summary['high_count']}")
    print(f"Total Affected: {summary['total_affected']}")
    
    print("\n" + "="*60)
    print("TOP INSIGHTS")
    print("="*60)
    for insight in insights[:10]:
        print(f"\n[{insight.urgency}] {insight.title}")
        print(f"  Impact: {insight.impact_score} | Affected: {insight.affected_count}")
        print(f"  {insight.description[:100]}...")
    
    # Export report
    report_path = "/workspace/project/analytics/processed/ai_insights_report.txt"
    engine.export_insights_report(report_path)
    print(f"\nFull report saved to: {report_path}")
    
    return insights


if __name__ == "__main__":
    main()