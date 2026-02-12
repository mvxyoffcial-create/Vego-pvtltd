import googlemaps
from app.config import settings
from typing import Tuple, Optional

class GoogleMapsService:
    def __init__(self):
        self.gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
    
    def calculate_distance(self, origin_lat: float, origin_lng: float, 
                          dest_lat: float, dest_lng: float) -> Tuple[float, float]:
        """
        Calculate distance between two points
        Returns: (distance_in_km, distance_in_meters)
        """
        try:
            origin = f"{origin_lat},{origin_lng}"
            destination = f"{dest_lat},{dest_lng}"
            
            result = self.gmaps.distance_matrix(
                origins=origin,
                destinations=destination,
                mode="driving"
            )
            
            if result['rows'][0]['elements'][0]['status'] == 'OK':
                distance_meters = result['rows'][0]['elements'][0]['distance']['value']
                distance_km = distance_meters / 1000
                return distance_km, distance_meters
            else:
                # Fallback to haversine formula
                return self._haversine_distance(origin_lat, origin_lng, dest_lat, dest_lng)
        except Exception as e:
            print(f"Error calculating distance: {e}")
            # Fallback to haversine formula
            return self._haversine_distance(origin_lat, origin_lng, dest_lat, dest_lng)
    
    def _haversine_distance(self, lat1: float, lon1: float, 
                           lat2: float, lon2: float) -> Tuple[float, float]:
        """
        Calculate distance using Haversine formula
        Returns: (distance_in_km, distance_in_meters)
        """
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lon = radians(lon2 - lon1)
        
        a = sin(delta_lat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        distance_km = R * c
        distance_meters = distance_km * 1000
        
        return distance_km, distance_meters
    
    def get_address_from_coords(self, lat: float, lng: float) -> Optional[str]:
        """Get formatted address from coordinates"""
        try:
            result = self.gmaps.reverse_geocode((lat, lng))
            if result:
                return result[0]['formatted_address']
        except Exception as e:
            print(f"Error getting address: {e}")
        return None

maps_service = GoogleMapsService()
