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
