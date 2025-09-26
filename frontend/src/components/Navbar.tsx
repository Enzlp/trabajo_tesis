import logo from '../assets/platform_logo_v2.svg';

function Navbar() {
  return (
      <div className="w-full flex items-center px-2  space-x-2 items-center justify-center">
        <img src={logo} className='w-8 h-8'></img>
        <h1 className="font-bold text-[#00d1b2] text-2xl">Colaborador IA</h1>
      </div>
  );
}

export default Navbar;
