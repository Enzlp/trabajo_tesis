export default function FilterCard() {
  const latamCountries = [
    { code: 'AR', name: 'Argentina' },
    { code: 'BO', name: 'Bolivia' },
    { code: 'BR', name: 'Brasil' },
    { code: 'CL', name: 'Chile' },
    { code: 'CO', name: 'Colombia' },
    { code: 'CR', name: 'Costa Rica' },
    { code: 'CU', name: 'Cuba' },
    { code: 'DO', name: 'República Dominicana' },
    { code: 'EC', name: 'Ecuador' },
    { code: 'SV', name: 'El Salvador' },
    { code: 'GT', name: 'Guatemala' },
    { code: 'HN', name: 'Honduras' },
    { code: 'MX', name: 'México' },
    { code: 'NI', name: 'Nicaragua' },
    { code: 'PA', name: 'Panamá' },
    { code: 'PY', name: 'Paraguay' },
    { code: 'PE', name: 'Perú' },
    { code: 'PR', name: 'Puerto Rico' },
    { code: 'UY', name: 'Uruguay' },
    { code: 'VE', name: 'Venezuela' },
  ];

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
                  <input type="radio" name="orden" value="similitud" defaultChecked />
                  Similitud
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="radio" name="orden" value="citas" />
                  N° de citas
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="radio" name="orden" value="trabajos" />
                  N° de trabajos
                </label>
              </div>
            </td>
          </tr>
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
        </tbody>
      </table>
      <div className="mt-4 flex justify-end">
        <button className="px-4 py-2 bg-[#00d1b2] text-white rounded font-semibold cursor-pointer hover:bg-[#00b89c] transition-colors">
          Aplicar Filtro
        </button>
      </div>
    </div>
  )
}
