import './App.css'
import Navbar from './components/Navbar'
import { BrowserRouter as Router, Routes, Route} from 'react-router-dom';
import Dashboard from './pages/dashboard/index';
import Home from './pages/home/index';

function App() {
  return (
    <Router>
      <div className="flex flex-col w-full h-full">
        <Navbar />
        <hr className="my-4 border-t border-gray-200" />

        <Routes>
          <Route path = "/" element = {<Home />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
