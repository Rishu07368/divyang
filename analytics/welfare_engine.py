"""
Disability Intelligence Platform - Welfare Recommendation Engine
Matches beneficiaries with eligible government welfare schemes
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Scheme:
    """Represents a welfare scheme"""
    name: str
    agency: str  # Central/State/NGO
    description: str
    benefits: List[str]
    eligibility_criteria: Dict
    required_documents: List[str]
    application_url: str
    category: str  # financial, education, healthcare, assistive, etc.


@dataclass
class Recommendation:
    """Represents a welfare scheme recommendation"""
    scheme: Scheme
    eligibility_score: float  # 0-100 how well they match
    is_eligible: bool
    missing_requirements: List[str]
    reasoning: str


class WelfareSchemeDatabase:
    """Database of government welfare schemes for persons with disabilities"""
    
    def __init__(self):
        self.schemes = self._load_schemes()
    
    def _load_schemes(self) -> List[Scheme]:
        """Load comprehensive list of disability welfare schemes"""
        schemes = []
        
        # ==================== CENTRAL GOVERNMENT SCHEMES ====================
        
        schemes.append(Scheme(
            name="Disability Pension Scheme (NIRTH)",
            agency="Central Government",
            description="Monthly pension for persons with severe disabilities",
            benefits=["Monthly pension of ₹300-500", "State-specific variations"],
            eligibility_criteria={
                "disability_type": ["any"],
                "disability_degree": ["SEVERE", "CRITICAL"],
                "age_min": 18,
                "age_max": 99,
                "income_ceiling": 24000,  # Annual family income
            },
            required_documents=["Aadhaar Card", "Disability Certificate", "Bank Account", "Income Certificate"],
            application_url="https://www.nirth.res.in",
            category="financial"
        ))
        
        schemes.append(Scheme(
            name="ADIP (Assistance to Disabled Persons) Scheme",
            agency="Central Government - Ministry of Social Justice",
            description="Free distribution of aids and appliances to persons with disabilities",
            benefits=["Free wheelchairs", "Crutches", "Hearing aids", "Artificial limbs", "Spectacles"],
            eligibility_criteria={
                "disability_type": ["any"],
                "disability_degree": ["MILD", "MODERATE", "SEVERE", "CRITICAL"],
                "age_min": 0,
                "age_max": 99,
                "income_ceiling": 20000,  # Monthly family income
            },
            required_documents=["Aadhaar Card", "Disability Certificate", "Income Certificate", "Passport Photo"],
            application_url="https://www.swavlambancard.gov.in",
            category="assistive"
        ))
        
        schemes.append(Scheme(
            name="National Overseas Scholarship",
            agency="Central Government",
            description="Scholarship for students with 40% disability for abroad studies",
            benefits=["Full tuition fees", "Living allowance", "Travel grant"],
            eligibility_criteria={
                "disability_type": ["any"],
                "disability_degree": ["MILD", "MODERATE", "SEVERE", "CRITICAL"],
                "age_min": 0,
                "age_max": 35,
                "education_min": "12th",
            },
            required_documents=["Disability Certificate", "Academic Records", "Income Certificate", "Passport"],
            application_url="https://www.socialjustice.nic.in",
            category="education"
        ))
        
        schemes.append(Scheme(
            name="Scholarship for Students with Disabilities",
            agency="Central Government",
            description="Pre-matric and post-matric scholarships for disabled students",
            benefits=["₹500-1200 per month (pre-matric)", "₹750-1600 per month (post-matric)"],
            eligibility_criteria={
                "disability_type": ["any"],
                "disability_degree": ["MILD", "MODERATE", "SEVERE", "CRITICAL"],
                "age_min": 0,
                "age_max": 40,
                "education_min": "5th",
                "income_ceiling": 250000,  # Annual family income
            },
            required_documents=["Disability Certificate", "Aadhaar Card", "Bank Account", "School/College Certificate", "Income Certificate"],
            application_url="https://www.nationalscholarships.gov.in",
            category="education"
        ))
        
        schemes.append(Scheme(
            name="Pradhan Mantri Disability Pension Scheme",
            agency="Central Government",
            description="Direct benefit transfer for persons with severe disabilities",
            benefits=["₹300-500 per month", "Direct bank transfer"],
            eligibility_criteria={
                "disability_type": ["any"],
                "disability_degree": ["SEVERE", "CRITICAL"],
                "age_min": 18,
                "age_max": 79,
                "income_ceiling": 24000,
            },
            required_documents=["Aadhaar Card", "Disability Certificate (40%+)", "Bank Account", "Jan Aadhaar/Income Certificate"],
            application_url="https://pmdps.nic.in",
            category="financial"
        ))
        
        schemes.append(Scheme(
            name="Sanjay Gandhi Niryatam Card",
            agency="Central Government - Ministry of Railways",
            description="Concessional railway travel for persons with disabilities",
            benefits=["50% concession on train tickets", "Free sleeper class for attendant"],
            eligibility_criteria={
                "disability_type": ["any"],
                "disability_degree": ["SEVERE", "CRITICAL"],
                "age_min": 0,
                "age_max": 99,
            },
            required_documents=["Disability Certificate", "Passport Photo", "Aadhaar Card"],
            application_url="https://www.irctc.co.in",
            category="transport"
        ))
        
        schemes.append(Scheme(
            name="Health Insurance for Differently Abled",
            agency="Ayushman Bharat - Central",
            description="Free health coverage under PMJAY for eligible families",
            benefits=["₹5 lakh coverage per family", "Cashless treatment", "Pre and post hospitalization"],
            eligibility_criteria={
                "disability_type": ["any"],
                "disability_degree": ["MILD", "MODERATE", "SEVERE", "CRITICAL"],
                "age_min": 0,
                "age_max": 99,
                "ayushman_eligible": True,  # Based on SECC data
            },
            required_documents=["Aadhaar Card", "Ayushman Card/Ration Card", "Disability Certificate"],
            application_url="https://pmjay.gov.in",
            category="healthcare"
        ))
        
        # ==================== UTTAR PRADESH STATE SCHEMES ====================
        
        schemes.append(Scheme(
            name="Uttar Pradesh Disability Pension",
            agency="Uttar Pradesh Government",
            description="State-funded monthly pension for persons with disabilities",
            benefits=["₹500-1000 per month", "Quarterly payment"],
            eligibility_criteria={
                "disability_type": ["any"],
                "disability_degree": ["SEVERE", "CRITICAL"],
                "age_min": 18,
                "age_max": 99,
                "state": "Uttar Pradesh",
                "income_ceiling": 48000,
            },
            required_documents=["Aadhaar Card", "Disability Certificate (40%+)", "Bank Account", "Residence Certificate", "Income Certificate"],
            application_url="https://sspy-up.gov.in",
            category="financial"
        ))
        
        schemes.append(Scheme(
            name="UP Free Education Scheme for Disabled",
            agency="Uttar Pradesh Government",
            description="Free education from class 1 to PhD for persons with disabilities",
            benefits=["Free education", "Free books", "Free uniform", "Scholarship for higher studies"],
            eligibility_criteria={
                "disability_type": ["any"],
                "disability_degree": ["MILD", "MODERATE", "SEVERE", "CRITICAL"],
                "age_min": 5,
                "age_max": 35,
                "state": "Uttar Pradesh",
                "education_min": "None",
            },
            required_documents=["Disability Certificate", "Aadhaar Card", "Domicile Certificate", "School/College Admission Proof"],
            application_url="https://up.gov.in",
            category="education"
        ))
        
        schemes.append(Scheme(
            name="UP Assistive Device Distribution",
            agency="Uttar Pradesh Government",
            description="Free distribution of wheelchairs, hearing aids, and other aids",
            benefits=["Free wheelchair", "Hearing aid", "Calliper/Braces", "White cane"],
            eligibility_criteria={
                "disability_type": ["any"],
                "disability_degree": ["SEVERE", "CRITICAL", "MODERATE"],
                "age_min": 0,
                "age_max": 99,
                "state": "Uttar Pradesh",
            },
            required_documents=["Disability Certificate", "Aadhaar Card", "Passport Photo", "Bank Account"],
            application_url="https://up.gov.in",
            category="assistive"
        ))
        
        schemes.append(Scheme(
            name="UP Marriage Incentive Scheme for Disabled",
            agency="Uttar Pradesh Government",
            description="Financial assistance for marriage of persons with disabilities",
            benefits=["₹20,000-70,000 one-time grant"],
            eligibility_criteria={
                "disability_type": ["any"],
                "disability_degree": ["MILD", "MODERATE", "SEVERE", "CRITICAL"],
                "age_min": 18,
                "age_max": 60,
                "state": "Uttar Pradesh",
                "income_ceiling": 72000,
            },
            required_documents=["Disability Certificate", "Aadhaar Card", "Marriage Certificate", "Bank Account"],
            application_url="https://up.gov.in",
            category="social"
        ))
        
        schemes.append(Scheme(
            name="UP Self-Employment Scheme for Disabled",
            agency="Uttar Pradesh Government",
            description="Loan assistance and training for self-employment",
            benefits=["Skill training", "Loan subsidy up to ₹50,000", "Business development support"],
            eligibility_criteria={
                "disability_type": ["any"],
                "disability_degree": ["MILD", "MODERATE", "SEVERE", "CRITICAL"],
                "age_min": 18,
                "age_max": 50,
                "state": "Uttar Pradesh",
            },
            required_documents=["Disability Certificate", "Aadhaar Card", "Bank Account", "Business Plan"],
            application_url="https://up.gov.in",
            category="employment"
        ))
        
        schemes.append(Scheme(
            name="UP Transport Concession",
            agency="Uttar Pradesh Transport Department",
            description="Free or discounted bus travel for persons with disabilities",
            benefits=["Free bus travel within UP", "50% concession on inter-state buses"],
            eligibility_criteria={
                "disability_type": ["any"],
                "disability_degree": ["SEVERE", "CRITICAL"],
                "age_min": 0,
                "age_max": 99,
                "state": "Uttar Pradesh",
            },
            required_documents=["Disability Certificate", "Aadhaar Card", "Passport Photo"],
            application_url="https://up.gov.in",
            category="transport"
        ))
        
        # ==================== NGO/OTHER SCHEMES ====================
        
        schemes.append(Scheme(
            name="NHFDC (National Handicapped Finance) Scholarship",
            agency="NHFDC - Government Enterprise",
            description="Educational loans and scholarships for disabled students",
            benefits=["Scholarship up to ₹2 lakh", "Concessional loans"],
            eligibility_criteria={
                "disability_type": ["any"],
                "disability_degree": ["MILD", "MODERATE", "SEVERE", "CRITICAL"],
                "age_min": 0,
                "age_max": 32,
                "education_min": "10th",
            },
            required_documents=["Disability Certificate", "Academic Records", "Income Certificate", "Aadhaar Card"],
            application_url="https://www.nhfdc.nic.in",
            category="education"
        ))
        
        schemes.append(Scheme(
            name="State Disability Commissioner Fund",
            agency="State Disability Commissioner",
            description="Emergency assistance and medical support fund",
            benefits=["One-time grant up to ₹10,000", "Medical assistance"],
            eligibility_criteria={
                "disability_type": ["any"],
                "disability_degree": ["SEVERE", "CRITICAL"],
                "age_min": 0,
                "age_max": 99,
            },
            required_documents=["Disability Certificate", "Aadhaar Card", "Medical Recommendation", "Income Proof"],
            application_url="https://www.upcomdis.nic.in",
            category="emergency"
        ))
        
        return schemes
    
    def get_schemes_by_category(self, category: str) -> List[Scheme]:
        """Get schemes filtered by category"""
        return [s for s in self.schemes if s.category == category]
    
    def get_all_schemes(self) -> List[Scheme]:
        """Get all available schemes"""
        return self.schemes


class WelfareRecommendationEngine:
    """
    Matches beneficiaries with eligible welfare schemes
    """
    
    def __init__(self):
        self.scheme_db = WelfareSchemeDatabase()
    
    def check_eligibility(self, beneficiary: pd.Series, scheme: Scheme) -> Tuple[bool, float, List[str]]:
        """
        Check if a beneficiary is eligible for a scheme
        
        Returns:
            (is_eligible, eligibility_score, missing_requirements)
        """
        criteria = scheme.eligibility_criteria
        missing = []
        score = 100  # Start with perfect score
        
        # Check disability type
        if 'disability_type' in criteria:
            if 'any' not in criteria['disability_type']:
                disability = str(beneficiary.get('disability_type', '')).upper()
                if not any(dt in disability for dt in criteria['disability_type']):
                    missing.append(f"Disability type not eligible: {disability}")
                    score -= 50
        
        # Check disability degree
        if 'disability_degree' in criteria:
            degree = str(beneficiary.get('disability_degree', '')).upper()
            if degree not in criteria['disability_degree']:
                missing.append(f"Severity level not eligible: {degree}")
                score -= 40
        
        # Check age
        if 'age_min' in criteria:
            age = beneficiary.get('age')
            if pd.notna(age):
                if float(age) < criteria['age_min']:
                    missing.append(f"Age below minimum: {age} years")
                    score -= 30
        if 'age_max' in criteria:
            age = beneficiary.get('age')
            if pd.notna(age):
                if float(age) > criteria['age_max']:
                    missing.append(f"Age above maximum: {age} years")
                    score -= 30
        
        # Check income ceiling
        if 'income_ceiling' in criteria:
            # Check if beneficiary has Ayushman card (indicates low income)
            ayushman = str(beneficiary.get('ayushman_card', '')).upper()
            ration_status = str(beneficiary.get('ration_card_status', '')).upper()
            
            if 'YES' not in ayushman and 'ELIGIBLE' not in ration_status:
                missing.append("Income eligibility unclear (no Ayushman card or eligible ration card)")
                score -= 20
        
        # Check state
        if 'state' in criteria:
            block = str(beneficiary.get('block', '')).upper()
            if 'UP' not in block and 'UTTAR' not in block:
                missing.append("State eligibility: Only Uttar Pradesh")
                score -= 25
        
        # Check education
        if 'education_min' in criteria:
            education = str(beneficiary.get('currently_studying', '')).upper()
            school_class = str(beneficiary.get('studying_class', ''))
            if criteria['education_min'] != 'None':
                if 'NO' in education and 'STUDYING' in education:
                    missing.append("Currently not studying, may not meet education criteria")
                    score -= 15
        
        # Check Aadhaar
        aadhaar = str(beneficiary.get('aadhaar_available', '')).upper()
        if 'YES' not in aadhaar:
            missing.append("Aadhaar card required for application")
            score -= 15
        
        is_eligible = score >= 50 and len(missing) < 3
        
        return is_eligible, max(0, score), missing
    
    def recommend_schemes(self, beneficiary: pd.Series, max_results: int = 5) -> List[Recommendation]:
        """
        Generate scheme recommendations for a beneficiary
        
        Args:
            beneficiary: Row from processed beneficiary data
            max_results: Maximum number of recommendations
            
        Returns:
            List of Recommendation objects
        """
        recommendations = []
        
        for scheme in self.scheme_db.get_all_schemes():
            is_eligible, score, missing = self.check_eligibility(beneficiary, scheme)
            
            # Generate reasoning
            if is_eligible:
                reasoning = f"✓ Eligible for {scheme.name}. {scheme.description}"
            else:
                reasoning = f"⚠ Partial eligibility for {scheme.name}. {', '.join(missing[:2])}"
            
            recommendations.append(Recommendation(
                scheme=scheme,
                eligibility_score=score,
                is_eligible=is_eligible,
                missing_requirements=missing,
                reasoning=reasoning
            ))
        
        # Sort by eligibility score
        recommendations.sort(key=lambda x: (x.is_eligible, x.eligibility_score), reverse=True)
        
        return recommendations[:max_results]
    
    def get_critical_gaps(self, beneficiary: pd.Series) -> Dict:
        """
        Identify critical welfare gaps for a beneficiary
        """
        gaps = {
            'missing_aadhaar': False,
            'missing_disability_certificate': False,
            'no_ayushman_card': False,
            'not_in_school': False,
            'no_mobile_contact': False,
            'severe_without_interventions': False,
        }
        
        aadhaar = str(beneficiary.get('aadhaar_available', '')).upper()
        if 'YES' not in aadhaar and 'NO' in aadhaar:
            gaps['missing_aadhaar'] = True
        
        ayushman = str(beneficiary.get('ayushman_card', '')).upper()
        if 'YES' not in ayushman:
            gaps['no_ayushman_card'] = True
        
        studying = str(beneficiary.get('currently_studying', '')).upper()
        if 'NO' in studying and 'NOT' in studying:
            gaps['not_in_school'] = True
        
        mobile = str(beneficiary.get('family_mobile', ''))
        if pd.isna(mobile) or len(mobile) < 10:
            gaps['no_mobile_contact'] = True
        
        degree = str(beneficiary.get('disability_degree', '')).upper()
        if degree in ['SEVERE', 'CRITICAL']:
            interventions = str(beneficiary.get('field', ''))
            if pd.isna(interventions) or len(interventions) < 5:
                gaps['severe_without_interventions'] = True
        
        return gaps
    
    def recommend_all(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate recommendations for all beneficiaries"""
        logger.info(f"Generating welfare recommendations for {len(df)} beneficiaries...")
        
        results = []
        
        for idx, row in df.iterrows():
            beneficiary_id = row.get('unique_id', f'row_{idx}')
            child_name = row.get('child_name', row.get("Child's full name", 'Unknown'))
            
            recs = self.recommend_schemes(row, max_results=5)
            
            # Get top eligible schemes
            eligible = [r for r in recs if r.is_eligible]
            
            # Identify gaps
            gaps = self.get_critical_gaps(row)
            
            results.append({
                'unique_id': beneficiary_id,
                'child_name': child_name,
                'disability_type': row.get('disability_type'),
                'disability_degree': row.get('disability_degree'),
                'recommended_schemes': '; '.join([r.scheme.name for r in eligible[:3]]),
                'total_eligible': len(eligible),
                'total_potentially_eligible': len(recs),
                'primary_scheme': eligible[0].scheme.name if eligible else 'None',
                'primary_scheme_category': eligible[0].scheme.category if eligible else None,
                'has_aadhaar': 'YES' if not gaps['missing_aadhaar'] else 'NO',
                'has_ayushman': 'NO' if gaps['no_ayushman_card'] else 'YES',
                'in_school': 'NO' if gaps['not_in_school'] else 'YES',
                'has_contact': 'NO' if gaps['no_mobile_contact'] else 'YES',
                'critical_gaps': ', '.join([k for k, v in gaps.items() if v]) if any(gaps.values()) else 'None',
                'recommendation_json': {
                    'eligible': [{'name': r.scheme.name, 'category': r.scheme.category} for r in eligible],
                    'potentially_eligible': [{'name': r.scheme.name, 'score': r.eligibility_score} for r in recs if not r.is_eligible],
                    'gaps': gaps
                }
            })
        
        result_df = pd.DataFrame(results)
        
        # Summary statistics
        logger.info(f"Recommendations generated. Eligible scheme distribution:")
        eligible_counts = result_df['total_eligible'].value_counts().head()
        for count, num_beneficiaries in eligible_counts.items():
            logger.info(f"  {count} schemes: {num_beneficiaries} beneficiaries")
        
        return result_df


