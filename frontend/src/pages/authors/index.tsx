import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import loading_animation from "../../assets/loading_animation.svg";
import user_id from '../../assets/user-id.svg';
import AuthorWorks from "./AuthorWorks";

interface Author {
  id: string;
  orcid?: string;
  display_name: string;
  display_name_alternatives: string[];
  works_count: number;
  cited_by_count: number;
  last_known_institution: string; 
  works_api_url: string;
  updated_date: Date;
}

interface Institution {
  id: string;
  display_name: string;
  homepage_url: string;
  country_code: string;
}

export default function Authors() {

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


  const { authorId } = useParams<{ authorId: string }>();
  const [authorInfo, setAuthorInfo] = useState<Author>();
  const [institutionName, setInstitutionName] = useState<string>("");
  const [institutionUrl, setInstitutionUrl] = useState<string>("");
  const [countryCode, setCountryCode] = useState<string>("");

  useEffect(() => {
    if (!authorId) return;

    const authorUrl = `https://openalex.org/${authorId}`;

    const timeoutId = setTimeout(() => {
      fetch(`http://127.0.0.1:8000/api/author/?id=${authorUrl}`)
        .then((res) => res.json())
        .then(async (data: Author[]) => {
          const author = data[0];
          setAuthorInfo(author);


          if (author.last_known_institution) {
            try {
              const instRes = await fetch(`http://127.0.0.1:8000/api/institution/?id=${author.last_known_institution}`);
              const instData: Institution[] = await instRes.json();

              if (instData.length > 0) {
                setInstitutionName(instData[0].display_name);
				        setInstitutionUrl(instData[0].homepage_url);
                setCountryCode(instData[0].country_code)
              } else {
                setInstitutionName("No disponible");
              }
            } catch (error) {
              console.error("Error al cargar institución:", error);
              setInstitutionName("No disponible");
            }
          } else {
            setInstitutionName("No disponible");
          }
        })
        .catch((err) => console.error(err));
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [authorId]);


  if (!authorInfo) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <img
          src={loading_animation}
          alt="Cargando..."
          className="w-16 h-16 animate-spin"
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen px-8 py-2 flex flex-col m-4">
      <div className="flex w-full gap-4">
        <div className="flex flex-col border-2 border-gray-300 rounded-xl p-6 w-4/10 h-fit">
          <div className="flex items-center gap-2">
            <img src={user_id} className="w-10 h-10" alt="user" />
            <h3 className="text-xl font-semibold">{authorInfo.display_name}</h3>
          </div>

          <div className="py-2">
            <p className="text-base text-gray-700">
              <span className="font-semibold">Nombres Alternativos:</span>{" "}
              {authorInfo.display_name_alternatives?.length > 0
                ? authorInfo.display_name_alternatives.join(", ")
                : "No disponible"}
            </p>

            <p className="text-base text-gray-700">
              <span className="font-semibold">Institución: </span>
              <a href={institutionUrl} className="text-blue-700 font-semibold">{institutionName || "Cargando..."}</a>
            </p>

            <p className="text-base text-gray-700">
              <span className="font-semibold">Pais: </span>
              {latamCountryCodes[countryCode]}
            </p>

            <p className="text-base text-gray-700">
              <span className="font-semibold">ORCID: </span>
              {authorInfo.orcid ? (
                <a href={authorInfo.orcid} className="text-blue-700 font-semibold">
                  Ver ORCID
                </a>
              ) : (
                "N/A"
              )}
            </p>
            <p className="text-base text-gray-700">
              <span className="font-semibold">OpenAlex:</span>{" "}
              <a href={authorInfo.id} className="text-blue-700 font-semibold">Ver en OpenAlex</a>
            </p>
          </div>

          <hr className="my-2 border-gray-300" />

          <div className="py-2">
            <p className="text-base text-gray-700">
              <span className="font-semibold">N° de trabajos: </span>
              {authorInfo.works_count}
            </p>
            <p className="text-base text-gray-700">
              <span className="font-semibold">N° de citas: </span>
              {authorInfo.cited_by_count}
            </p>
          </div>
        </div>
        <AuthorWorks/>
      </div>
    </div>
  );
}
