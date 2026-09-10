import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts'
import './RaceDetail.css'

const API_BASE = 'http://127.0.0.1:8000/api'

const COLORS = [
  '#e10600', '#00d2be', '#0090ff', '#ff8700', '#dc0000',
  '#2b4562', '#00a1e8', '#0d2137', '#006f62', '#b6babd',
  '#ffffff', '#a6051a', '#f596c8', '#c92d4b', '#37bedd',
  '#5e8faa', '#fffc00', '#900000', '#469bff', '#b292ff',
  '#52e252', '#ffc300',
]

function RaceDetail() {
  const { raceId } = useParams()

  const [laps, setLaps] = useState([])
  const [pitStops, setPitStops] = useState([])
  const [results, setResults] = useState([])
  const [session, setSession] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedDrivers, setSelectedDrivers] = useState([])

  useEffect(() => {
    setLoading(true)
    setError(null)

    Promise.all([
      fetch(`${API_BASE}/races/${raceId}/laps/?session=R`).then((r) => r.json()),
      fetch(`${API_BASE}/races/${raceId}/pitstops/?session=R`).then((r) => r.json()),
      fetch(`${API_BASE}/races/${raceId}/results/?session=R`).then((r) => r.json()),
      fetch(`${API_BASE}/races/${raceId}/session/?session=R`).then((r) => r.json()),
    ])
      .then(([lapsData, pitStopsData, resultsData, sessionData]) => {
        setLaps(lapsData)
        setPitStops(pitStopsData)
        setResults(resultsData)
        setSession(sessionData)

        const topThree = resultsData
          .filter((r) => r.finishing_position !== null)
          .sort((a, b) => a.finishing_position - b.finishing_position)
          .slice(0, 3)
          .map((r) => r.driver_code)
        setSelectedDrivers(topThree)

        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [raceId])

  if (loading) return <div className="page"><p className="loading-state">Loading race data...</p></div>
  if (error) return <div className="page"><p className="error-state">Error: {error}</p></div>

  const allDriverCodes = [...new Set(laps.map((lap) => lap.driver_code))].sort()

  const toggleDriver = (code) => {
    setSelectedDrivers((prev) =>
      prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code]
    )
  }

  const lapNumbers = [...new Set(laps.map((lap) => lap.lap_number))].sort((a, b) => a - b)
  const chartData = lapNumbers.map((lapNumber) => {
    const row = { lap: lapNumber }
    laps
      .filter((lap) => lap.lap_number === lapNumber)
      .forEach((lap) => {
        row[lap.driver_code] = lap.lap_time_seconds
      })
    return row
  })

  const selectedTimes = laps
    .filter((lap) => selectedDrivers.includes(lap.driver_code) && lap.lap_time_seconds)
    .map((lap) => lap.lap_time_seconds)
  const yMin = selectedTimes.length ? Math.floor(Math.min(...selectedTimes)) - 2 : 70
  const yMax = selectedTimes.length ? Math.ceil(Math.max(...selectedTimes)) + 2 : 110

  return (
    <div className="page">
      <div className="page-header">
        <h1>Race #{raceId}</h1>
      </div>

      {session && (
        <div className="weather-bar">
          <span>🌡️ Air {session.air_temp.toFixed(1)}°C</span>
          <span>🛣️ Track {session.track_temp.toFixed(1)}°C</span>
          <span>💧 {session.humidity.toFixed(0)}% humidity</span>
          <span>{session.rainfall ? '🌧️ Rain' : '☀️ Dry'}</span>
        </div>
      )}

      <div className="card">
        <h2>Compare Drivers</h2>
        <div className="driver-chips">
          {allDriverCodes.map((code, i) => {
            const color = COLORS[i % COLORS.length]
            const active = selectedDrivers.includes(code)
            return (
              <button
                key={code}
                className={`driver-chip ${active ? 'active' : ''}`}
                style={{
                  borderColor: color,
                  background: active ? color : 'transparent',
                }}
                onClick={() => toggleDriver(code)}
              >
                {code}
              </button>
            )
          })}
        </div>
      </div>

      <div className="card">
        <h2>Lap Times</h2>
        {selectedDrivers.length === 0 ? (
          <p className="empty-state">Select drivers above to compare lap times.</p>
        ) : (
          <ResponsiveContainer width="100%" height={380}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2c32" />
              <XAxis dataKey="lap" stroke="#9a9ba5" tick={{ fontSize: 12 }} />
              <YAxis domain={[yMin, yMax]} stroke="#9a9ba5" tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{ background: '#17181c', border: '1px solid #2a2c32', borderRadius: 8 }}
              />
              <Legend />
              {selectedDrivers.map((code) => {
                const colorIndex = allDriverCodes.indexOf(code)
                return (
                  <Line
                    key={code}
                    type="monotone"
                    dataKey={code}
                    stroke={COLORS[colorIndex % COLORS.length]}
                    dot={false}
                    connectNulls
                    strokeWidth={2}
                  />
                )
              })}
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className="card">
        <h2>Pit Stops</h2>
        <ul className="pit-list">
          {pitStops.map((stop) => (
            <li key={stop.id}>
              <span className="code">{stop.driver_code}</span>
              Lap {stop.lap_number} —{' '}
              {stop.duration_seconds > 120
                ? `${(stop.duration_seconds / 60).toFixed(1)} min (stoppage)`
                : `${stop.duration_seconds.toFixed(2)}s`}
            </li>
          ))}
        </ul>
      </div>

      <div className="card">
        <h2>Results</h2>
        <table className="results">
          <thead>
            <tr>
              <th>Pos</th>
              <th>Driver</th>
              <th>Team</th>
              <th>Grid</th>
              <th>Points</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {results.map((result) => (
              <tr key={result.id}>
                <td><span className="pos-badge">{result.finishing_position ?? '-'}</span></td>
                <td>{result.driver_name}</td>
                <td>{result.team_name}</td>
                <td>{result.grid_position ?? '-'}</td>
                <td>{result.points}</td>
                <td>{result.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default RaceDetail