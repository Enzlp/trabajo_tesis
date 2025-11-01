import { useEffect, useState } from "react"
import { useParams } from "react-router-dom";
import loading_animation from "../../assets/loading_animation.svg";
import { MathJaxContext, MathJax } from "better-react-mathjax";

interface Work{
  cited_by_count: number;
  display_name: string;
  doi: string;
  id: string;
  is_paratext: boolean;
  is_retracted: boolean;
  language: string;
  publication_date: string;
  publication_year: number;
  title: string;
  type: string;
}

interface ApiResponse{
  next_last_work_id: string;
  results: Work[];
}

export default function AuthorWorks(){
  const {authorId} = useParams<{authorId: string}>();
  const [workList, setWorkList] = useState<Work[]>([]);

  useEffect(() => {
    if (!authorId) return;

    const limit = 10;
    const apiUrl = `http://127.0.0.1:8000/api/authors/${authorId}/works/?limit=${limit}`;

    const timeoutId = setTimeout(() => {
      fetch(apiUrl)
        .then((res) => {
          if (!res.ok) {
            throw new Error(`Error HTTP: ${res.status}`);
          }
          return res.json();
        })
        .then((data: ApiResponse) => {
          setWorkList(data.results);
          console.log(data.results);
        })
        .catch((err) => {
          console.error("Error al obtener datos:", err);
        });
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [authorId]); 

  if(!workList || workList.length == 0){
    return (
      <div className="flex flex-col rounded-xl p-6 w-6/10 items-center justify-center">
        <img
          src={loading_animation}
          alt="Cargando..."
          className="w-16 h-16 animate-spin"
        />
      </div>
    );
  }

  return (
  <>
    {workList && (
      <div className="flex flex-col border-2 border-gray-300 rounded-xl p-6 w-6/10">
        <h3 className="px-4 mb-2 text-xl font-semibold">Trabajos</h3>
        {workList.map((work: Work) => (
          <div key={work.id} className="p-4 hover:bg-gray-100 hover:cursor-pointer transition-colors duration-300">
            <h3
              className="text-base font-semibold"
              dangerouslySetInnerHTML={{ __html: work.title }}
            />
            <div>
              <p className="text-sm text-gray-400 font-semibold">{work.publication_year} - </p>
            </div>
            <div className="flex">
              <p className="text-sm font-medium">Citado por {work.cited_by_count} - Idioma: {work.language}</p>
              <a></a>
            </div>
          </div>
        ))}
      </div>
    )}
  </>
);

}