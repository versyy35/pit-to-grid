import { useState, useEffect } from 'react'

const SEASONS = [2021, 2022, 2023, 2024, 2025, 2026]

function App() {
  const [season, setSeason] = useState(2023)
  const [races, setRaces] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    setError(null)

    fetch(`http://127.0.0.1:8000/api/races/?season=${season}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error: ${response.status}`)
        }
        return response.json()
      })
      .then((data) => {
        setRaces(data.results)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [season])

  return (
    <div>
      <h1>Pit to Grid</h1>

      <label htmlFor="season-select">Select Season: </label>
      <select
        id="season-select"
        value={season}
        onChange={(e) => setSeason(Number(e.target.value))}
      >
        {SEASONS.map((year) => (
          <option key={year} value={year}>
            {year}
          </option>
        ))}
      </select>

      {loading && <p>Loading races...</p>}
      {error && <p>Error: {error}</p>}

      {!loading && !error && (
        <ul>
          {races.map((race) => (
            <li key={race.id}>
              Round {race.round_number}: {race.name} — {race.circuit}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default App