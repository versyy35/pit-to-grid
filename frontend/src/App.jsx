import { BrowserRouter, Routes, Route } from 'react-router-dom'
import RaceSelector from './pages/RaceSelector'
import RaceDetail from './pages/RaceDetail'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<RaceSelector />} />
        <Route path="/race/:raceId" element={<RaceDetail />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App