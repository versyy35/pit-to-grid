import { useParams } from 'react-router-dom'

function RaceDetail() {
  const { raceId } = useParams()

  return (
    <div>
      <h1>Race Detail</h1>
      <p>You navigated to race ID: {raceId}</p>
    </div>
  )
}

export default RaceDetail