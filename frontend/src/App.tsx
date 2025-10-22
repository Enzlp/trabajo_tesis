import './App.css'
import Navbar from './components/Navbar'
import { BrowserRouter as Router, Routes, Route} from 'react-router-dom';
import Dashboard from './pages/dashboard/index';
import Home from './pages/home/index';
import Results from './pages/results';

function App() {
  return (
    <Router>
      <div className="flex flex-col w-full h-full">
        <Navbar />
        <hr className="my-4 border-t border-gray-200" />

        <Routes>
          <Route path = "/" element = {<Home />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/results" element={<Results />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
