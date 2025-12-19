import { useLocation } from "react-router-dom";
import RecommendedCard from "./RecommendedCard";
import FilterCard from "./FilterCard";
import { useEffect, useState } from "react";
import MetricsCard from "./MetricsCard";
import { Info, TrendingUp, ChevronRight, Globe } from "lucide-react";

interface Concept {
  id: string;
  display_name: string;
}

type ConceptScore = {
  concept_id: string;
  score: number;
  display_name: string;
}

type Recommendation = {
  author_id: string;
  orcid: string | null;
  display_name: string;
  country_code: string;
  institution_name: string;
  similarity_score: number;
  cb_score: number;
  cf_score: number;
  works_count: number;
  cited_by_count: number;
  top_concepts: ConceptScore[];
};

export default function Results() {
  const location = useLocation();
  const [loading, setLoading] = useState<boolean>(true);
  const [totalResult, setTotalResult] = useState<number>(0);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);

  const [conceptList, setConceptList] = useState<Concept[]>([]);
  const [authorId, setAuthorId] = useState<string>("");

  const [peso1, setPeso1] = useState<number>(0.5);
  const [peso2, setPeso2] = useState<number>(0.5);

  const [currentOrderBy, setCurrentOrderBy] = useState<string>("sim");
  const [currentLimit, setCurrentLimit] = useState<number>(50);
  const [currentCountry, setCurrentCountry] = useState<string>("");

  // Estados para tooltips
  const [showInfoRec, setShowInfoRec] = useState(false);

  const infoRecommendations =
    "Las recomendaciones se generan combinando afinidad temática, basada en los intereses que ingreses, y la red de colaboración del autor seleccionado. Dependiendo de tu elección, se usa uno de los modelos o un sistema híbrido, y los scores indican la relevancia de cada recomendación, normalizados para poder compararlas entre modelos.";

  useEffect(() => {
    const cList: Concept[] = location.state?.conceptList || [];
    const aId: string = location.state?.authorId || "";


    setConceptList(cList);
    setAuthorId(aId);

    const fetchRecommendations = async () => {
      try {
        const payload: any = {};
        if (cList.length > 0) payload.concept_vector = cList;
        if (aId !== "") payload.author_id = aId;

        const response = await fetch(
          "https://collabrecommender.dcc.uchile.cl/api/recommendation/",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          }
        );

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        const data = await response.json();
        setRecommendations(data.recommendations);
        setTotalResult(data.total_recommendations);
        setLoading(false);
      } catch (err) {
        if (err instanceof Error) console.log(err.message);
      }
    };

    fetchRecommendations();
  }, [location.state?.conceptList]);

  const applyFilters = async (by: string, limit: number, country: string) => {
    try {
      setLoading(true);
      setRecommendations([]);
      setCurrentOrderBy(by);
      setCurrentLimit(limit);
      setCurrentCountry(country);

      const payload: any = {};
      if (conceptList.length > 0) payload.concept_vector = conceptList;
      if (authorId !== "") payload.author_id = authorId;

      payload.order_by = by;
      payload.limit = limit;
      if (country !== "") payload.country_code = country;
      if (conceptList.length > 0 && authorId !== "") {
        payload.alpha = peso1;
        payload.beta = peso2;
      }

      const response = await fetch(
        "https://collabrecommender.dcc.uchile.cl/api/recommendation/",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      setRecommendations(data.recommendations);
      setTotalResult(data.total_recommendations);
      setLoading(false);
    } catch (err) {
      if (err instanceof Error) console.log(err.message);
      setLoading(false);
    }
  };

  const weightedFetch = async () => {
    try {
      setLoading(true);
      setRecommendations([]);

      const payload: any = {};
      payload.concept_vector = conceptList;
      payload.author_id = authorId;
      payload.alpha = peso1;
      payload.beta = peso2;
      payload.order_by = currentOrderBy;
      payload.limit = currentLimit;
      if (currentCountry !== "") payload.country_code = currentCountry;

      const response = await fetch(
        "https://collabrecommender.dcc.uchile.cl/api/recommendation/",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      setRecommendations(data.recommendations);
      setTotalResult(data.total_recommendations);
      setLoading(false);
    } catch (err) {
      if (err instanceof Error) console.log(err.message);
    }
  };

return (
  <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-teal-50 px-4 md:px-8 py-6">
    <div className="max-w-7xl mx-auto">

      {/* Search Summary Card */}
      <div className="mb-6 bg-white rounded-2xl shadow-lg border border-gray-100 p-6">

        {/* Breadcrumb */}
        <div className="flex items-center gap-2 text-sm text-gray-500 mb-4">
          <span>Inicio</span>
          <ChevronRight className="w-4 h-4" />
          <span className="text-teal-600 font-medium">Resultados</span>
        </div>

        {/* Título */}
        <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-4">
          Investigadores Recomendados
        </h1>

        <p className="mb-4">Los investigadores se muestran con un porcentaje que indica su relevancia según tu búsqueda. Los scores combinan afinidad temática y conexiones en la red de colaboración regional, para que puedas identificar rápidamente los perfiles más relevantes.</p>

        {/* Result count + info */}
        <div className="flex items-center gap-2 text-gray-600 mb-6">
          <TrendingUp className="w-5 h-5 text-teal-600" />
          <p className="text-sm md:text-base">
            Mostrando <span className="font-bold text-teal-700">{totalResult}</span> resultados
          </p>
          <div className="flex items-center gap-2 ml-4">
            <div
              onMouseEnter={() => setShowInfoRec(true)}
              onMouseLeave={() => setShowInfoRec(false)}
              className="relative"
            >
              <button className="text-gray-400 hover:text-teal-600 transition-colors">
                <Info className="w-5 h-5" />
              </button>
              {showInfoRec && (
                <div className="absolute z-20 w-72 p-3 left-6 top-1/2 -translate-y-1/2 bg-gray-900 text-white text-xs rounded-lg shadow-xl">
                  {infoRecommendations}
                </div>
              )}
            </div>
          </div>
        </div>

      </div>

		{/* Filters & Metrics above recommendations */}
		<div className="mb-6 flex flex-col lg:flex-row gap-6 items-stretch">

		{/* Left: Filters - ocupa 2/3 en lg */}
		<div className="w-full lg:w-2/3">
			<FilterCard filterFunction={applyFilters} />
		</div>

		{/* Right: Metrics - ocupa 1/3 en lg, solo si hay concepto y autor */}
    {conceptList.length > 0 && authorId !== "" ? (
      <div className="w-full lg:w-1/3">
        <MetricsCard
          peso1={peso1}
          peso2={peso2}
          setPeso1={setPeso1}
          setPeso2={setPeso2}
          fetchFunction={weightedFetch}
        />
      </div>
    ) : (
      // Aquí va lo que quieres renderizar cuando NO se cumpla la condición
      <div className="rounded-2xl shadow-md border border-gray-100 w-full lg:w-1/3 flex bg-gradient-to-r from-teal-500 to-cyan-600">
        <div className="p-6 flex items-center">
          <p className="text-white">Usa la búsqueda híbrida para ajustar y ver los parámetros del modelo.</p>
          <Globe className="w-50 h-50 text-white" />
        </div>
      </div>
    )}


		</div>



      {/* Recommendations */}
      <RecommendedCard recs={recommendations} loading={loading} />

    </div>
  </div>
);

}