import logo from '../assets/P2G-BigLogo.png'
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import TrackMap from '../components/TrackMap'
import './RaceSelector.css'

const API_BASE = 'http://127.0.0.1:8000/api'
const SEASONS = [2021, 2022, 2023, 2024, 2025, 2026]

function RaceSelector() {
  const navigate = useNavigate()

  const [season, setSeason] = useState(2023)
  const [races, setRaces] = useState([])
  const [selectedRaceId, setSelectedRaceId] = useState('')
  const [champion, setChampion] = useState(null)
  const [raceDetail, setRaceDetail] = useState(null)
  const [loading, setLoading] = useState(true)

  // Fetch races + champion whenever the season changes
  useEffect(() => {
    setLoading(true)
    setSelectedRaceId('')
    setRaceDetail(null)

    Promise.all([
      fetch(`${API_BASE}/races/?season=${season}`).then((r) => r.json()),
      fetch(`${API_BASE}/seasons/${season}/champion/`).then((r) => r.json()),
    ])
      .then(([racesData, championData]) => {
        setRaces(racesData.results)
        setChampion(championData.driver__full_name ? championData : null)
        if (racesData.results.length > 0) {
          setSelectedRaceId(String(racesData.results[0].id))
        }
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [season])

  // Fetch circuit info whenever the selected race changes
  useEffect(() => {
    if (!selectedRaceId) return
    fetch(`${API_BASE}/races/${selectedRaceId}/`)
      .then((r) => r.json())
      .then((data) => setRaceDetail(data))
      .catch(() => setRaceDetail(null))
  }, [selectedRaceId])

  const handleAnalyse = () => {
    if (selectedRaceId) navigate(`/race/${selectedRaceId}`)
  }

  return (
    <div className="selector-page">
      <img src={logo} alt="Pit to Grid" className="brand-logo" />
      <p className="brand-tagline">Analyzing Data from the Grid to You.</p>

      <div className="selector-hero">
        <div className="hero-side">
          {champion && champion.driver__photo_url && (
            <img
              src={champion.driver__photo_url}
              alt={champion.driver__full_name}
              className="champion-photo"
            />
          )}
          {champion && (
            <p className="champion-caption">
              {champion.driver__full_name} — {champion.total_points} pts
            </p>
          )}
        </div>

        <div className="hero-side">
          <TrackMap circuitFile={raceDetail?.circuit_file} />
        </div>
      </div>

      <div className="selector-controls">
        <select
          className="dropdown"
          value={season}
          onChange={(e) => setSeason(Number(e.target.value))}
        >
          {SEASONS.map((year) => (
            <option key={year} value={year}>{year}</option>
          ))}
        </select>

        <select
          className="dropdown"
          value={selectedRaceId}
          onChange={(e) => setSelectedRaceId(e.target.value)}
          disabled={loading || races.length === 0}
        >
          {races.map((race) => (
            <option key={race.id} value={race.id}>
              Round {race.round_number}: {race.name}
            </option>
          ))}
        </select>
      </div>

      <button className="analyse-button" onClick={handleAnalyse} disabled={!selectedRaceId}>
        Analyse
      </button>
    </div>
  )
}

export default RaceSelector