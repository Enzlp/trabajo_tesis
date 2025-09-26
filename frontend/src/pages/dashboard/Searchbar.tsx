function Searchbar() {
  return (
    <div className="p-4 flex w-full max-w-lg">
      <input
        type="text"
        placeholder="Buscar..."
        className="bg-white border border-gray-400 p-2 rounded-l-md focus:outline-none flex-1"
      />
      <button className="bg-[#00d1b2] text-white font-semibold p-2 rounded-r-md cursor-pointer hover:bg-[#00b899]">
        Buscar
      </button>
    </div>
  )
}

export default Searchbar
