import logo from '../assets/platform_logo_v2.svg';
import { useNavigate } from "react-router-dom";

function Navbar() {
  const navigate = useNavigate();
  return (
    <div className="w-full flex justify-between items-center px-4 py-2">
      <div onClick={() => navigate("/")} className="flex items-center space-x-2 cursor-pointer">
        <img src={logo} alt="Logo" className="w-8 h-8" />
        <h1 className="font-bold text-[#00d1b2] text-2xl">Colaborador IA</h1>
      </div>

      {/*
      <div
        onClick={() => navigate("/dashboard")}
        className="text-[#00d1b2] font-semibold text-xl hover:underline cursor-pointer"
      >
        Dashboard
      </div>
      */}
    </div>
  );
}


export default Navbar;
