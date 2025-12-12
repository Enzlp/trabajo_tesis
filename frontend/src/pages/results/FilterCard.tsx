import { useState } from "react";

type FilterCardProps = {
  filterFunction: (by: string, limit: number, country: string) => void;
};

export default function FilterCard({ filterFunction }: FilterCardProps) {
  const [orderVal, setOrderVal] = useState<string>("sim");
  const [resultLimit, setResultLimit] = useState<number>(50);
  const [countryCode, setCountryCode] = useState<string>("");

  const latamCountryCodes: { [key: string]: string } = {
    AR: "Argentina",
    BO: "Bolivia",
    BR: "Brazil",
    CL: "Chile",
    CO: "Colombia",
    CR: "Costa Rica",
    CU: "Cuba",
    DO: "Dominican Republic",
    EC: "Ecuador",
    GT: "Guatemala",
    HN: "Honduras",
    MX: "Mexico",
    NI: "Nicaragua",
    PA: "Panama",
    PE: "Peru",
    PR: "Puerto Rico",
    PY: "Paraguay",
    SV: "El Salvador",
    UY: "Uruguay",
    VE: "Venezuela",
  };

  return (
    <div className="flex flex-col border-2 border-gray-300 rounded-xl p-4 sm:p-6 bg-white w-full">
      <table className="table-fixed w-full text-sm sm:text-base md:text-lg font-semibold">
        <colgroup>
          <col className="w-2/5 sm:w-1/2" />
          <col className="w-3/5 sm:w-1/2" />
        </colgroup>
        <tbody>
          <tr className="py-2">
            <td className="align-top text-sm sm:text-base">Ordenar Por:</td>
            <td className="align-top">
              <div className="flex flex-col gap-1.5 sm:gap-2 w-fit">
                <label className="flex items-center gap-2 cursor-pointer text-sm sm:text-base">
                  <input
                    type="radio"
                    name="orden"
                    value="sim"
                    checked={orderVal === "sim"}
                    onChange={(e) => setOrderVal(e.target.value)}
                  />
                  Similitud
                </label>

                <label className="flex items-center gap-2 cursor-pointer text-sm sm:text-base">
                  <input
                    type="radio"
                    name="orden"
                    value="cites"
                    checked={orderVal === "cites"}
                    onChange={(e) => setOrderVal(e.target.value)}
                  />
                  N° de citas
                </label>

                <label className="flex items-center gap-2 cursor-pointer text-sm sm:text-base">
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

          <tr className="py-2">
            <td className="align-center text-sm sm:text-base">Filtrar por país:</td>
            <td className="align-top">
              <select
                className="flex-1 my-2 border border-gray-300 rounded w-full p-1.5 sm:p-2 text-sm sm:text-base"
                value={countryCode}
                onChange={(e) => setCountryCode(e.target.value)}
              >
                <option value="">Todos</option>
                {Object.entries(latamCountryCodes).map(([code, name]) => (
                  <option key={code} value={code}>
                    {name}
                  </option>
                ))}
              </select>
            </td>
          </tr>

          <tr className="py-2">
            <td className="align-center text-sm sm:text-base">Resultados:</td>
            <td className="align-top">
              <input
                type="number"
                min={1}
                max={200}
                value={resultLimit}
                onChange={(e) =>
                  setResultLimit(
                    Math.min(200, Math.max(1, Number(e.target.value)))
                  )
                }
                className="border border-gray-300 rounded w-full p-1.5 sm:p-2 text-sm sm:text-base"
              />
            </td>
          </tr>
        </tbody>
      </table>

      <div className="mt-4 flex justify-end">
        <button
          className="px-3 sm:px-4 py-1.5 sm:py-2 bg-[#00d1b2] text-white rounded text-sm sm:text-base font-semibold cursor-pointer hover:bg-[#00b89c] transition-colors"
          onClick={() => filterFunction(orderVal, resultLimit, countryCode)}
        >
          Aplicar Filtro
        </button>
      </div>
    </div>
  );
}