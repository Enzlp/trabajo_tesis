import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import loading_animation from "../../assets/loading_animation.svg";
import { Building, MapPin, BookOpen, Award, ExternalLink } from "lucide-react";
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
    AR: "Argentina", BO: "Bolivia", BR: "Brazil", CL: "Chile",
    CO: "Colombia", CR: "Costa Rica", CU: "Cuba", DO: "Dominican Republic",
    EC: "Ecuador", GT: "Guatemala", HN: "Honduras", MX: "Mexico",
    NI: "Nicaragua", PA: "Panama", PE: "Peru", PR: "Puerto Rico",
    PY: "Paraguay", SV: "El Salvador", UY: "Uruguay", VE: "Venezuela",
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
      fetch(`http://127.0.0.1:8000/api/authors/?id=${authorUrl}`)
        .then((res) => res.json())
        .then(async (data: Author[]) => {
          const author = data[0];
          setAuthorInfo(author);

          if (author.last_known_institution) {
            try {
              const instRes = await fetch(
                `http://127.0.0.1:8000/api/institution/?id=${author.last_known_institution}`
              );
              const instData: Institution[] = await instRes.json();

              if (instData.length > 0) {
                setInstitutionName(instData[0].display_name);
                setInstitutionUrl(instData[0].homepage_url);
                setCountryCode(instData[0].country_code);
              } else {
                setInstitutionName("No disponible");
              }
            } catch {
              setInstitutionName("No disponible");
            }
          } else {
            setInstitutionName("No disponible");
          }
        });
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [authorId]);

  if (!authorInfo) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <img
          src={loading_animation}
          alt="Cargando..."
          className="w-12 h-12 sm:w-16 sm:h-16 animate-spin"
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8">

        {/* Tarjeta principal responsiva */}
        <div className="rounded-xl border-2 border-gray-300 p-4 sm:p-6 md:p-8 mb-6">
          
          {/* Encabezado */}
          <div className="border-b border-gray-200 pb-4 sm:pb-6 mb-6">
            <h1 className="text-xl sm:text-2xl font-semibold mb-2">
              {authorInfo.display_name}
            </h1>
            <div className="text-gray-600 text-sm sm:text-base">
              {authorInfo.display_name_alternatives?.length > 0
                ? <>También conocido como: {authorInfo.display_name_alternatives.join(", ")}</>
                : "No disponible"}
            </div>
          </div>

          {/* GRID RESPONSIVA */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">

            {/* Columna Izquierda */}
            <div className="space-y-4">

              <div className="flex items-start gap-3">
                <Building className="w-5 h-5 text-teal-600 mt-1" />
                <div>
                  <div className="text-sm text-gray-600">Institución</div>
                  <a
                    href={institutionUrl}
                    className="text-blue-700 font-semibold break-words"
                  >
                    {institutionName || "Cargando..."}
                  </a>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <MapPin className="w-5 h-5 text-teal-600 mt-1" />
                <div>
                  <div className="text-sm text-gray-600">País</div>
                  <div>{latamCountryCodes[countryCode]}</div>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <BookOpen className="w-5 h-5 text-teal-600 mt-1" />
                <div>
                  <div className="text-sm text-gray-600">Número de publicaciones</div>
                  <div>{authorInfo.works_count}</div>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Award className="w-5 h-5 text-teal-600 mt-1" />
                <div>
                  <div className="text-sm text-gray-600">Número de citas</div>
                  <div>{authorInfo.cited_by_count}</div>
                </div>
              </div>

            </div>

            {/* Columna Derecha */}
            <div className="space-y-4">
              
              {authorInfo.orcid && (
                <div className="flex items-start gap-3">
                  <ExternalLink className="w-5 h-5 text-teal-600 mt-1" />
                  <div>
                    <div className="text-sm text-gray-600 mb-1">ORCID</div>
                    <a
                      href={`https://orcid.org/${authorInfo.orcid}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-teal-600 hover:text-teal-700 hover:underline inline-flex items-center gap-1 break-all"
                    >
                      {authorInfo.orcid}
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </div>
                </div>
              )}

              <div className="flex items-start gap-3">
                <ExternalLink className="w-5 h-5 text-teal-600 mt-1" />
                <div>
                  <div className="text-sm text-gray-600 mb-1">Perfil OpenAlex</div>
                  <a
                    href={authorInfo.id}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-teal-600 hover:text-teal-700 hover:underline inline-flex items-center gap-1 break-all"
                  >
                    {authorInfo.id}
                    <ExternalLink className="w-4 h-4 flex-shrink-0" />
                  </a>
                </div>
              </div>

            </div>
          </div>
        </div>

        {/* Works responsivo */}
        <AuthorWorks />

      </div>
    </div>
  );
}
