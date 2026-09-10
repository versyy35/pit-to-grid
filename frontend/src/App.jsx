import { useState, useEffect } from 'react'

function App() {
  const [races, setRaces] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/races/?season=2023')
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
  }, [])

  if (loading) return <p>Loading races...</p>
  if (error) return <p>Error: {error}</p>

  return (
    <div>
      <h1>Pit to Grid — 2023 Season</h1>
      <ul>
        {races.map((race) => (
          <li key={race.id}>
            Round {race.round_number}: {race.name} — {race.circuit}
          </li>
        ))}
      </ul>
    </div>
  )
}

export default App