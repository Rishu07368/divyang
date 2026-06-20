"""
Disability Intelligence Platform - Field Worker Intelligence
Optimizes field worker routes, visit planning, and travel efficiency
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
class VisitPlan:
    """Represents a single beneficiary visit plan"""
    unique_id: str
    child_name: str
    village: str
    priority: str  # HIGH, MEDIUM, LOW
    severity: str
    visit_type: str  # INITIAL, FOLLOWUP, URGENT
    estimated_duration_minutes: int
    location_lat: float
    location_lon: float
    special_requirements: List[str]


@dataclass
class DailyRoute:
    """Represents a daily route for a field worker"""
    date: str
    visits: List[VisitPlan]
    total_distance_km: float
    total_duration_hours: float
    villages_covered: int
    beneficiaries_covered: int
    route_efficiency: float  # beneficiaries per hour


class FieldWorkerIntelligence:
    """
    Optimizes field worker operations:
    - Route optimization
    - Daily visit plans
    - Cluster visits
    - Travel efficiency analysis
    """
    
    # Known village coordinates (Uttar Pradesh, Bahraich area)
    VILLAGE_COORDS = {
        'HARIYAR': (27.5667, 81.8167),
        'BAHABAR': (27.5833, 81.8000),
        'BAHAPUR': (27.5700, 81.7800),
        'LALAPUR': (27.5500, 81.7500),
        'BRAHMPUR': (27.5800, 81.8100),
        'BARAIDABAR': (27.5600, 81.7900),
        'KESHWAPUR': (27.5550, 81.7700),
        'MAJHAULA': (27.5900, 81.8300),
        'RAJAPUR': (27.5450, 81.7600),
        'SHIVPUR': (27.5750, 81.8050),
    }
    
    # Average travel speed in km/h for rural areas
    AVG_TRAVEL_SPEED = 20
    
    # Visit duration estimates (minutes)
    VISIT_DURATIONS = {
        'CRITICAL': 60,
        'SEVERE': 45,
        'MODERATE': 30,
        'MILD': 20,
        'UNKNOWN': 30,
    }
    
    def __init__(self):
        self.severity_priority = {
            'CRITICAL': 1,
            'SEVERE': 2,
            'MODERATE': 3,
            'MILD': 4,
            'UNKNOWN': 5,
        }
    
    def get_coordinates(self, village: str) -> Tuple[float, float]:
        """Get coordinates for a village"""
        if pd.isna(village):
            return (27.57, 81.80)  # Default center
        
        village_upper = str(village).upper().strip()
        
        for known_name, coords in self.VILLAGE_COORDS.items():
            if known_name in village_upper or village_upper in known_name:
                return coords
        
        # Default coordinates
        return (27.57, 81.80)
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in km using Haversine formula"""
        R = 6371  # Earth's radius in km
        
        lat1_rad = np.radians(lat1)
        lat2_rad = np.radians(lat2)
        delta_lat = np.radians(lat2 - lat1)
        delta_lon = np.radians(lon2 - lon1)
        
        a = np.sin(delta_lat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(delta_lon/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        
        return R * c
    
    def create_visit_plan(self, row: pd.Series, priority_override: str = None) -> VisitPlan:
        """Create a visit plan for a single beneficiary"""
        village = row.get('village', 'Unknown')
        coords = self.get_coordinates(village)
        
        severity = str(row.get('disability_degree', 'UNKNOWN')).upper().strip()
        
        # Determine priority
        if priority_override:
            priority = priority_override
        elif severity == 'CRITICAL':
            priority = 'HIGH'
        elif severity == 'SEVERE':
            priority = 'HIGH'
        elif severity == 'MODERATE':
            priority = 'MEDIUM'
        else:
            priority = 'LOW'
        
        # Determine visit type
        interventions = str(row.get('field', ''))
        if pd.isna(interventions) or len(interventions) < 5:
            visit_type = 'INITIAL'
        else:
            visit_type = 'FOLLOWUP'
        
        # Check for urgent needs
        problem_situation = str(row.get('problem_situation', '')).upper()
        if 'INCREASING' in problem_situation or 'WORSE' in problem_situation:
            visit_type = 'URGENT'
            priority = 'HIGH'
        
        # Determine special requirements
        special_reqs = []
        disability_type = str(row.get('disability_type', '')).upper()
        
        if 'SPEECH' in disability_type:
            special_reqs.append('Speech therapy equipment')
        if 'MUSCULAR' in disability_type or 'CEREBRAL' in disability_type:
            special_reqs.append('Physiotherapy kit')
        if 'HEARING' in disability_type:
            special_reqs.append('Audio equipment')
        
        return VisitPlan(
            unique_id=str(row.get('unique_id', '')),
            child_name=str(row.get('child_name', 'Unknown')),
            village=str(village),
            priority=priority,
            severity=severity,
            visit_type=visit_type,
            estimated_duration_minutes=self.VISIT_DURATIONS.get(severity, 30),
            location_lat=coords[0],
            location_lon=coords[1],
            special_requirements=special_reqs
        )
    
    def optimize_route(self, visits: List[VisitPlan], start_coords: Tuple[float, float] = None) -> List[VisitPlan]:
        """
        Optimize route using nearest neighbor heuristic
        Returns visits ordered for optimal travel
        """
        if not visits:
            return []
        
        if start_coords is None:
            start_coords = (27.57, 81.80)  # Default start
        
        optimized = []
        remaining = visits.copy()
        current_pos = start_coords
        
        while remaining:
            # Find nearest unvisited location
            best_idx = 0
            best_dist = float('inf')
            
            for i, visit in enumerate(remaining):
                dist = self.calculate_distance(
                    current_pos[0], current_pos[1],
                    visit.location_lat, visit.location_lon
                )
                if dist < best_dist:
                    best_dist = dist
                    best_idx = i
            
            # Move to best location
            next_visit = remaining.pop(best_idx)
            optimized.append(next_visit)
            current_pos = (next_visit.location_lat, next_visit.location_lon)
        
        return optimized
    
    def create_daily_route(
        self, 
        beneficiaries: pd.DataFrame, 
        date: str,
        max_visits: int = 8,
        max_hours: float = 6.0
    ) -> DailyRoute:
        """Create optimized daily route for field worker"""
        
        # Create visit plans
        visit_plans = []
        for _, row in beneficiaries.iterrows():
            plan = self.create_visit_plan(row)
            visit_plans.append(plan)
        
        # Sort by priority first
        priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        visit_plans.sort(key=lambda x: priority_order.get(x.priority, 3))
        
        # Limit visits based on time
        total_time = sum(v.estimated_duration_minutes for v in visit_plans[:max_visits])
        travel_time_estimate = len(visit_plans[:max_visits]) * 10  # 10 min per travel
        
        while total_time + travel_time_estimate > max_hours * 60 and len(visit_plans) > max_visits - 2:
            max_visits -= 1
            total_time = sum(v.estimated_duration_minutes for v in visit_plans[:max_visits])
        
        selected_visits = visit_plans[:max_visits]
        
        # Optimize route
        optimized_visits = self.optimize_route(selected_visits)
        
        # Calculate total distance
        total_distance = 0
        current_pos = (27.57, 81.80)  # Starting point
        
        for visit in optimized_visits:
            dist = self.calculate_distance(
                current_pos[0], current_pos[1],
                visit.location_lat, visit.location_lon
            )
            total_distance += dist
            current_pos = (visit.location_lat, visit.location_lon)
        
        # Calculate total duration
        travel_time = total_distance / self.AVG_TRAVEL_SPEED * 60  # in minutes
        visit_time = sum(v.estimated_duration_minutes for v in optimized_visits)
        total_duration = (travel_time + visit_time) / 60  # in hours
        
        # Count villages
        villages = set(v.village for v in optimized_visits)
        
        return DailyRoute(
            date=date,
            visits=optimized_visits,
            total_distance_km=round(total_distance, 2),
            total_duration_hours=round(total_duration, 2),
            villages_covered=len(villages),
            beneficiaries_covered=len(optimized_visits),
            route_efficiency=round(len(optimized_visits) / max(total_duration, 0.1), 2)
        )
    
    def create_weekly_schedule(
        self, 
        df: pd.DataFrame, 
        start_date: str = "2026-06-22",
        days_per_week: int = 5
    ) -> List[DailyRoute]:
        """Create weekly schedule with daily routes"""
        from datetime import datetime, timedelta
        
        routes = []
        current_date = datetime.strptime(start_date, "%Y-%m-%d")
        
        # Sort beneficiaries by priority
        df_sorted = df.copy()
        severity_order = {'CRITICAL': 0, 'SEVERE': 1, 'MODERATE': 2, 'MILD': 3, 'UNKNOWN': 4}
        df_sorted['severity_order'] = df_sorted['disability_degree'].map(severity_order).fillna(5)
        df_sorted = df_sorted.sort_values('severity_order').reset_index(drop=True)
        
        # Split into groups using pandas instead of numpy
        group_size = max(1, len(df_sorted) // days_per_week)
        beneficiary_groups = []
        for i in range(0, len(df_sorted), group_size):
            group = df_sorted.iloc[i:i + group_size]
            if len(group) > 0:
                beneficiary_groups.append(group)
        
        for i in range(min(days_per_week, len(beneficiary_groups))):
            group = beneficiary_groups[i]
            if len(group) == 0:
                continue
            
            date_str = current_date.strftime("%Y-%m-%d")
            daily_route = self.create_daily_route(
                group,
                date_str,
                max_visits=8,
                max_hours=6.0
            )
            routes.append(daily_route)
            
            current_date += timedelta(days=1)
            # Skip weekends
            if current_date.weekday() == 5:  # Saturday
                current_date += timedelta(days=2)
        
        return routes
    
    def create_cluster_visits(self, df: pd.DataFrame) -> Dict[str, List[VisitPlan]]:
        """Group beneficiaries into cluster visits by village"""
        clusters = defaultdict(list)
        
        for _, row in df.iterrows():
            village = row.get('village', 'Unknown')
            plan = self.create_visit_plan(row)
            clusters[str(village)].append(plan)
        
        # Sort each cluster by priority
        for village in clusters:
            priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
            clusters[village].sort(key=lambda x: priority_order.get(x.priority, 3))
        
        return dict(clusters)
    
    def analyze_travel_efficiency(self, routes: List[DailyRoute]) -> Dict:
        """Analyze travel efficiency metrics"""
        if not routes:
            return {}
        
        total_distance = sum(r.total_distance_km for r in routes)
        total_visits = sum(r.beneficiaries_covered for r in routes)
        total_duration = sum(r.total_duration_hours for r in routes)
        total_villages = sum(r.villages_covered for r in routes)
        
        return {
            'total_days': len(routes),
            'total_distance_km': round(total_distance, 2),
            'total_visits': total_visits,
            'total_villages': total_villages,
            'avg_distance_per_day': round(total_distance / len(routes), 2),
            'avg_visits_per_day': round(total_visits / len(routes), 2),
            'avg_efficiency': round(total_visits / max(total_duration, 0.1), 2),  # visits per hour
            'distance_per_visit': round(total_distance / max(total_visits, 1), 2),
            'villages_per_day': round(total_villages / len(routes), 2),
        }
    
    def recommend_team_assignments(self, df: pd.DataFrame) -> List[Dict]:
        """Recommend field worker team assignments based on beneficiary distribution"""
        
        # Group by village
        village_groups = df.groupby('village').agg({
            'unique_id': 'count',
            'disability_degree': lambda x: x.value_counts().to_dict(),
        }).reset_index()
        
        assignments = []
        
        # Sort villages by total beneficiaries and severity
        village_groups['severity_score'] = village_groups['disability_degree'].apply(
            lambda x: sum(
                {'CRITICAL': 4, 'SEVERE': 3, 'MODERATE': 2, 'MILD': 1}.get(s, 0) * c 
                for s, c in x.items()
            )
        )
        village_groups = village_groups.sort_values('severity_score', ascending=False)
        
        # Assign workers to high-priority areas
        current_worker = 1
        for _, row in village_groups.iterrows():
            severity = row['disability_degree']
            critical = severity.get('CRITICAL', 0)
            severe = severity.get('SEVERE', 0)
            
            # More workers for higher severity
            workers_needed = 1
            if critical >= 3 or severe >= 5:
                workers_needed = 2
            if critical >= 6 or severe >= 10:
                workers_needed = 3
            
            assignments.append({
                'worker_id': f"WORKER_{current_worker}",
                'assigned_villages': [row['village']],
                'beneficiaries': row['unique_id'],
                'critical_count': critical,
                'severe_count': severe,
                'workers_assigned': workers_needed,
                'priority': 'HIGH' if critical > 0 or severe > 3 else 'MEDIUM' if severe > 0 else 'LOW',
            })
            
            current_worker += 1
        
        return assignments
    
    def generate_route_summary(self, routes: List[DailyRoute]) -> str:
        """Generate human-readable route summary"""
        summary_lines = []
        
        summary_lines.append("=" * 60)
        summary_lines.append("FIELD WORKER ROUTE SUMMARY")
        summary_lines.append("=" * 60)
        
        efficiency = self.analyze_travel_efficiency(routes)
        
        summary_lines.append(f"\nTotal Days: {efficiency['total_days']}")
        summary_lines.append(f"Total Distance: {efficiency['total_distance_km']} km")
        summary_lines.append(f"Total Beneficiaries: {efficiency['total_visits']}")
        summary_lines.append(f"Total Villages: {efficiency['total_villages']}")
        summary_lines.append(f"Average Efficiency: {efficiency['avg_efficiency']} visits/hour")
        
        summary_lines.append("\n" + "-" * 60)
        summary_lines.append("DAILY BREAKDOWN")
        summary_lines.append("-" * 60)
        
        for route in routes:
            summary_lines.append(f"\n📅 {route.date}")
            summary_lines.append(f"   Villages: {route.villages_covered} | Beneficiaries: {route.beneficiaries_covered}")
            summary_lines.append(f"   Distance: {route.total_distance_km} km | Duration: {route.total_duration_hours} hrs")
            summary_lines.append(f"   Efficiency: {route.route_efficiency} visits/hr")
            
            high_priority = [v for v in route.visits if v.priority == 'HIGH']
            if high_priority:
                summary_lines.append(f"   HIGH PRIORITY: {len(high_priority)} beneficiaries")
        
        return "\n".join(summary_lines)


def main():
    """Test the field worker intelligence module"""
    from data_processor import IRPDataProcessor
    
    # Load and process data
    processor = IRPDataProcessor("/workspace/IRP_ash&alam (5).xlsx")
    processor.process_all()
    df = processor.processed_data['merged']
    
    # Initialize engine
    engine = FieldWorkerIntelligence()
    
    # Create cluster visits
    print("\n" + "="*60)
    print("CLUSTER VISITS BY VILLAGE")
    print("="*60)
    clusters = engine.create_cluster_visits(df)
    
    for village, visits in list(clusters.items())[:5]:
        high = sum(1 for v in visits if v.priority == 'HIGH')
        print(f"\n{village}: {len(visits)} beneficiaries ({high} HIGH priority)")
    
    # Create weekly schedule
    print("\n" + "="*60)
    print("WEEKLY SCHEDULE")
    print("="*60)
    routes = engine.create_weekly_schedule(df, start_date="2026-06-22")
    
    for route in routes:
        print(f"\n{route.date}:")
        print(f"  Villages: {route.villages_covered} | Beneficiaries: {route.beneficiaries_covered}")
        print(f"  Distance: {route.total_distance_km} km | Duration: {route.total_duration_hours} hrs")
        for visit in route.visits[:3]:
            print(f"    - {visit.child_name} ({visit.village}) - {visit.priority} priority")
    
    # Analyze efficiency
    print("\n" + "="*60)
    print("TRAVEL EFFICIENCY ANALYSIS")
    print("="*60)
    efficiency = engine.analyze_travel_efficiency(routes)
    for metric, value in efficiency.items():
        print(f"  {metric}: {value}")
    
    # Team assignments
    print("\n" + "="*60)
    print("TEAM ASSIGNMENT RECOMMENDATIONS")
    print("="*60)
    assignments = engine.recommend_team_assignments(df)
    for assignment in assignments[:5]:
        print(f"\n{assignment['worker_id']}: {assignment['assigned_villages'][0]}")
        print(f"  Beneficiaries: {assignment['beneficiaries']} | Priority: {assignment['priority']}")
        print(f"  Workers needed: {assignment['workers_assigned']}")
    
    # Generate summary
    summary = engine.generate_route_summary(routes)
    print("\n" + summary)
    
    return routes, efficiency, assignments


if __name__ == "__main__":
    main()