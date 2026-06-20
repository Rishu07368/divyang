"""
Disability Intelligence Platform - Resource Allocation Engine
Optimizes resource deployment for maximum impact
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
class InterventionZone:
    """Represents a geographic intervention zone"""
    zone_id: str
    name: str
    center_lat: float
    center_lon: float
    villages: List[str]
    beneficiary_count: int
    severity_distribution: Dict[str, int]
    priority_score: float
    recommended_interventions: List[str]
    estimated_cost: float
    impact_potential: str


@dataclass
class CampLocation:
    """Represents a recommended rehabilitation camp location"""
    location_name: str
    village: str
    lat: float
    lon: float
    nearby_villages: List[str]
    total_beneficiaries: int
    severity_breakdown: Dict[str, int]
    services_needed: List[str]
    recommended_team: List[str]
    priority: int  # 1-5, 1 being highest


class ResourceAllocationEngine:
    """
    Generates optimal resource allocation strategies:
    - Intervention zones
    - Camp locations
    - Outreach priorities
    - Educator deployment
    """
    
    # Known village coordinates
    VILLAGE_COORDS = {
        'HARIYAR': (27.5667, 81.8167),
        'BAHABAR': (27.5833, 81.8000),
        'LALAPUR': (27.5500, 81.7500),
        'BAHAPUR': (27.5700, 81.7800),
        'BRAHMPUR': (27.5800, 81.8100),
    }
    
    # Intervention service types
    SERVICE_TYPES = {
        'SPEECH AND LANGUAGE': ['speech_therapy', 'communication_aids'],
        'MUSCULAR DYSTROPHY': ['physiotherapy', 'mobility_aids', 'occupational_therapy'],
        'CEREBRAL PALSY': ['physiotherapy', 'occupational_therapy', 'special_education'],
        'INTELLECTUAL DISABILITY': ['special_education', 'behavior_therapy', 'life_skills'],
        'HEARING IMPAIRMENT': ['audiology', 'sign_language', 'hearing_aids'],
        'VISUAL IMPAIRMENT': ['orientation_mobility', 'braille_training', 'assistive_devices'],
        'MULTIPLE DISABILITIES': ['multidisciplinary_team', 'comprehensive_rehab'],
    }
    
    def __init__(self):
        self.severity_weights = {
            'CRITICAL': 4,
            'SEVERE': 3,
            'MODERATE': 2,
            'MILD': 1,
            'UNKNOWN': 1,
        }
    
    def calculate_village_priority(self, village_df: pd.DataFrame) -> float:
        """Calculate priority score for a village based on beneficiary needs"""
        if len(village_df) == 0:
            return 0
        
        score = 0
        
        # Severity weighting (primary factor)
        severity_sum = 0
        for _, row in village_df.iterrows():
            degree = str(row.get('disability_degree', 'UNKNOWN')).upper().strip()
            severity_sum += self.severity_weights.get(degree, 1)
        score += severity_sum * 10
        
        # Population factor (logarithmic - larger villages get diminishing returns)
        pop = len(village_df)
        score += np.log1p(pop) * 5
        
        # Gap factor - beneficiaries not currently receiving interventions
        gap_count = 0
        for _, row in village_df.iterrows():
            interventions = str(row.get('field', ''))
            if pd.isna(interventions) or len(str(interventions)) < 5:
                gap_count += 1
        score += (gap_count / max(len(village_df), 1)) * 20
        
        # Education gap
        not_studying = 0
        for _, row in village_df.iterrows():
            studying = str(row.get('currently_studying', ''))
            if 'NO' in studying.upper():
                not_studying += 1
        score += (not_studying / max(len(village_df), 1)) * 15
        
        return min(score, 100)
    
    def create_intervention_zones(self, df: pd.DataFrame, max_zone_size: int = 50) -> List[InterventionZone]:
        """
        Create intervention zones based on geographic clustering
        """
        logger.info(f"Creating intervention zones for {len(df)} beneficiaries...")
        
        # Group by village
        village_groups = df.groupby('village')
        
        zones = []
        zone_counter = 1
        
        for village, group in village_groups:
            if pd.isna(village):
                continue
            
            # Get village coordinates
            village_upper = str(village).upper().strip()
            coords = self.VILLAGE_COORDS.get(village_upper, (27.57, 81.80))
            
            # Calculate severity distribution
            severity_dist = {}
            for degree in ['CRITICAL', 'SEVERE', 'MODERATE', 'MILD', 'UNKNOWN']:
                count = (group['disability_degree'].str.upper().str.strip() == degree).sum()
                if count > 0:
                    severity_dist[degree] = count
            
            # Calculate priority
            priority = self.calculate_village_priority(group)
            
            # Determine recommended interventions based on disability types
            interventions = set()
            for dtype in group['disability_type'].dropna().unique():
                dtype_upper = str(dtype).upper()
                for key, services in self.SERVICE_TYPES.items():
                    if key in dtype_upper:
                        interventions.update(services)
            
            # Estimate cost based on beneficiary count and severity
            base_cost = len(group) * 500  # ₹500 per beneficiary
            severity_multiplier = sum(
                self.severity_weights.get(s, 1) * c 
                for s, c in severity_dist.items()
            ) / max(len(group), 1)
            estimated_cost = base_cost * (1 + severity_multiplier * 0.2)
            
            zone = InterventionZone(
                zone_id=f"ZONE_{zone_counter:03d}",
                name=f"Zone {village}",
                center_lat=coords[0],
                center_lon=coords[1],
                villages=[village],
                beneficiary_count=len(group),
                severity_distribution=severity_dist,
                priority_score=round(priority, 2),
                recommended_interventions=list(interventions),
                estimated_cost=round(estimated_cost, 2),
                impact_potential="High" if priority > 60 else "Medium" if priority > 30 else "Low"
            )
            zones.append(zone)
            zone_counter += 1
        
        # Sort by priority
        zones.sort(key=lambda z: z.priority_score, reverse=True)
        
        logger.info(f"Created {len(zones)} intervention zones")
        return zones
    
    def recommend_camp_locations(self, df: pd.DataFrame, max_camp_distance: float = 10.0) -> List[CampLocation]:
        """
        Recommend optimal locations for rehabilitation camps
        """
        logger.info("Recommending camp locations...")
        
        # Get unique villages with coordinates
        villages = df.groupby('village').agg({
            'unique_id': 'count',
            'disability_degree': lambda x: x.value_counts().to_dict(),
        }).reset_index()
        
        villages.columns = ['village', 'count', 'severity_dist']
        
        # Calculate village priority scores
        village_priorities = []
        for _, row in villages.iterrows():
            if pd.isna(row['village']):
                continue
            
            village_upper = str(row['village']).upper().strip()
            coords = self.VILLAGE_COORDS.get(village_upper, (27.57, 81.80))
            
            severity_score = sum(
                self.severity_weights.get(s, 1) * c 
                for s, c in row['severity_dist'].items()
            )
            
            priority_score = row['count'] * 5 + severity_score * 10
            
            village_priorities.append({
                'village': row['village'],
                'count': row['count'],
                'severity_dist': row['severity_dist'],
                'lat': coords[0],
                'lon': coords[1],
                'priority_score': priority_score
            })
        
        # Sort by priority and select camp locations
        village_priorities.sort(key=lambda x: x['priority_score'], reverse=True)
        
        camps = []
        selected_villages = set()
        camp_counter = 1
        
        for vp in village_priorities:
            if vp['village'] in selected_villages:
                continue
            
            if vp['count'] < 3:  # Minimum beneficiaries for camp
                continue
            
            # Find nearby villages
            nearby = []
            for other in village_priorities:
                if other['village'] == vp['village']:
                    continue
                
                dist = self._haversine_distance(
                    vp['lat'], vp['lon'],
                    other['lat'], other['lon']
                )
                
                if dist <= max_camp_distance:
                    nearby.append(other['village'])
                    selected_villages.add(other['village'])
            
            # Determine services needed
            services_needed = set()
            for other_name in [vp['village']] + nearby:
                village_data = df[df['village'] == other_name]
                for dtype in village_data['disability_type'].dropna().unique():
                    dtype_upper = str(dtype).upper()
                    for key, services in self.SERVICE_TYPES.items():
                        if key in dtype_upper:
                            services_needed.update(services)
            
            # Determine recommended team
            team = []
            if 'speech_therapy' in services_needed:
                team.append('Speech Therapist')
            if 'physiotherapy' in services_needed:
                team.append('Physiotherapist')
            if 'special_education' in services_needed:
                team.append('Special Educator')
            if 'audiology' in services_needed:
                team.append('Audiologist')
            team.append('CBR Worker')
            
            # Calculate total beneficiaries
            total = vp['count']
            for other_name in nearby:
                other_data = df[df['village'] == other_name]
                total += len(other_data)
            
            camp = CampLocation(
                location_name=f"Camp {camp_counter}",
                village=vp['village'],
                lat=vp['lat'],
                lon=vp['lon'],
                nearby_villages=nearby,
                total_beneficiaries=total,
                severity_breakdown=vp['severity_dist'],
                services_needed=list(services_needed),
                recommended_team=team,
                priority=camp_counter
            )
            camps.append(camp)
            camp_counter += 1
            selected_villages.add(vp['village'])
            
            if camp_counter > 5:  # Limit to top 5 camps
                break
        
        logger.info(f"Recommended {len(camps)} camp locations")
        return camps
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in km"""
        R = 6371  # Earth's radius in km
        
        lat1_rad = np.radians(lat1)
        lat2_rad = np.radians(lat2)
        delta_lat = np.radians(lat2 - lat1)
        delta_lon = np.radians(lon2 - lon1)
        
        a = np.sin(delta_lat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(delta_lon/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        
        return R * c
    
    def generate_outreach_schedule(self, df: pd.DataFrame, available_days: int = 20) -> List[Dict]:
        """
        Generate weekly outreach schedule for field workers
        """
        zones = self.create_intervention_zones(df)
        
        schedule = []
        day = 1
        
        for zone in zones:
            if day > available_days:
                break
            
            # Determine visits needed based on severity
            critical_visits = zone.severity_distribution.get('CRITICAL', 0)
            severe_visits = zone.severity_distribution.get('SEVERE', 0)
            
            visits_needed = min(
                critical_visits * 2 + severe_visits,
                3  # Max visits per zone per month
            )
            
            for visit_num in range(visits_needed):
                if day > available_days:
                    break
                
                schedule.append({
                    'day': day,
                    'week': (day - 1) // 5 + 1,
                    'zone_id': zone.zone_id,
                    'village': zone.name.replace('Zone ', ''),
                    'priority': 'HIGH' if critical_visits > 0 else 'MEDIUM',
                    'beneficiaries': zone.beneficiary_count,
                    'services': ', '.join(zone.recommended_interventions[:3]),
                    'estimated_time_hours': min(zone.beneficiary_count * 0.5, 6)
                })
                day += 1
        
        return schedule
    
    def calculate_resource_requirements(self, df: pd.DataFrame) -> Dict:
        """Calculate total resource requirements"""
        
        total = len(df)
        
        # By disability type
        by_disability = df['disability_type'].value_counts().to_dict()
        
        # By severity
        by_severity = df['disability_degree'].value_counts().to_dict()
        
        # Service requirements
        service_needs = defaultdict(int)
        for _, row in df.iterrows():
            dtype = str(row.get('disability_type', '')).upper()
            for key, services in self.SERVICE_TYPES.items():
                if key in dtype:
                    for service in services:
                        service_needs[service] += 1
        
        # Educator requirements
        # Rough estimate: 1 special educator per 15 beneficiaries
        special_edu_needed = max(1, int(np.ceil(total / 15)))
        
        # Physiotherapist requirements
        # 1 physiotherapist per 20 mobility-affected beneficiaries
        mobility_disabilities = ['MUSCULAR DYSTROPHY', 'CEREBRAL PALSY']
        mobility_count = sum(
            by_disability.get(d, 0) 
            for d in mobility_disabilities
        )
        physio_needed = max(1, int(np.ceil(mobility_count / 20)))
        
        # Speech therapist requirements
        speech_count = by_disability.get('SPEECH AND LANGUAGE', 0)
        speech_needed = max(1, int(np.ceil(speech_count / 25)))
        
        # CBR Worker requirements
        # 1 CBR worker per 30 beneficiaries in rural areas
        cbr_needed = max(1, int(np.ceil(total / 30)))
        
        return {
            'total_beneficiaries': total,
            'by_disability_type': by_disability,
            'by_severity': by_severity,
            'service_requirements': dict(service_needs),
            'staff_requirements': {
                'special_educators': special_edu_needed,
                'physiotherapists': physio_needed,
                'speech_therapists': speech_needed,
                'cbr_workers': cbr_needed,
            },
            'estimated_monthly_cost': {
                'staff_salaries': (special_edu_needed * 25000 + 
                                   physio_needed * 30000 + 
                                   speech_needed * 28000 + 
                                   cbr_needed * 20000),
                'travel_allowance': cbr_needed * 5000,
                'materials': total * 200,
                'total': 0  # Calculate below
            }
        }


def main():
    """Test the resource allocation engine"""
    from data_processor import IRPDataProcessor
    
    # Load and process data
    processor = IRPDataProcessor("/workspace/IRP_ash&alam (5).xlsx")
    processor.process_all()
    df = processor.processed_data['merged']
    
    # Initialize engine
    engine = ResourceAllocationEngine()
    
    # Generate intervention zones
    print("\n" + "="*60)
    print("INTERVENTION ZONES")
    print("="*60)
    zones = engine.create_intervention_zones(df)
    for zone in zones[:5]:
        print(f"\n{zone.zone_id}: {zone.name}")
        print(f"  Beneficiaries: {zone.beneficiary_count}")
        print(f"  Priority: {zone.priority_score}")
        print(f"  Severity: {zone.severity_distribution}")
        print(f"  Interventions: {zone.recommended_interventions[:3]}")
        print(f"  Estimated Cost: ₹{zone.estimated_cost:,.0f}")
    
    # Recommend camp locations
    print("\n" + "="*60)
    print("RECOMMENDED CAMP LOCATIONS")
    print("="*60)
    camps = engine.recommend_camp_locations(df)
    for camp in camps:
        print(f"\n{camp.location_name}: {camp.village}")
        print(f"  Total Beneficiaries: {camp.total_beneficiaries}")
        print(f"  Nearby Villages: {camp.nearby_villages[:3]}")
        print(f"  Services Needed: {camp.services_needed[:3]}")
        print(f"  Team: {camp.recommended_team}")
    
    # Resource requirements
    print("\n" + "="*60)
    print("RESOURCE REQUIREMENTS")
    print("="*60)
    resources = engine.calculate_resource_requirements(df)
    print(f"Total Beneficiaries: {resources['total_beneficiaries']}")
    print(f"\nStaff Requirements:")
    for role, count in resources['staff_requirements'].items():
        print(f"  {role}: {count}")
    print(f"\nService Requirements:")
    for service, count in sorted(resources['service_requirements'].items(), key=lambda x: -x[1])[:5]:
        print(f"  {service}: {count}")
    
    # Outreach schedule
    print("\n" + "="*60)
    print("SAMPLE OUTREACH SCHEDULE (First 10 days)")
    print("="*60)
    schedule = engine.generate_outreach_schedule(df, available_days=10)
    for entry in schedule[:10]:
        print(f"Day {entry['day']}: {entry['village']} ({entry['priority']}) - {entry['beneficiaries']} beneficiaries")
    
    return zones, camps, resources, schedule


if __name__ == "__main__":
    main()