"""
Disability Intelligence Platform - Severity Engine
Infers disability severity based on functional assessments, symptoms, and educational needs
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SeverityScore:
    """Represents a severity assessment result"""
    level: str  # MILD, MODERATE, SEVERE, CRITICAL
    score: float  # 0-100
    confidence: float  # 0-1
    factors: List[str]
    reasoning: str
    recommendations: List[str]


class SeverityEngine:
    """
    Determines disability severity using multiple factors:
    - Self-reported disability degree
    - Functional assessment scores
    - Number of affected domains
    - Educational needs
    - Mobility aids required
    - Health conditions
    """
    
    # Scoring weights for different factors
    WEIGHTS = {
        'self_reported': 0.30,  # Weight for existing self-reported degree
        'functional_domains': 0.35,  # Weight for functional limitation scores
        'affected_domains': 0.15,  # Weight for number of affected domains
        'education_needs': 0.10,  # Weight for educational support needs
        'mobility_aids': 0.10,  # Weight for mobility aid requirements
    }
    
    # Difficulty level mappings
    DIFFICULTY_MAP = {
        'NO DIFFICULTY': 0,
        'कोई कठिनाई नहीं': 0,
        'SOME DIFFICULTY': 1,
        'कुछ कठिनाई': 1,
        'A LOT OF DIFFICULTY': 2,
        'बहुत अधिक कठिनाई': 2,
    }
    
    # Disability type severity baseline (based on typical impact)
    DISABILITY_BASELINE = {
        'SPEECH AND LANGUAGE': {'base': 30, 'variance': 15},
        'HEARING IMPAIRMENT': {'base': 35, 'variance': 15},
        'VISUAL IMPAIRMENT': {'base': 40, 'variance': 20},
        'INTELLECTUAL DISABILITY': {'base': 55, 'variance': 20},
        'CEREBRAL PALSY': {'base': 60, 'variance': 25},
        'MUSCULAR DYSTROPHY': {'base': 65, 'variance': 20},
        'AUTISM SPECTRUM': {'base': 50, 'variance': 25},
        'MULTIPLE DISABILITIES': {'base': 70, 'variance': 20},
        'DOWN SYNDROME': {'base': 50, 'variance': 20},
        'LEARNING DISABILITY': {'base': 35, 'variance': 15},
    }
    
    def __init__(self):
        self.severity_thresholds = {
            'MILD': (0, 35),
            'MODERATE': (35, 55),
            'SEVERE': (55, 75),
            'CRITICAL': (75, 100),
        }
    
    def normalize_severity(self, degree: str) -> Optional[float]:
        """Convert self-reported degree to normalized score (0-100)"""
        if pd.isna(degree):
            return None
        
        degree = str(degree).upper().strip()
        
        mapping = {
            'MILD': 25,
            'MODERATE': 50,
            'SEVERE': 75,
            'CRITICAL': 90,
            'PROFOUND': 95,
        }
        
        return mapping.get(degree, None)
    
    def calculate_functional_score(self, row: pd.Series) -> Tuple[float, List[str]]:
        """
        Calculate functional limitation score based on assessment domains
        Returns (score, affected_domains_list)
        """
        score = 0
        affected_domains = []
        
        domains = [
            ('movement', 'movement_difficulty_level'),
            ('selfcare', 'selfcare_difficulty_level'),
            ('communication', 'communication_difficulty_level'),
            ('learning', 'learning_difficulty_level'),
            ('behavior', 'behavior_difficulty_level'),
            ('social', 'social_difficulty_level'),
        ]
        
        for domain_name, col_name in domains:
            if col_name in row.index and pd.notna(row[col_name]):
                difficulty = self.DIFFICULTY_MAP.get(str(row[col_name]).strip(), 1)
                if difficulty > 0:
                    score += difficulty * 15  # Each domain max 30 points
                    affected_domains.append(domain_name)
        
        # Scale to 0-100
        max_possible = len(domains) * 30
        normalized_score = (score / max_possible) * 100 if max_possible > 0 else 0
        
        return normalized_score, affected_domains
    
    def assess_education_needs(self, row: pd.Series) -> float:
        """Assess educational support needs (0-100)"""
        score = 0
        factors = []
        
        # Check if currently studying
        currently_studying = row.get('currently_studying', '')
        if pd.notna(currently_studying):
            if 'NO' in str(currently_studying).upper():
                score += 30
                factors.append('Not currently in school')
        
        # Check learning difficulty
        learning_level = row.get('learning_difficulty_level', '')
        if pd.notna(learning_level):
            difficulty = self.DIFFICULTY_MAP.get(str(learning_level).strip(), 0)
            score += difficulty * 20
        
        # Check school type
        school_type = row.get('school_type', '')
        if pd.notna(school_type):
            if 'SPECIAL' in str(school_type).upper():
                score += 15
                factors.append('Requires special school')
            elif 'MAINSTREAM' in str(school_type).upper():
                score += 5
        
        return min(score, 100)
    
    def assess_mobility_needs(self, row: pd.Series) -> float:
        """Assess mobility aid requirements (0-100)"""
        score = 0
        
        mobility_aids = row.get('mobility_aids', '')
        if pd.notna(mobility_aids):
            aids = str(mobility_aids).upper()
            
            if 'WHEELCHAIR' in aids:
                score += 40
            if 'CRUTCHES' in aids or 'WALKER' in aids:
                score += 25
            if 'BRACES' in aids or 'ORTHOTIC' in aids:
                score += 30
            if 'CANE' in aids:
                score += 15
        
        # Movement difficulty adds to mobility needs
        movement_level = row.get('movement_difficulty_level', '')
        if pd.notna(movement_level):
            difficulty = self.DIFFICULTY_MAP.get(str(movement_level).strip(), 0)
            score += difficulty * 10
        
        return min(score, 100)
    
    def calculate_composite_score(
        self, 
        self_reported_score: Optional[float],
        functional_score: float,
        affected_domain_count: int,
        education_score: float,
        mobility_score: float
    ) -> Tuple[float, Dict]:
        """Calculate weighted composite severity score"""
        
        # Start with disability baseline
        base_score = 50
        
        # Add functional domain score
        functional_contribution = functional_score * self.WEIGHTS['functional_domains']
        
        # Add affected domains count
        domain_contribution = min(affected_domain_count * 8, 30) * self.WEIGHTS['affected_domains']
        
        # Add education needs
        education_contribution = education_score * self.WEIGHTS['education_needs']
        
        # Add mobility needs
        mobility_contribution = mobility_score * self.WEIGHTS['mobility_aids']
        
        # If self-reported degree exists, use it as anchor
        if self_reported_score is not None:
            self_reported_contribution = self_reported_score * self.WEIGHTS['self_reported']
            base_score = self_reported_score * 0.5  # Start closer to self-reported
        
        composite = (
            base_score +
            functional_contribution +
            domain_contribution +
            education_contribution +
            mobility_contribution
        )
        
        factors = {
            'self_reported_contribution': self_reported_score,
            'functional_contribution': functional_score,
            'affected_domains': affected_domain_count,
            'education_contribution': education_score,
            'mobility_contribution': mobility_score,
        }
        
        return min(max(composite, 0), 100), factors
    
    def get_severity_level(self, score: float) -> str:
        """Convert numeric score to severity level"""
        for level, (low, high) in self.severity_thresholds.items():
            if low <= score < high:
                return level
        if score >= 75:
            return 'CRITICAL'
        return 'MILD'
    
    def generate_recommendations(self, level: str, factors: List[str]) -> List[str]:
        """Generate recommendations based on severity level"""
        recommendations = []
        
        if level in ['SEVERE', 'CRITICAL']:
            recommendations.extend([
                'Priority referral to specialist services',
                'Weekly therapy sessions recommended',
                'Family caregiver training essential',
                'Consider assistive device assessment',
                'Regular medical follow-up required',
            ])
        elif level == 'MODERATE':
            recommendations.extend([
                'Bi-weekly therapy sessions',
                'Individualized education plan (IEP) recommended',
                'Regular progress monitoring',
                'Parent education sessions',
            ])
        else:  # MILD
            recommendations.extend([
                'Monthly therapy check-ins',
                'Home-based intervention program',
                'School integration support',
                'Quarterly reassessment',
            ])
        
        return recommendations
    
    def assess_beneficiary(self, row: pd.Series, disability_type: str = None) -> SeverityScore:
        """
        Assess severity for a single beneficiary
        
        Args:
            row: Data row with all assessment fields
            disability_type: Type of disability if known
            
        Returns:
            SeverityScore with level, score, confidence, and reasoning
        """
        factors_used = []
        reasoning_parts = []
        
        # Get self-reported degree
        self_reported_degree = row.get('disability_degree', None)
        self_reported_score = self.normalize_severity(self_reported_degree)
        if self_reported_score is not None:
            factors_used.append(f'Self-reported degree: {self_reported_degree}')
            reasoning_parts.append(f"Self-reported severity: {self_reported_degree}")
        
        # Calculate functional score
        functional_score, affected_domains = self.calculate_functional_score(row)
        if affected_domains:
            factors_used.append(f'Functional domains affected: {len(affected_domains)} ({", ".join(affected_domains)})')
            reasoning_parts.append(f"{len(affected_domains)} functional domains affected: {', '.join(affected_domains)}")
        
        # Assess education needs
        education_score = self.assess_education_needs(row)
        if education_score > 20:
            factors_used.append(f'Education needs score: {education_score}')
        
        # Assess mobility needs
        mobility_score = self.assess_mobility_needs(row)
        if mobility_score > 20:
            factors_used.append(f'Mobility needs score: {mobility_score}')
            reasoning_parts.append(f"Mobility support required (score: {mobility_score})")
        
        # Calculate composite score
        composite_score, all_factors = self.calculate_composite_score(
            self_reported_score,
            functional_score,
            len(affected_domains),
            education_score,
            mobility_score
        )
        
        # Adjust based on disability type baseline if available
        if disability_type and isinstance(disability_type, str):
            dtype_upper = str(disability_type).upper()
            if dtype_upper in self.DISABILITY_BASELINE:
                baseline = self.DISABILITY_BASELINE[dtype_upper]
                # Blend with disability baseline
                composite_score = composite_score * 0.7 + baseline['base'] * 0.3
                reasoning_parts.append(f"Disability type baseline: {disability_type}")
        
        # Determine severity level
        level = self.get_severity_level(composite_score)
        
        # Calculate confidence
        confidence = 0.7 if self_reported_score else 0.5
        if len(affected_domains) >= 3:
            confidence += 0.15
        if education_score > 30 or mobility_score > 30:
            confidence += 0.1
        confidence = min(confidence, 0.95)
        
        # Generate reasoning
        reasoning = ". ".join(reasoning_parts) if reasoning_parts else "Assessment based on available functional data"
        
        # Generate recommendations
        recommendations = self.generate_recommendations(level, factors_used)
        
        return SeverityScore(
            level=level,
            score=round(composite_score, 1),
            confidence=round(confidence, 2),
            factors=factors_used,
            reasoning=reasoning,
            recommendations=recommendations
        )
    
    def assess_all_beneficiaries(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Assess severity for all beneficiaries in dataframe
        
        Args:
            df: DataFrame with beneficiary data
            
        Returns:
            DataFrame with added severity columns
        """
        logger.info(f"Assessing severity for {len(df)} beneficiaries...")
        
        results = []
        
        for idx, row in df.iterrows():
            disability_type = row.get('disability_type', None)
            assessment = self.assess_beneficiary(row, disability_type)
            
            results.append({
                'unique_id': row.get('unique_id', idx),
                'child_name': row.get('child_name', row.get("Child's full name", '')),
                'original_degree': row.get('disability_degree', None),
                'inferred_level': assessment.level,
                'severity_score': assessment.score,
                'confidence': assessment.confidence,
                'severity_factors': ' | '.join(assessment.factors),
                'severity_reasoning': assessment.reasoning,
                'severity_recommendations': ' | '.join(assessment.recommendations),
            })
        
        result_df = pd.DataFrame(results)
        
        # Log distribution
        distribution = result_df['inferred_level'].value_counts()
        logger.info(f"Severity distribution: {distribution.to_dict()}")
        
        return result_df
    
    def get_severity_summary(self, assessment_df: pd.DataFrame) -> Dict:
        """Generate summary statistics for severity assessments"""
        summary = {
            'total_assessed': len(assessment_df),
            'by_level': assessment_df['inferred_level'].value_counts().to_dict(),
            'average_score': round(assessment_df['severity_score'].mean(), 2),
            'average_confidence': round(assessment_df['confidence'].mean(), 2),
            'score_range': {
                'min': round(assessment_df['severity_score'].min(), 2),
                'max': round(assessment_df['severity_score'].max(), 2),
            },
            'by_disability_type': {},
            'high_priority_count': len(assessment_df[assessment_df['inferred_level'].isin(['SEVERE', 'CRITICAL'])]),
        }
        
        # Breakdown by disability type
        if 'original_degree' in assessment_df.columns:
            by_type = assessment_df.groupby('inferred_level').size().to_dict()
            summary['by_level'] = by_type
        
        return summary


