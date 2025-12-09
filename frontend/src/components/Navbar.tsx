import logo from '../assets/platform_logo_v2.svg';
import { useNavigate } from "react-router-dom";
import { HelpCircle } from 'lucide-react';

function Navbar() {
  const navigate = useNavigate();
  return (
    <div className="w-full flex justify-between items-center px-4 py-2">
      <div onClick={() => navigate("/")} className="flex items-center space-x-2 cursor-pointer">
        <img src={logo} alt="Logo" className="w-8 h-8" />
        <h1 className="font-bold text-[#00d1b2] text-2xl">Colaborador IA</h1>
      </div>
      <a 
        href='/about'
        className='w-10 h-10 rounded-full border-2 border-gray-300 flex items-center justify-center hover:border-teal-500 hover:text-teal-500 transition-colors'
        aria-label='informacion'>
        <HelpCircle className='w-5 h-5' />
      </a>
    </div>
  );
}


export default Navbar;
