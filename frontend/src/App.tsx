import './App.css'
import Navbar from './components/Navbar'
import { BrowserRouter as Router, Routes, Route} from 'react-router-dom';

function App() {
  return (
    <div className='flex flex-col'>
      <Navbar />
      <Router >
        <Routes>
          
        </Routes>
      </Router>
    </div>
  )
}

export default App
