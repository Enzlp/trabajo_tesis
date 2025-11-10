import { useState } from "react";

type FilterCardProps = {
  orderFunction: (by: string) => void;
};

export default function FilterCard({ orderFunction }: FilterCardProps) {
  const [orderVal, setOrderVal] = useState<string>("sim");

  return (
    <div className="flex flex-col border-2 border-gray-300 rounded-xl p-6 bg-white w-full">
      <table className="table-fixed w-full text-lg font-semibold">
        <colgroup>
          <col className="w-1/2" /> 
          <col className="w-1/2" /> 
        </colgroup>
        <tbody>
          <tr className="py-2">
            <td className="align-top">Ordenar Por:</td>
            <td className="align-top">
              <div className="flex flex-col gap-2 w-fit">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="orden"
                    value="sim"
                    checked={orderVal === "sim"}
                    onChange={(e) => setOrderVal(e.target.value)}
                  />
                  Similitud
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="orden"
                    value="cites"
                    checked={orderVal === "cites"}
                    onChange={(e) => setOrderVal(e.target.value)}
                  />
                  N° de citas
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="orden"
                    value="works"
                    checked={orderVal === "works"}
                    onChange={(e) => setOrderVal(e.target.value)}
                  />
                  N° de trabajos
                </label>
              </div>
            </td>
          </tr>
          {/*
          <tr className="py-2">
            <td className="align-center">Filtrar país:</td>
            <td className="align-top">
              <select className="flex-1 my-2 border border-gray-300 rounded w-full p-2">
                <option value="">Todos</option>
                {latamCountries.map((country) => (
                  <option key={country.code} value={country.code}>
                    {country.name}
                  </option>
                ))}
              </select>
            </td>
          </tr>
          */}
        </tbody>
      </table>
      <div className="mt-4 flex justify-end">
        <button
          className="px-4 py-2 bg-[#00d1b2] text-white rounded font-semibold cursor-pointer hover:bg-[#00b89c] transition-colors"
          onClick={() => orderFunction(orderVal)} 
        >
          Aplicar Filtro
        </button>
      </div>
    </div>
  );
}
