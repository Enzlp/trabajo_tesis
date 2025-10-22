import { useLocation } from "react-router-dom";
import arrowLeft from '../../assets/arrow-left.svg'
import RecommendedCard from "./RecommendedCard";
import { useNavigate } from "react-router-dom";
import FilterCard from "./FilterCard";
import StatsCard from './StatsCard';

interface Concept {
  id: number;
  display_name: string;
}

export default function Results() {
	const location = useLocation();
	const conceptList: Concept[] = location.state?.conceptList || [];
	const navigate = useNavigate();

  const goBack = () =>{
    navigate('/');
  }

	console.log(conceptList)
    return (
      <div className="min-h-screen px-8 py-2 felx flex-col m-4 ">
        <div className="flex items-center cursor-pointer rounded-2xl hover:bg-gray-200 w-fit p-2" onClick={goBack}>
          <img src={arrowLeft} className="w-6 h-6"></img>
          <h1 className="font-semibold text-lg px-2">Atrás</h1>
        </div>
        <div className="flex w-full gap-4">
          <div className="flex flex-col w-6/10">
            <h1 className="text-2xl font-bold mb-4">Investigadores recomendados</h1>
            <RecommendedCard />
          </div>
          <div className="flex flex-col w-4/10">
            <div className="flex flex-col">
              <h1 className="text-2xl font-bold mb-4"> Filtros </h1>
              <FilterCard />
            </div>
              <div className="flex flex-col">
                <h1 className="text-2xl font-bold my-4"> Stats </h1>
                <StatsCard />
              </div>
          </div>
        </div>

      </div>
    )
}