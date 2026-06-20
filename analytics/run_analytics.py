"""
Disability Intelligence Platform - Main Analytics Pipeline
Runs complete analysis and generates all outputs
"""

import sys
import os
from pathlib import Path

# Add analytics directory to path
sys.path.insert(0, str(Path(__file__).parent))

from data_processor import IRPDataProcessor
from severity_engine import SeverityEngine
from gis_engine import GISEngine
from welfare_engine import WelfareRecommendationEngine
from resource_allocation import ResourceAllocationEngine
from field_worker_intelligence import FieldWorkerIntelligence
from ai_insights import AIInsightsEngine

import json
import pandas as pd
import numpy as np
from datetime import datetime

def convert_numpy_types(obj):
    """Convert numpy types to native Python types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    return obj


def run_full_pipeline(excel_path: str, output_dir: str):
    """Run complete analytics pipeline"""
    
    print("="*80)
    print("DISABILITY INTELLIGENCE PLATFORM - ANALYTICS PIPELINE")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Create output directories
    output_path = Path(output_dir)
    processed_dir = output_path / "processed"
    maps_dir = output_path / "maps"
    reports_dir = output_path / "reports"
    
    for d in [processed_dir, maps_dir, reports_dir]:
        d.mkdir(parents=True, exist_ok=True)
    
    # ==================== STEP 1: DATA PROCESSING ====================
    print("STEP 1: DATA INGESTION & PROCESSING")
    print("-"*40)
    processor = IRPDataProcessor(excel_path)
    processor.process_all()
    
    # Save processed data
    processor.to_csv(processed_dir)
    processor.to_json(processed_dir / "all_data.json")
    
    df = processor.processed_data['merged']
    stats = processor.get_summary_stats()
    
    print(f"✓ Processed {stats['total_beneficiaries']} beneficiaries")
    print(f"✓ Disability types: {len(stats['by_disability_type'])}")
    print(f"✓ Villages covered: {len(stats['by_village'])}")
    print()
    
    # ==================== STEP 2: SEVERITY ASSESSMENT ====================
    print("STEP 2: SEVERITY ASSESSMENT")
    print("-"*40)
    severity_engine = SeverityEngine()
    severity_results = severity_engine.assess_all_beneficiaries(df)
    severity_results.to_csv(processed_dir / "severity_assessments.csv", index=False)
    
    severity_summary = severity_engine.get_severity_summary(severity_results)
    print(f"✓ Assessed {severity_summary['total_assessed']} beneficiaries")
    print(f"  Severity distribution: {severity_summary['by_level']}")
    print(f"  Average score: {severity_summary['average_score']}")
    print()
    
    # ==================== STEP 3: WELFARE RECOMMENDATIONS ====================
    print("STEP 3: WELFARE SCHEME RECOMMENDATIONS")
    print("-"*40)
    welfare_engine = WelfareRecommendationEngine()
    welfare_results = welfare_engine.recommend_all(df)
    welfare_results.to_csv(processed_dir / "welfare_recommendations.csv", index=False)
    
    eligible_count = welfare_results['total_eligible'].sum()
    print(f"✓ Generated recommendations for {len(welfare_results)} beneficiaries")
    print(f"  Total eligible scheme matches: {eligible_count}")
    print(f"  Without Ayushman card: {(welfare_results['has_ayushman'] == 'NO').sum()}")
    print()
    
    # ==================== STEP 4: GIS MAPPING ====================
    print("STEP 4: GIS MAP GENERATION")
    print("-"*40)
    geocode_cache = output_path / "geocode_cache.json"
    gis_engine = GISEngine(str(geocode_cache))
    maps = gis_engine.generate_all_maps(df, str(maps_dir))
    
    print(f"✓ Generated maps:")
    for name, path in maps.items():
        print(f"  • {name}")
    print()
    
    # ==================== STEP 5: RESOURCE ALLOCATION ====================
    print("STEP 5: RESOURCE ALLOCATION PLANNING")
    print("-"*40)
    resource_engine = ResourceAllocationEngine()
    zones = resource_engine.create_intervention_zones(df)
    camps = resource_engine.recommend_camp_locations(df)
    resources = resource_engine.calculate_resource_requirements(df)
    schedule = resource_engine.generate_outreach_schedule(df, available_days=20)
    
    # Save resource data
    resource_data = {
        'intervention_zones': [
            {
                'zone_id': z.zone_id,
                'name': z.name,
                'beneficiary_count': z.beneficiary_count,
                'priority_score': z.priority_score,
                'severity_distribution': z.severity_distribution,
                'recommended_interventions': z.recommended_interventions,
                'estimated_cost': z.estimated_cost,
                'impact_potential': z.impact_potential
            }
            for z in zones
        ],
        'camp_locations': [
            {
                'location_name': c.location_name,
                'village': c.village,
                'total_beneficiaries': c.total_beneficiaries,
                'nearby_villages': c.nearby_villages,
                'services_needed': c.services_needed,
                'recommended_team': c.recommended_team,
                'priority': c.priority
            }
            for c in camps
        ],
        'staff_requirements': resources['staff_requirements'],
        'service_requirements': resources['service_requirements'],
        'outreach_schedule': schedule
    }
    
    with open(processed_dir / "resource_allocation.json", 'w') as f:
        json.dump(convert_numpy_types(resource_data), f, indent=2)
    
    print(f"✓ Created {len(zones)} intervention zones")
    print(f"✓ Recommended {len(camps)} camp locations")
    print(f"✓ Generated 20-day outreach schedule")
    print()
    
    # ==================== STEP 6: FIELD WORKER INTELLIGENCE ====================
    print("STEP 6: FIELD WORKER OPTIMIZATION")
    print("-"*40)
    field_engine = FieldWorkerIntelligence()
    clusters = field_engine.create_cluster_visits(df)
    routes = field_engine.create_weekly_schedule(df, start_date="2026-06-22")
    efficiency = field_engine.analyze_travel_efficiency(routes)
    assignments = field_engine.recommend_team_assignments(df)
    
    # Save field worker data
    field_data = {
        'village_clusters': {
            village: [
                {
                    'unique_id': v.unique_id,
                    'child_name': v.child_name,
                    'priority': v.priority,
                    'severity': v.severity,
                    'visit_type': v.visit_type
                }
                for v in visits
            ]
            for village, visits in clusters.items()
        },
        'weekly_routes': [
            {
                'date': r.date,
                'visits': [
                    {
                        'unique_id': v.unique_id,
                        'child_name': v.child_name,
                        'village': v.village,
                        'priority': v.priority
                    }
                    for v in r.visits
                ],
                'total_distance_km': r.total_distance_km,
                'beneficiaries_covered': r.beneficiaries_covered,
                'efficiency': r.route_efficiency
            }
            for r in routes
        ],
        'travel_efficiency': efficiency,
        'team_assignments': assignments
    }
    
    with open(processed_dir / "field_worker_data.json", 'w') as f:
        json.dump(convert_numpy_types(field_data), f, indent=2)
    
    print(f"✓ Created {len(clusters)} village clusters")
    print(f"✓ Optimized {len(routes)}-day weekly schedule")
    print(f"  Average efficiency: {efficiency['avg_efficiency']} visits/hour")
    print(f"  Total distance: {efficiency['total_distance_km']} km")
    print()
    
    # ==================== STEP 7: AI INSIGHTS ====================
    print("STEP 7: AI INSIGHTS GENERATION")
    print("-"*40)
    insights_engine = AIInsightsEngine()
    insights = insights_engine.generate_all_insights(df)
    insights_summary = insights_engine.get_insights_summary()
    
    # Export insights report
    insights_engine.export_insights_report(reports_dir / "ai_insights_report.txt")
    
    # Save insights as JSON
    insights_json = [
        {
            'id': i.id,
            'category': i.category,
            'title': i.title,
            'description': i.description,
            'evidence': i.evidence,
            'impact_score': i.impact_score,
            'confidence': i.confidence,
            'urgency': i.urgency,
            'recommendations': i.recommendations,
            'affected_count': i.affected_count,
            'location': i.location
        }
        for i in insights
    ]
    
    with open(processed_dir / "ai_insights.json", 'w') as f:
        json.dump(convert_numpy_types(insights_json), f, indent=2)
    
    print(f"✓ Generated {insights_summary['total_insights']} actionable insights")
    print(f"  CRITICAL: {insights_summary['critical_count']}")
    print(f"  HIGH: {insights_summary['high_count']}")
    print(f"  Total affected: {insights_summary['total_affected']} beneficiaries")
    print()
    
    # ==================== GENERATE DASHBOARD DATA ====================
    print("STEP 8: DASHBOARD DATA EXPORT")
    print("-"*40)
    
    dashboard_data = {
        'summary': {
            'total_beneficiaries': stats['total_beneficiaries'],
            'last_updated': datetime.now().isoformat(),
            'by_gender': stats['by_gender'],
            'by_age_group': stats['by_age_group'],
            'by_social_status': stats['by_social_status'],
        },
        'disability_distribution': stats['by_disability_type'],
        'severity_distribution': severity_summary['by_level'],
        'village_distribution': stats['by_village'],
        'key_metrics': {
            'severity_avg_score': severity_summary['average_score'],
            'welfare_eligible_total': int(eligible_count),
            'without_ayushman': int((welfare_results['has_ayushman'] == 'NO').sum()),
            'not_in_school': int((welfare_results['in_school'] == 'NO').sum()),
            'high_priority_beneficiaries': int(severity_summary['high_priority_count']),
        },
        'resource_needs': {
            'staff': resources['staff_requirements'],
            'estimated_monthly_cost': resources['estimated_monthly_cost'],
        },
        'top_insights': insights_summary['top_insights'],
    }
    
    with open(output_path / "dashboard_data.json", 'w') as f:
        json.dump(convert_numpy_types(dashboard_data), f, indent=2)
    
    print(f"✓ Dashboard data exported to {output_path / 'dashboard_data.json'}")
    print()
    
    # ==================== COMPLETION ====================
    print("="*80)
    print("PIPELINE COMPLETE")
    print("="*80)
    print(f"Output directory: {output_dir}")
    print(f"Generated files:")
    print(f"  • Processed data: {processed_dir}")
    print(f"  • Maps: {maps_dir}")
    print(f"  • Reports: {reports_dir}")
    print(f"  • Dashboard data: {output_path / 'dashboard_data.json'}")
    print()
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return {
        'processed_data': str(processed_dir),
        'maps': maps,
        'reports': str(reports_dir),
        'dashboard_data': str(output_path / 'dashboard_data.json'),
        'summary': dashboard_data
    }


def main():
    """Main entry point"""
    excel_path = "/workspace/IRP_ash&alam (5).xlsx"
    output_dir = "/workspace/project/frontend/public/data"
    
    results = run_full_pipeline(excel_path, output_dir)
    
    return results


if __name__ == "__main__":
    main()