def main():
    """Test the severity engine"""
    from data_processor import IRPDataProcessor
    
    # Load and process data
    processor = IRPDataProcessor("/workspace/IRP_ash&alam (5).xlsx")
    processor.process_all()
    df = processor.processed_data['merged']
    
    # Initialize engine
    engine = SeverityEngine()
    
    # Assess all beneficiaries
    results = engine.assess_all_beneficiaries(df)
    
    # Save results
    output_path = "/workspace/project/analytics/processed/severity_assessments.csv"
    results.to_csv(output_path, index=False)
    
    # Print summary
    summary = engine.get_severity_summary(results)
    print("\n" + "="*60)
    print("SEVERITY ASSESSMENT SUMMARY")
    print("="*60)
    print(f"Total Assessed: {summary['total_assessed']}")
    print(f"Average Score: {summary['average_score']}")
    print(f"Average Confidence: {summary['average_confidence']}")
    print(f"\nSeverity Distribution:")
    for level, count in summary['by_level'].items():
        print(f"  {level}: {count}")
    print(f"\nHigh Priority (Severe/Critical): {summary['high_priority_count']}")
    
    # Show sample results
    print("\nSample Results (first 5):")
    print(results[['unique_id', 'child_name', 'inferred_level', 'severity_score', 'confidence']].head().to_string())
    
    return results


if __name__ == "__main__":
    main()