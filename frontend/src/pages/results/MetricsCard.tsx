type MetricsCardProps = {
  peso1: number;
  peso2: number;
  setPeso1: React.Dispatch<React.SetStateAction<number>>;
  setPeso2: React.Dispatch<React.SetStateAction<number>>;
  fetchFunction: () => Promise<void>;
};


export default function MetricsCard({peso1,peso2, setPeso1, setPeso2, fetchFunction }: MetricsCardProps){

  const handlePeso1 = (e: React.ChangeEvent<HTMLInputElement>) => {
    let v = parseFloat(e.target.value);

    if (isNaN(v)) v = 0;

    // asegurar rango 0–1
    v = Math.min(1, Math.max(0, v));

    setPeso1(v);
    setPeso2(1 - v);
  };

  const handlePeso2 = (e: React.ChangeEvent<HTMLInputElement>) => {
    let v = parseFloat(e.target.value);

    if (isNaN(v)) v = 0;

    v = Math.min(1, Math.max(0, v));

    setPeso2(v);
    setPeso1(1 - v);
  };

  return (
    <div className="flex flex-col border-2 border-gray-300 rounded-xl p-6 bg-white w-full">
      <table className="table-fixed w-full text-lg font-semibold border-separate border-spacing-y-3">
        <colgroup>
          <col className="w-1/2" /> 
          <col className="w-1/2" /> 
        </colgroup>
        <tbody>
          <tr>
            <td>Peso modelo cb:</td>
            <td>
              <input 
                type="number"
                min={0}
                max={1}
                step={0.01}
                value={peso1}
                onChange={handlePeso1}
                className="w-full border border-gray-300 rounded px-2"
              />
            </td>
          </tr>
          <tr>
            <td>Peso modelo cf:</td>
            <td>
              <input 
                type="number"
                min={0}
                max={1}
                step={0.01}
                value={peso2}
                onChange={handlePeso2}
                className="w-full border border-gray-300 rounded px-2"
              />
            </td>
          </tr>
        </tbody>
      </table>

      <div className="mt-4 flex justify-end">
        <button
          className="px-4 py-2 bg-[#00d1b2] text-white rounded font-semibold cursor-pointer hover:bg-[#00b89c] transition-colors"
          onClick={fetchFunction}
        >
          Cambiar Pesos
        </button>
      </div>
    </div>
  );
}
