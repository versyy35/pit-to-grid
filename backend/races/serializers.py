from rest_framework import serializers
from .models import Season, Team, Driver, Race, Session, Lap, PitStop, Result


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = ['id', 'year']


class RaceSerializer(serializers.ModelSerializer):
    season_year = serializers.IntegerField(source='season.year', read_only=True)

    class Meta:
        model = Race
        fields = ['id', 'season_year', 'round_number', 'name', 'circuit', 'country', 'event_date']


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ['id', 'driver_code', 'driver_number', 'full_name']


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'name']


class SessionSerializer(serializers.ModelSerializer):
    race = RaceSerializer(read_only=True)

    class Meta:
        model = Session
        fields = ['id', 'race', 'session_type', 'air_temp', 'track_temp', 'humidity', 'rainfall']


class LapSerializer(serializers.ModelSerializer):
    driver_code = serializers.CharField(source='driver.driver_code', read_only=True)

    class Meta:
        model = Lap
        fields = [
            'id', 'driver_code', 'lap_number', 'lap_time_seconds',
            'sector1_seconds', 'sector2_seconds', 'sector3_seconds',
            'compound', 'tyre_life', 'position', 'is_pit_lap',
        ]


class PitStopSerializer(serializers.ModelSerializer):
    driver_code = serializers.CharField(source='driver.driver_code', read_only=True)

    class Meta:
        model = PitStop
        fields = ['id', 'driver_code', 'lap_number', 'duration_seconds']


class ResultSerializer(serializers.ModelSerializer):
    driver_code = serializers.CharField(source='driver.driver_code', read_only=True)
    driver_name = serializers.CharField(source='driver.full_name', read_only=True)
    driver_photo = serializers.CharField(source='driver.photo_url', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)

    class Meta:
        model = Result
        fields = [
            'id', 'driver_code', 'driver_name', 'driver_photo', 'team_name',
            'finishing_position', 'grid_position', 'points', 'status',
            'q1_seconds', 'q2_seconds', 'q3_seconds',
        ]
