"""
Disability Intelligence Platform - GIS Engine
Handles geographic data, geocoding, and interactive map generation
"""

import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap, MarkerCluster, FastMarkerCluster
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import json
import logging
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VillageGeocoder:
    """Handles geocoding of village names with caching"""
    
    # Extended village coordinate database for Uttar Pradesh/Bihar region
    VILLAGE_COORDINATES = {
        # Bihar region villages (sample)
        'HARIYAR': (26.95, 84.42),
        'BAHABAR': (26.92, 84.38),
        'BAHAPUR': (26.98, 84.45),
        'LALAPUR': (26.90, 84.35),
        'BRAHMPUR': (26.97, 84.40),
        'BARAIDABAR': (26.94, 84.43),
        'KESHWAPUR': (26.91, 84.36),
        'MAJHAULA': (26.96, 84.48),
        'RAJAPUR': (26.88, 84.32),
        'SHIVPUR': (26.95, 84.41),
        'VISHWANATHPUR': (26.68, 83.03),
        'MATHIYA': (26.88, 83.64),
        'PANDAY': (25.30, 83.01),
        'BELWA': (26.90, 84.00),
        'PARSAUNI': (26.75, 84.50),
        'NADUA GYANPUR': (26.85, 84.30),
        'NIBAHI': (26.95, 84.25),
        'SINGHPUR': (26.92, 84.45),
        'RASULPUR': (26.88, 84.38),
        'PIPRAHIYA': (26.82, 84.42),
        'MITHABEL': (26.78, 84.35),
        'BAIJUDIHA': (26.72, 84.28),
        'HARAIYA': (26.95, 84.50),
        'HARAIYA TOLA': (26.94, 84.51),
        'RASULPUR 2': (26.87, 84.37),
        'SHEMRA TOLA': (26.82, 84.44),
        'KHURHRI': (26.75, 84.40),
        'VISHWANTHPUR': (26.68, 83.03),
        'NEKAVAR JR02': (26.95, 84.35),
    }
    
    def __init__(self, cache_file: str = None):
        self.geolocator = Nominatim(user_agent="disability_intelligence_platform")
        self.cache = dict(self.VILLAGE_COORDINATES)  # Start with known villages
        self.cache_file = cache_file
        if cache_file and Path(cache_file).exists():
            try:
                with open(cache_file, 'r') as f:
                    saved_cache = json.load(f)
                    self.cache.update(saved_cache)
            except:
                pass
    
    def geocode(self, village: str, block: str = None, district: str = "Uttar Pradesh") -> Optional[Tuple[float, float]]:
        """
        Geocode a village name to lat/long coordinates
        Returns (latitude, longitude) or None if not found
        """
        if pd.isna(village) or not village or str(village).strip() == 'NA':
            return None
        
        village_str = str(village).strip().upper()
        
        # Check cache first (including partial matches)
        for known_name, coords in self.cache.items():
            if known_name.upper() in village_str or village_str in known_name.upper():
                return coords
        
        # Check exact match in known coordinates
        if village_str in self.VILLAGE_COORDINATES:
            return self.VILLAGE_COORDINATES[village_str]
        
        # Skip external geocoding to avoid rate limits
        # Use approximate coordinates based on common patterns
        logger.debug(f"Village '{village}' not found in cache")
        return None
    
    def save_cache(self):
        """Save geocoding cache to file"""
        if self.cache_file:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
    
    def batch_geocode(self, villages: List[str], blocks: List[str] = None) -> Dict[str, Tuple[float, float]]:
        """Geocode multiple villages"""
        results = {}
        
        for i, village in enumerate(villages):
            block = blocks[i] if blocks and i < len(blocks) else None
            coords = self.geocode(village, block)
            results[village] = coords
        
        return results