def main():
    """Test the welfare recommendation engine"""
    from data_processor import IRPDataProcessor
    
    # Load and process data
    processor = IRPDataProcessor("/workspace/IRP_ash&alam (5).xlsx")
    processor.process_all()
    df = processor.processed_data['merged']
    
    # Initialize engine
    engine = WelfareRecommendationEngine()
    
    # Generate recommendations
    results = engine.recommend_all(df)
    
    # Save results
    output_path = "/workspace/project/analytics/processed/welfare_recommendations.csv"
    results.to_csv(output_path, index=False)
    
    # Print summary
    print("\n" + "="*60)
    print("WELFARE RECOMMENDATION SUMMARY")
    print("="*60)
    print(f"Total Beneficiaries: {len(results)}")
    print(f"Average Schemes Eligible: {results['total_eligible'].mean():.1f}")
    print(f"Without Aadhaar: {(results['has_aadhaar'] == 'NO').sum()}")
    print(f"Without Ayushman: {(results['has_ayushman'] == 'NO').sum()}")
    print(f"Not in School: {(results['in_school'] == 'NO').sum()}")
    print(f"Has Critical Gaps: {(results['critical_gaps'] != 'None').sum()}")
    
    # Show top recommendations
    print("\nTop Recommended Schemes:")
    top_schemes = results['primary_scheme'].value_counts().head(5)
    for scheme, count in top_schemes.items():
        print(f"  {scheme}: {count} beneficiaries")
    
    # Show sample
    print("\nSample Recommendations (first 3):")
    sample = results[['unique_id', 'child_name', 'primary_scheme', 'total_eligible']].head(3)
    print(sample.to_string())
    
    return results


if __name__ == "__main__":
    main()