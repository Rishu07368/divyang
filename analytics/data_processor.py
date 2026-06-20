"""
Disability Intelligence Platform - Data Processor
Handles Excel data ingestion, cleaning, transformation, and analysis
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IRPDataProcessor:
    """Processes IRP (Individual Rehabilitation Plan) Excel data"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.sheets = {}
        self.processed_data = {}
        
    def load_excel(self) -> Dict[str, pd.DataFrame]:
        """Load all sheets from Excel file"""
        logger.info(f"Loading Excel file: {self.file_path}")
        xl = pd.ExcelFile(self.file_path)
        
        for sheet in xl.sheet_names:
            # Load without assuming headers (sheets have dual-language headers)
            df = pd.read_excel(xl, sheet_name=sheet, header=None)
            self.sheets[sheet] = df
            logger.info(f"Loaded sheet '{sheet}': {df.shape[0]} rows x {df.shape[1]} cols")
        
        return self.sheets
    
    def clean_basic_info(self) -> pd.DataFrame:
        """Clean and standardize Basic Info sheet"""
        logger.info("Cleaning Basic Info sheet...")
        df = self.sheets['01_Basic_Info'].copy()
        
        # This sheet has dual headers (row 0: English, row 1: Hindi)
        # Get English headers from row 0
        english_headers = df.iloc[0].tolist()
        
        # Skip header rows and get data starting from row 2
        df = df.iloc[2:]
        
        # Remove rows with Hindi text in name column (header row) or empty
        df = df[df[0] != "बच्चे का पूरा नाम"]
        df = df[df[0].notna()]
        
        # Reset index
        df = df.reset_index(drop=True)
        
        # Assign English headers as column names
        df.columns = english_headers
        
        # Now rename to standard format
        column_mapping = {
            "Child's full name": 'child_name',
            'Unique ID': 'unique_id',
            'Date of Assessment': 'assessment_date',
            'Name of the Assessor': 'assessor_name',
            'Age (full year)': 'age',
            'Gender': 'gender',
            'Type of disability': 'disability_type',
            'Degree of disability': 'disability_degree',
            'Is Aadhaar available?': 'aadhaar_available',
            'Is the photo of the child attached?': 'photo_attached',
            'Age Group': 'age_group',
            'village': 'village',
            'Hamlet/ Settlement/ locality': 'hamlet',
            'Gram Panchayat': 'gram_panchayat',
            'Block': 'block',
            'Family mobile number': 'family_mobile',
            'Alternate Contact Number': 'alternate_contact',
            'Name of the Head Caregiver': 'caregiver_name',
            'Relationship with the child': 'caregiver_relationship',
            "Caregiver's Occupation": 'caregiver_occupation',
            'Does the caregiver stay with the child most of the time?': 'caregiver_stays',
            'Who decides on the education/treatment/rehabilitation of the child?': 'education_decision_maker',
            'Who takes the child to school/hospital/therapy?': 'transport_person',
            'Family type': 'family_type',
            'Social Status': 'social_status',
            'Ration Card Status': 'ration_card_status',
            'Do you have an Ayushman card?': 'ayushman_card',
            'Section 03                                                  The main reason for evaluation': 'evaluation_reason',
            'The main reason for the evaluation - other details': 'evaluation_reason_other',
            'How the problem arose': 'problem_onset',
            'Other details of the problem': 'problem_onset_other',
            'Problem Situation': 'problem_situation',
        }
        
        df = df.rename(columns=column_mapping)
        
        # Keep only columns we renamed (remove unnamed columns)
        df = df[[c for c in df.columns if c in column_mapping.values()]]
        
        # Clean age - convert to numeric
        if 'age' in df.columns:
            df['age'] = pd.to_numeric(df['age'], errors='coerce')
        
        # Clean phone numbers - remove XX placeholders
        if 'family_mobile' in df.columns:
            df['family_mobile'] = df['family_mobile'].astype(str).str.replace(r'[^0-9]', '', regex=True)
            df['family_mobile'] = df['family_mobile'].replace('', np.nan)
        
        # Standardize text columns
        for col in ['gender', 'disability_type', 'disability_degree', 'aadhaar_available']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.upper().str.strip()
        
        self.processed_data['basic_info'] = df
        logger.info(f"Basic Info cleaned: {len(df)} records")
        return df
    
    def clean_functional_assessment(self) -> pd.DataFrame:
        """Clean Functional Assessment sheet"""
        logger.info("Cleaning Functional Assessment sheet...")
        df = self.sheets['02_Functional_Assessment'].copy()
        
        # Limit columns early to avoid memory issues - keep first 50 columns
        df = df.iloc[:, :50]
        
        # Get English headers from row 0
        english_headers = df.iloc[0].tolist()
        
        # Skip header rows and get data starting from row 2
        df = df.iloc[2:]
        
        # Remove rows with Hindi text in name column or empty
        df = df[df[0] != "बच्चे का पूरा नाम"]
        df = df[df[0].notna()]
        df = df.reset_index(drop=True)
        
        # Assign English headers
        df.columns = english_headers
        
        # Key column mapping
        key_mapping = {
            "Child's full name": 'child_name',
            'Unique ID': 'unique_id',
            'Date of Assessment': 'assessment_date',
        }
        
        # Rename key columns
        df = df.rename(columns=key_mapping)
        
        self.processed_data['functional_assessment'] = df
        logger.info(f"Functional Assessment cleaned: {len(df)} records, {len(df.columns)} columns")
        return df
    
    def clean_education_schemes(self) -> pd.DataFrame:
        """Clean Education Schemes Referral sheet"""
        logger.info("Cleaning Education Schemes Referral sheet...")
        df = self.sheets['03_Education_Schemes_Referral'].copy()
        
        # Get English headers from row 0
        english_headers = df.iloc[0].tolist()
        
        # Skip header rows
        df = df.iloc[2:]
        
        # Remove rows with Hindi text or empty
        df = df[df[0] != "बच्चे का पूरा नाम"]
        df = df[df[0].notna()]
        df = df.reset_index(drop=True)
        
        # Assign English headers
        df.columns = english_headers
        
        # Key column mapping
        column_mapping = {
            "Child's full name": 'child_name',
            'Unique ID': 'unique_id',
            'Date of Assessment': 'assessment_date',
            'School Status': 'currently_studying',
            'Current Class': 'studying_class',
        }
        
        df = df.rename(columns=column_mapping)
        
        # Keep mapped columns
        df = df[[c for c in df.columns if c in column_mapping.values()]]
        
        self.processed_data['education_schemes'] = df
        logger.info(f"Education Schemes cleaned: {len(df)} records")
        return df
    
    def clean_irp_goals(self) -> pd.DataFrame:
        """Clean IRP Goals sheet"""
        logger.info("Cleaning IRP Goals sheet...")
        df = self.sheets['04_IRP_Goals'].copy()
        
        # Get English headers from row 0
        english_headers = df.iloc[0].tolist()
        
        # Skip header rows
        df = df.iloc[2:]
        
        # Remove rows with Hindi text or empty
        df = df[df[0] != "बच्चे का पूरा नाम"]
        df = df[df[0].notna()]
        df = df.reset_index(drop=True)
        
        # Assign English headers
        df.columns = english_headers
        
        # Key column mapping
        column_mapping = {
            "Child's full name": 'child_name',
            'Unique ID': 'unique_id',
            'Date of Assessment': 'assessment_date',
        }
        
        df = df.rename(columns=column_mapping)
        
        # Keep mapped columns
        df = df[[c for c in df.columns if c in column_mapping.values()]]
        
        self.processed_data['irp_goals'] = df
        logger.info(f"IRP Goals cleaned: {len(df)} records")
        return df
    
    def clean_intervention_plan(self) -> pd.DataFrame:
        """Clean Intervention Plan sheet"""
        logger.info("Cleaning Intervention Plan sheet...")
        df = self.sheets['05_Intervention_Plan'].copy()
        
        # Get English headers from row 0
        english_headers = df.iloc[0].tolist()
        
        # Skip header rows
        df = df.iloc[2:]
        
        # Remove rows with Hindi text or empty
        df = df[df[0] != "बच्चे का पूरा नाम"]
        df = df[df[0].notna()]
        df = df.reset_index(drop=True)
        
        # Assign English headers
        df.columns = english_headers
        
        # Key column mapping
        column_mapping = {
            "Child's full name": 'child_name',
            'Unique ID': 'unique_id',
            'Date of Assessment': 'assessment_date',
        }
        
        df = df.rename(columns=column_mapping)
        
        self.processed_data['intervention_plan'] = df
        logger.info(f"Intervention Plan cleaned: {len(df)} records")
        return df
    
    def merge_all_data(self) -> pd.DataFrame:
        """Merge all sheets into unified beneficiary view"""
        logger.info("Merging all data sheets...")
        
        basic = self.processed_data['basic_info'].copy()
        functional = self.processed_data['functional_assessment'].copy()
        education = self.processed_data['education_schemes'].copy()
        goals = self.processed_data['irp_goals'].copy()
        
        # Ensure unique_id is string type
        for df in [basic, functional, education, goals]:
            if 'unique_id' in df.columns:
                df['unique_id'] = df['unique_id'].astype(str).str.strip()
        
        # Drop duplicates before merge (each child should appear once per sheet)
        functional = functional.drop_duplicates(subset=['unique_id'])
        education = education.drop_duplicates(subset=['unique_id'])
        goals = goals.drop_duplicates(subset=['unique_id'])
        
        # Merge on unique_id - use 1:1 merge (basic is master)
        merged = basic.merge(functional, on='unique_id', how='left', suffixes=('', '_func'))
        merged = merged.merge(education, on='unique_id', how='left', suffixes=('', '_edu'))
        merged = merged.merge(goals, on='unique_id', how='left', suffixes=('', '_goals'))
        
        # Remove duplicate columns - filter for string columns only
        cols_to_drop = []
        for c in merged.columns:
            if isinstance(c, str):
                if c.endswith('_func') or c.endswith('_edu') or c.endswith('_goals'):
                    cols_to_drop.append(c)
        
        if cols_to_drop:
            merged = merged.drop(columns=cols_to_drop)
        
        # Drop any remaining duplicates based on unique_id
        merged = merged.drop_duplicates(subset=['unique_id'])
        
        self.processed_data['merged'] = merged
        logger.info(f"Merged data: {len(merged)} records, {len(merged.columns)} columns")
        return merged
    
    def get_summary_stats(self) -> Dict:
        """Generate summary statistics"""
        merged = self.processed_data['merged']
        
        stats = {
            'total_beneficiaries': len(merged),
            'by_gender': merged['gender'].value_counts().to_dict(),
            'by_disability_type': merged['disability_type'].value_counts().to_dict(),
            'by_disability_degree': merged['disability_degree'].value_counts().to_dict(),
            'by_age_group': merged['age_group'].value_counts().to_dict(),
            'by_village': merged['village'].value_counts().to_dict(),
            'by_block': merged['block'].value_counts().to_dict(),
            'by_social_status': merged['social_status'].value_counts().to_dict(),
            'aadhaar_available': merged['aadhaar_available'].value_counts().to_dict(),
            'ayushman_card': merged['ayushman_card'].value_counts().to_dict(),
            'currently_studying': merged['currently_studying'].value_counts().to_dict() if 'currently_studying' in merged.columns else {},
            'missing_data': {
                'age': int(merged['age'].isna().sum()),
                'disability_type': int(merged['disability_type'].isna().sum()),
                'disability_degree': int(merged['disability_degree'].isna().sum()),
                'village': int(merged['village'].isna().sum()),
                'block': int(merged['block'].isna().sum()),
            }
        }
        
        # Calculate age statistics
        stats['age_stats'] = {
            'mean': float(merged['age'].mean()) if merged['age'].notna().any() else 0,
            'median': float(merged['age'].median()) if merged['age'].notna().any() else 0,
            'min': int(merged['age'].min()) if merged['age'].notna().any() else 0,
            'max': int(merged['age'].max()) if merged['age'].notna().any() else 0,
        }
        
        return stats
    
    def to_json(self, output_path: str):
        """Export processed data to JSON"""
        with open(output_path, 'w') as f:
            json.dump(self.processed_data, f, indent=2, default=str)
        logger.info(f"Exported processed data to {output_path}")
    
    def to_csv(self, output_dir: str):
        """Export each sheet to CSV"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for name, df in self.processed_data.items():
            file_path = output_path / f"{name}.csv"
            df.to_csv(file_path, index=False)
            logger.info(f"Exported {name} to {file_path}")
    
    def get_geo_data(self) -> pd.DataFrame:
        """Get data formatted for GIS mapping"""
        merged = self.processed_data['merged']
        
        geo_data = merged[[
            'unique_id', 'child_name', 'village', 'gram_panchayat', 'block',
            'disability_type', 'disability_degree', 'age', 'gender',
            'assessment_date'
        ]].copy()
        
        geo_data = geo_data[geo_data['village'].notna()]
        
        return geo_data
    
    def process_all(self) -> Dict[str, pd.DataFrame]:
        """Run complete processing pipeline"""
        self.load_excel()
        self.clean_basic_info()
        self.clean_functional_assessment()
        self.clean_education_schemes()
        self.clean_irp_goals()
        self.clean_intervention_plan()
        self.merge_all_data()
        
        return self.processed_data


def main():
    """Main processing function"""
    file_path = "/workspace/IRP_ash&alam (5).xlsx"
    output_dir = "/workspace/project/analytics/processed"
    
    processor = IRPDataProcessor(file_path)
    processor.process_all()
    
    # Generate outputs
    processor.to_csv(output_dir)
    processor.to_json(f"{output_dir}/all_data.json")
    
    # Print summary
    stats = processor.get_summary_stats()
    print("\n" + "="*60)
    print("DATA PROCESSING SUMMARY")
    print("="*60)
    print(f"Total Beneficiaries: {stats['total_beneficiaries']}")
    print(f"\nDisability Distribution:")
    for dtype, count in stats['by_disability_type'].items():
        print(f"  {dtype}: {count}")
    print(f"\nSeverity Distribution:")
    for degree, count in stats['by_disability_degree'].items():
        print(f"  {degree}: {count}")
    print(f"\nVillage Distribution:")
    for village, count in list(stats['by_village'].items())[:5]:
        print(f"  {village}: {count}")
    print(f"\nAge Statistics: Mean={stats['age_stats']['mean']:.1f}, Median={stats['age_stats']['median']:.1f}")
    
    return processor


if __name__ == "__main__":
    main()