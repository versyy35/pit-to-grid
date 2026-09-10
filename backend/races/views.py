from django.db.models import Sum
from .circuit_mapping import get_circuit_file
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView


from .models import Race, Session, Lap, PitStop, Result
from .serializers import RaceSerializer, LapSerializer, PitStopSerializer, ResultSerializer


class RaceListView(generics.ListAPIView):
    """GET /api/races/  -- optionally filter with ?season=2023"""
    serializer_class = RaceSerializer

    def get_queryset(self):
        qs = Race.objects.select_related('season').all()
        season = self.request.query_params.get('season')
        if season:
            qs = qs.filter(season__year=season)
        return qs


def _get_session_or_none(race_id, session_type):
    return Session.objects.filter(race_id=race_id, session_type=session_type).first()


class RaceLapsView(APIView):
    """GET /api/races/<race_id>/laps/?session=R (default R)"""

    def get(self, request, race_id):
        session_type = request.query_params.get('session', 'R')
        session_obj = _get_session_or_none(race_id, session_type)
        if session_obj is None:
            return Response({'detail': 'Session not found.'}, status=404)
        laps = Lap.objects.filter(session=session_obj).select_related('driver')
        return Response(LapSerializer(laps, many=True).data)


class RacePitStopsView(APIView):
    """GET /api/races/<race_id>/pitstops/?session=R (default R)"""

    def get(self, request, race_id):
        session_type = request.query_params.get('session', 'R')
        session_obj = _get_session_or_none(race_id, session_type)
        if session_obj is None:
            return Response({'detail': 'Session not found.'}, status=404)
        pit_stops = PitStop.objects.filter(session=session_obj).select_related('driver')
        return Response(PitStopSerializer(pit_stops, many=True).data)


class RaceResultsView(APIView):
    """GET /api/races/<race_id>/results/?session=R (default R, or Q for qualifying)"""

    def get(self, request, race_id):
        session_type = request.query_params.get('session', 'R')
        session_obj = _get_session_or_none(race_id, session_type)
        if session_obj is None:
            return Response({'detail': 'Session not found.'}, status=404)
        results = Result.objects.filter(session=session_obj).select_related('driver', 'team')
        return Response(ResultSerializer(results, many=True).data)

class SeasonChampionView(APIView):
    """GET /api/seasons/<year>/champion/ -- top points scorer for that season (Race sessions only)"""

    def get(self, request, year):
        results = (
            Result.objects
            .filter(session__race__season__year=year, session__session_type='R')
            .values('driver__id', 'driver__full_name', 'driver__driver_code', 'driver__photo_url')
            .annotate(total_points=Sum('points'))
            .order_by('-total_points')
        )
        leader = results.first()
        if leader is None:
            return Response({'detail': 'No results found for this season.'}, status=404)
        return Response(leader)


class RaceSessionView(APIView):
    """GET /api/races/<race_id>/session/?session=R (default R) -- weather/session conditions"""

    def get(self, request, race_id):
        session_type = request.query_params.get('session', 'R')
        session_obj = _get_session_or_none(race_id, session_type)
        if session_obj is None:
            return Response({'detail': 'Session not found.'}, status=404)
        return Response({
            'session_type': session_obj.session_type,
            'air_temp': session_obj.air_temp,
            'track_temp': session_obj.track_temp,
            'humidity': session_obj.humidity,
            'rainfall': session_obj.rainfall,
        })

class RaceDetailView(APIView):
    """GET /api/races/<race_id>/ -- single race info, including its circuit SVG slug"""

    def get(self, request, race_id):
        race = Race.objects.select_related('season').filter(id=race_id).first()
        if race is None:
            return Response({'detail': 'Race not found.'}, status=404)
        return Response({
            'id': race.id,
            'name': race.name,
            'circuit': race.circuit,
            'country': race.country,
            'season_year': race.season.year,
            'round_number': race.round_number,
            'event_date': race.event_date,
            'circuit_file': get_circuit_file(race.circuit),
        })