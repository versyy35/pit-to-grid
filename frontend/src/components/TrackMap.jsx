import { useState, useEffect } from 'react'
import './TrackMap.css'

function TrackMap({ circuitFile }) {
  const [pathData, setPathData] = useState(null)

  useEffect(() => {
    if (!circuitFile) return
    fetch(`/circuits/${circuitFile}`)
      .then((res) => res.text())
      .then((text) => {
        const match = text.match(/d="([^"]+)"/)
        setPathData(match ? match[1] : null)
      })
      .catch(() => setPathData(null))
  }, [circuitFile])

  if (!circuitFile || !pathData) {
    return <div className="track-map-placeholder">No track layout available</div>
  }

  return (
    <div className="track-map">
      <svg viewBox="0 0 500 500" className="track-map-svg">
        <path d={pathData} className="track-outline" />
        <circle r="10" className="track-dot">
          <animateMotion
            dur="6s"
            repeatCount="indefinite"
            path={pathData}
          />
        </circle>
      </svg>
    </div>
  )
}

export default TrackMap