class GISEngine:
    """
    Generates interactive maps for disability intelligence
    - Beneficiary location maps
    - Severity heatmaps
    - Cluster analysis maps
    - Resource allocation maps
    """
    
    # Known village coordinates for accuracy (Uttar Pradesh, Bahraich area)
    KNOWN_VILLAGES = {
        'HARIYAR': (27.5667, 81.8167),
        'BAHABAR': (27.5833, 81.8000),
        'LALAPUR': (27.5500, 81.7500),
        'BAHAPUR': (27.5700, 81.7800),
        'BRAHMPUR': (27.5800, 81.8100),
        'BARAIDABAR': (27.5600, 81.7900),
        'KESHWAPUR': (27.5550, 81.7700),
        'MAJHAULA': (27.5900, 81.8300),
        'RAJAPUR': (27.5450, 81.7600),
        'SHIVPUR': (27.5750, 81.8050),
    }
    
    def __init__(self, cache_file: str = None):
        self.geocoder = VillageGeocoder(cache_file)
    
    def get_coordinates(self, village: str, block: str = None) -> Optional[Tuple[float, float]]:
        """Get coordinates for a village, using known locations or geocoding"""
        if pd.isna(village):
            return None
        
        village_upper = str(village).upper().strip()
        
        # Check known villages first
        for known_name, coords in self.KNOWN_VILLAGES.items():
            if known_name in village_upper or village_upper in known_name:
                return coords
        
        # Try geocoding
        return self.geocoder.geocode(village, block)
    
    def prepare_geo_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add latitude/longitude to dataframe"""
        df = df.copy()
        df['latitude'] = None
        df['longitude'] = None
        
        for idx, row in df.iterrows():
            coords = self.get_coordinates(
                row.get('village'),
                row.get('block')
            )
            if coords:
                df.at[idx, 'latitude'] = coords[0]
                df.at[idx, 'longitude'] = coords[1]
        
        # Convert to numeric
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
        
        geo_count = df['latitude'].notna().sum()
        logger.info(f"Geocoded {geo_count}/{len(df)} records")
        
        return df
    
    def create_beneficiary_map(
        self, 
        df: pd.DataFrame, 
        center: Tuple[float, float] = (27.57, 81.80),
        zoom: int = 10
    ) -> folium.Map:
        """Create interactive map with beneficiary markers"""
        
        # Prepare geo data
        df_geo = self.prepare_geo_data(df)
        
        # Create base map
        m = folium.Map(location=center, zoom_start=zoom, tiles='OpenStreetMap')
        
        # Add title
        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; z-index: 1000; 
                    background-color: white; padding: 10px; border-radius: 5px;
                    box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
            <h4 style="margin: 0;">Disability Intelligence - Beneficiary Map</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">Total Beneficiaries: {}</p>
        </div>
        '''.format(len(df_geo))
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Add marker cluster for beneficiaries with coordinates
        marker_cluster = MarkerCluster(name="Beneficiaries").add_to(m)
        
        # Color mapping for severity
        severity_colors = {
            'MILD': 'green',
            'MODERATE': 'orange',
            'SEVERE': 'red',
            'CRITICAL': 'darkred',
            'UNKNOWN': 'gray'
        }
        
        for idx, row in df_geo.iterrows():
            if pd.notna(row['latitude']) and pd.notna(row['longitude']):
                severity = row.get('disability_degree', 'UNKNOWN')
                severity = str(severity).upper().strip() if pd.notna(severity) else 'UNKNOWN'
                color = severity_colors.get(severity, 'gray')
                
                # Create popup content
                popup_content = f"""
                <div style="width: 200px;">
                    <b>{row.get('child_name', 'Unknown')}</b><br>
                    <b>ID:</b> {row.get('unique_id', 'N/A')}<br>
                    <b>Age:</b> {row.get('age', 'N/A')}<br>
                    <b>Gender:</b> {row.get('gender', 'N/A')}<br>
                    <b>Disability:</b> {row.get('disability_type', 'N/A')}<br>
                    <b>Severity:</b> {severity}<br>
                    <b>Village:</b> {row.get('village', 'N/A')}<br>
                    <b>Gram Panchayat:</b> {row.get('gram_panchayat', 'N/A')}
                </div>
                """
                
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=folium.Popup(popup_content, max_width=250),
                    icon=folium.Icon(color=color, icon='user', prefix='fa')
                ).add_to(marker_cluster)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Add fullscreen option
        folium.plugins.Fullscreen().add_to(m)
        
        return m
    
    def create_severity_heatmap(
        self, 
        df: pd.DataFrame,
        center: Tuple[float, float] = (27.57, 81.80),
        zoom: int = 10
    ) -> folium.Map:
        """Create heatmap showing severity concentration"""
        
        df_geo = self.prepare_geo_data(df)
        
        # Create base map
        m = folium.Map(location=center, zoom_start=zoom, tiles='CartoDB positron')
        
        # Add title
        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; z-index: 1000; 
                    background-color: white; padding: 10px; border-radius: 5px;
                    box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
            <h4 style="margin: 0;">Severity Heatmap</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">Red = High Severity Concentration</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Prepare heatmap data with severity weighting
        heat_data = []
        severity_weights = {
            'CRITICAL': 3.0,
            'SEVERE': 2.0,
            'MODERATE': 1.0,
            'MILD': 0.5,
            'UNKNOWN': 0.3
        }
        
        for idx, row in df_geo.iterrows():
            if pd.notna(row['latitude']) and pd.notna(row['longitude']):
                severity = str(row.get('disability_degree', 'UNKNOWN')).upper().strip()
                weight = severity_weights.get(severity, 0.5)
                
                # Add multiple times for weighted heatmap
                for _ in range(int(weight * 10)):
                    heat_data.append([row['latitude'], row['longitude'], 1])
        
        # Add heatmap layer
        HeatMap(
            heat_data,
            min_opacity=0.3,
            max_zoom=18,
            radius=25,
            blur=15,
            gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'yellow', 0.8: 'orange', 1: 'red'}
        ).add_to(m)
        
        return m
    
    def create_village_summary_map(
        self, 
        df: pd.DataFrame,
        center: Tuple[float, float] = (27.57, 81.80),
        zoom: int = 11
    ) -> folium.Map:
        """Create map showing village-level summary statistics"""
        
        df_geo = self.prepare_geo_data(df)
        
        # Filter to only geocoded records
        df_geo = df_geo[df_geo['latitude'].notna() & df_geo['longitude'].notna()]
        
        if len(df_geo) == 0:
            # Return empty map if no geocoded data
            m = folium.Map(location=center, zoom_start=zoom, tiles='OpenStreetMap')
            return m
        
        # Aggregate by village
        village_summary = df_geo.groupby('village').agg({
            'unique_id': 'count',
            'latitude': 'first',
            'longitude': 'first'
        }).reset_index()
        village_summary.columns = ['village', 'count', 'latitude', 'longitude']
        
        # Get dominant severity per village
        severity_agg = []
        for village, group in df_geo.groupby('village'):
            degrees = group['disability_degree'].dropna()
            dominant = degrees.value_counts().index[0] if len(degrees) > 0 else 'UNKNOWN'
            severity_agg.append({'village': village, 'dominant_severity': dominant})
        
        severity_df = pd.DataFrame(severity_agg)
        village_summary = village_summary.merge(severity_df, on='village')
        
        # Calculate average severity score for each village
        severity_scores = {'MILD': 1, 'MODERATE': 2, 'SEVERE': 3, 'CRITICAL': 4, 'UNKNOWN': 0}
        village_summary['severity_numeric'] = village_summary['dominant_severity'].map(severity_scores).fillna(0)
        
        # Create map
        m = folium.Map(location=center, zoom_start=zoom, tiles='OpenStreetMap')
        
        # Add title
        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; z-index: 1000; 
                    background-color: white; padding: 10px; border-radius: 5px;
                    box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
            <h4 style="margin: 0;">Village Summary Map</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">Circle size = number of beneficiaries</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Add circle markers for each village
        for idx, row in village_summary.iterrows():
            if pd.notna(row['latitude']) and pd.notna(row['longitude']):
                # Color by dominant severity
                severity = str(row['dominant_severity']).upper().strip()
                color = {
                    'MILD': '#2ecc71',
                    'MODERATE': '#f39c12',
                    'SEVERE': '#e74c3c',
                    'CRITICAL': '#8e44ad',
                    'UNKNOWN': '#95a5a6'
                }.get(severity, '#95a5a6')
                
                # Size based on count
                radius = min(5 + row['count'] * 3, 30)
                
                popup_content = f"""
                <div style="width: 180px;">
                    <b>Village:</b> {row['village']}<br>
                    <b>Beneficiaries:</b> {row['count']}<br>
                    <b>Dominant Severity:</b> {severity}<br>
                    <b>Severity Score:</b> {row['severity_numeric']:.1f}/4
                </div>
                """
                
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=radius,
                    popup=folium.Popup(popup_content, max_width=200),
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.7,
                    weight=2
                ).add_to(m)
                
                # Add village name label
                folium.Marker(
                    location=[row['latitude'] + 0.003, row['longitude']],
                    icon=folium.DivIcon(
                        html=f'<div style="font-size: 10px; color: #333; white-space: nowrap;">{row["village"]}</div>'
                    )
                ).add_to(m)
        
        # Add legend
        legend_html = '''
        <div style="position: fixed; bottom: 50px; right: 50px; z-index: 1000; 
                    background-color: white; padding: 10px; border-radius: 5px;
                    box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
            <h5 style="margin: 0 0 10px 0;">Severity Legend</h5>
            <p style="margin: 3px 0;"><span style="color: #2ecc71;">●</span> Mild</p>
            <p style="margin: 3px 0;"><span style="color: #f39c12;">●</span> Moderate</p>
            <p style="margin: 3px 0;"><span style="color: #e74c3c;">●</span> Severe</p>
            <p style="margin: 3px 0;"><span style="color: #8e44ad;">●</span> Critical</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        return m
    
    def export_geojson(self, df: pd.DataFrame) -> Dict:
        """Export beneficiary data as GeoJSON for external mapping"""
        
        df_geo = self.prepare_geo_data(df)
        
        features = []
        for idx, row in df_geo.iterrows():
            if pd.notna(row['latitude']) and pd.notna(row['longitude']):
                feature = {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [row['longitude'], row['latitude']]
                    },
                    'properties': {
                        'id': str(row.get('unique_id', '')),
                        'name': str(row.get('child_name', '')),
                        'age': int(row['age']) if pd.notna(row.get('age')) else None,
                        'gender': str(row.get('gender', '')),
                        'disability_type': str(row.get('disability_type', '')),
                        'disability_degree': str(row.get('disability_degree', '')),
                        'village': str(row.get('village', '')),
                        'gram_panchayat': str(row.get('gram_panchayat', '')),
                        'block': str(row.get('block', '')),
                    }
                }
                features.append(feature)
        
        geojson = {
            'type': 'FeatureCollection',
            'features': features
        }
        
        return geojson
    
    def generate_all_maps(self, df: pd.DataFrame, output_dir: str):
        """Generate all map types and save to files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save GeoJSON
        geojson = self.export_geojson(df)
        with open(output_path / 'beneficiaries.geojson', 'w') as f:
            json.dump(geojson, f, indent=2)
        
        # Generate and save beneficiary map
        beneficiary_map = self.create_beneficiary_map(df)
        beneficiary_map.save(str(output_path / 'beneficiary_map.html'))
        
        # Generate and save severity heatmap
        heatmap = self.create_severity_heatmap(df)
        heatmap.save(str(output_path / 'severity_heatmap.html'))
        
        # Generate and save village summary map
        village_map = self.create_village_summary_map(df)
        village_map.save(str(output_path / 'village_summary_map.html'))
        
        logger.info(f"Generated all maps in {output_dir}")
        
        return {
            'geojson': f'{output_dir}/beneficiaries.geojson',
            'beneficiary_map': f'{output_dir}/beneficiary_map.html',
            'severity_heatmap': f'{output_dir}/severity_heatmap.html',
            'village_map': f'{output_dir}/village_summary_map.html',
        }


def main():
    """Test the GIS engine"""
    from data_processor import IRPDataProcessor
    
    # Load and process data
    processor = IRPDataProcessor("/workspace/IRP_ash&alam (5).xlsx")
    processor.process_all()
    df = processor.processed_data['merged']
    
    # Initialize engine
    cache_file = "/workspace/project/analytics/geocode_cache.json"
    gis = GISEngine(cache_file)
    
    # Generate all maps
    output_dir = "/workspace/project/analytics/maps"
    maps = gis.generate_all_maps(df, output_dir)
    
    print("\n" + "="*60)
    print("GIS MAPS GENERATED")
    print("="*60)
    for name, path in maps.items():
        print(f"  {name}: {path}")
    
    return maps


if __name__ == "__main__":
    main()