import {Target, Network, TrendingUp, Users, BookOpen, Lightbulb } from 'lucide-react';

export default function About() {
  return (
    <div className="min-h-screen">
      {/* Mission Section */}
      <div className="py-8 sm:py-12 md:py-16 px-4 sm:px-6 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-8 sm:mb-12">
            <h2 className="text-2xl sm:text-3xl md:text-4xl mb-3 sm:mb-4 font-bold">Acerca de</h2>
            <p className="text-gray-600 max-w-3xl mx-auto text-sm sm:text-base md:text-lg text-justify px-2">
              Esta plataforma surge frente a la baja colaboración entre investigadores en inteligencia artificial dentro de Latinoamérica, 
              una situación destacada en el último reporte de ILIA (2024). Su objetivo es ofrecer una primera herramienta que facilite el 
              descubrimiento de investigadores en la región con quienes establecer colaboraciones.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-6 sm:gap-8">
            <div className="text-center px-4">
              <div className="w-14 h-14 sm:w-16 sm:h-16 bg-teal-100 rounded-xl flex items-center justify-center mx-auto mb-3 sm:mb-4">
                <Network className="w-7 h-7 sm:w-8 sm:h-8 text-teal-600" />
              </div>
              <h3 className="mb-2 text-base sm:text-lg font-semibold">Conectar</h3>
              <p className="text-gray-600 text-sm sm:text-base">
                Facilitar conexiones entre investigadores con intereses afines en toda América Latina
              </p>
            </div>

            <div className="text-center px-4">
              <div className="w-14 h-14 sm:w-16 sm:h-16 bg-teal-100 rounded-xl flex items-center justify-center mx-auto mb-3 sm:mb-4">
                <Lightbulb className="w-7 h-7 sm:w-8 sm:h-8 text-teal-600" />
              </div>
              <h3 className="mb-2 text-base sm:text-lg font-semibold">Descubrir</h3>
              <p className="text-gray-600 text-sm sm:text-base">
                Ayudar a encontrar nuevas oportunidades de colaboración basadas en perfiles académicos
              </p>
            </div>

            <div className="text-center px-4 sm:col-span-2 md:col-span-1">
              <div className="w-14 h-14 sm:w-16 sm:h-16 bg-teal-100 rounded-xl flex items-center justify-center mx-auto mb-3 sm:mb-4">
                <TrendingUp className="w-7 h-7 sm:w-8 sm:h-8 text-teal-600" />
              </div>
              <h3 className="mb-2 text-base sm:text-lg font-semibold">Impulsar</h3>
              <p className="text-gray-600 text-sm sm:text-base">
                Fortalecer la investigación regional mediante colaboraciones estratégicas y efectivas
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-8 sm:py-12 md:py-16 px-4 sm:px-6 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-8 sm:mb-12">
            <h2 className="text-2xl sm:text-3xl md:text-4xl mb-3 sm:mb-4 font-bold">Características Principales</h2>
          </div>

          <div className="grid md:grid-cols-2 gap-4 sm:gap-6 md:gap-8">
            {/* Feature 1 */}
            <div className="bg-white rounded-xl p-4 sm:p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-start gap-3 sm:gap-4">
                <div className="w-10 h-10 sm:w-12 sm:h-12 bg-teal-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Target className="w-5 h-5 sm:w-6 sm:h-6 text-teal-600" />
                </div>
                <div>
                  <h3 className="mb-1 sm:mb-2 text-base sm:text-lg font-semibold">Búsqueda por Conceptos</h3>
                  <p className="text-gray-600 text-sm sm:text-base">
                    Ingresa los temas de IA que te interesan y encuentra investigadores trabajando en áreas similares. 
                  </p>
                </div>
              </div>
            </div>

            {/* Feature 2 */}
            <div className="bg-white rounded-xl p-4 sm:p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-start gap-3 sm:gap-4">
                <div className="w-10 h-10 sm:w-12 sm:h-12 bg-teal-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Users className="w-5 h-5 sm:w-6 sm:h-6 text-teal-600" />
                </div>
                <div>
                  <h3 className="mb-1 sm:mb-2 text-base sm:text-lg font-semibold">Análisis de Redes de Coautoría</h3>
                  <p className="text-gray-600 text-sm sm:text-base">
                    Descubre investigadores a través de sus conexiones académicas. Si conoces a un investigador, 
                    podemos recomendarte otros en base a la red de colaboración regional.
                  </p>
                </div>
              </div>
            </div>

            {/* Feature 3 */}
            <div className="bg-white rounded-xl p-4 sm:p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-start gap-3 sm:gap-4">
                <div className="w-10 h-10 sm:w-12 sm:h-12 bg-teal-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <BookOpen className="w-5 h-5 sm:w-6 sm:h-6 text-teal-600" />
                </div>
                <div>
                  <h3 className="mb-1 sm:mb-2 text-base sm:text-lg font-semibold">Información Relevante</h3>
                  <p className="text-gray-600 text-sm sm:text-base">
                    Explora información relevante acerca de los investigadores recomendados, como información personal y 
                    sus ultimas publicaciones.
                  </p>
                </div>
              </div>
            </div>

            {/* Feature 4 */}
            <div className="bg-white rounded-xl p-4 sm:p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-start gap-3 sm:gap-4">
                <div className="w-10 h-10 sm:w-12 sm:h-12 bg-teal-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Network className="w-5 h-5 sm:w-6 sm:h-6 text-teal-600" />
                </div>
                <div>
                  <h3 className="mb-1 sm:mb-2 text-base sm:text-lg font-semibold">Búsqueda Híbrida</h3>
                  <p className="text-gray-600 text-sm sm:text-base">
                    Combina conceptos de interés con un investigador conocido para obtener recomendaciones 
                    personalizadas que integran ambos criterios de búsqueda.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* How It Works Section */}
      <div className="py-8 sm:py-12 md:py-16 px-4 sm:px-6 bg-white">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-8 sm:mb-12">
            <h2 className="mb-3 sm:mb-4 text-2xl sm:text-3xl md:text-4xl font-bold">¿Cómo Funciona?</h2>
            <p className="text-gray-600 text-sm sm:text-base md:text-lg">
              Encuentra colaboradores en tres simples pasos
            </p>
          </div>

          <div className="space-y-6 sm:space-y-8">
            <div className="flex gap-4 sm:gap-6 items-start">
              <div className="w-10 h-10 sm:w-12 sm:h-12 bg-teal-500 text-white rounded-full flex items-center justify-center flex-shrink-0 text-base sm:text-lg font-semibold">
                <span>1</span>
              </div>
              <div>
                <h3 className="mb-1 sm:mb-2 text-base sm:text-lg font-semibold">Elige tu método de búsqueda</h3>
                <p className="text-gray-600 text-sm sm:text-base">
                  Selecciona si quieres buscar por conceptos de IA, por un investigador conocido, o combinar ambos criterios 
                  para resultados más precisos.
                </p>
              </div>
            </div>

            <div className="flex gap-4 sm:gap-6 items-start">
              <div className="w-10 h-10 sm:w-12 sm:h-12 bg-teal-500 text-white rounded-full flex items-center justify-center flex-shrink-0 text-base sm:text-lg font-semibold">
                <span>2</span>
              </div>
              <div>
                <h3 className="mb-1 sm:mb-2 text-base sm:text-lg font-semibold">Ingresa tus criterios</h3>
                <p className="text-gray-600 text-sm sm:text-base">
                  Añade conceptos relevantes como "Machine Learning", "Computer Vision", o "NLP", y/o ingresa el nombre 
                  de un investigador que conozcas en el campo.
                </p>
              </div>
            </div>

            <div className="flex gap-4 sm:gap-6 items-start">
              <div className="w-10 h-10 sm:w-12 sm:h-12 bg-teal-500 text-white rounded-full flex items-center justify-center flex-shrink-0 text-base sm:text-lg font-semibold">
                <span>3</span>
              </div>
              <div>
                <h3 className="mb-1 sm:mb-2 text-base sm:text-lg font-semibold">Explora resultados personalizados</h3>
                <p className="text-gray-600 text-sm sm:text-base">
                  Recibe una lista ordenada de investigadores relevantes con métricas de afinidad, información sobre sus 
                  publicaciones, y enlaces directos a sus perfiles ORCID.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* OpenAlex and Concept Hierarchy Section */}
      <div className="py-8 sm:py-12 md:py-16 px-4 sm:px-6 bg-gray-50">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-8 sm:mb-12">
            <h2 className="mb-3 sm:mb-4 text-2xl sm:text-3xl md:text-4xl font-bold">Tecnología y Datos</h2>
          </div>

          <div className="bg-white rounded-xl p-5 sm:p-6 md:p-8 shadow-sm mb-6 sm:mb-8">
            <h3 className="mb-3 sm:mb-4 text-lg sm:text-xl font-semibold">Powered by OpenAlex</h3>
            <p className="text-gray-600 mb-3 sm:mb-4 leading-relaxed text-sm sm:text-base text-justify">
              Colaborador IA utiliza <a href="https://openalex.org" target="_blank" rel="noopener noreferrer" className="text-teal-600 hover:text-teal-700 underline">OpenAlex</a>, 
              una base de datos abierta y completa de producción académica que indexa millones de publicaciones, autores, instituciones y conceptos. 
              OpenAlex permite acceder a información sobre investigadores latinoamericanos en el campo de la Inteligencia Artificial, 
              incluyendo sus publicaciones, colaboraciones y conceptos relacionados.
            </p>
            <p className="text-gray-600 leading-relaxed text-sm sm:text-base text-justify">
              En base a la información obtenida por OpenAlex, es posible alimentar un modelo de recomendación híbrido compuesto por un modelo que genera recomendaciones
              por afinidad temática, y un modelo que genera recomendaciones en base a la red de colaboraciones regional.
            </p>
          </div>

          <div className="bg-white rounded-xl p-5 sm:p-6 md:p-8 shadow-sm mb-6 sm:mb-8">
            <h3 className="mb-3 sm:mb-4 text-lg sm:text-xl font-semibold">Jerarquía de Conceptos</h3>
            <p className="text-gray-600 mb-3 sm:mb-4 leading-relaxed text-sm sm:text-base text-justify">
              OpenAlex organiza los conceptos académicos en una jerarquía multinivel que va desde conceptos amplios hasta temas muy específicos. 
              Los conceptos se organizan de manera jerárquica, similar a un árbol. Existen 19 conceptos raíz, con 6 niveles de descendientes. Esto compone
              aproximadamente 65000 conceptos. Este árbol de conceptos es una versión modificada del creado por <a href='https://arxiv.org/abs/1805.12216' target="_blank" rel="noopener noreferrer" className="text-teal-600 hover:text-teal-700 underline">MAG</a>.
              Una lista comprensiva de todos los conceptos puede ser vista en la siguiente <a href='https://docs.google.com/spreadsheets/d/1LBFHjPt4rj_9r0t0TTAlT68NwOtNH8Z21lBMsJDMoZg/edit?gid=575855905#gid=575855905'
              target="_blank" rel="noopener noreferrer" className="text-teal-600 hover:text-teal-700 underline">hoja de calculo</a>.
            </p>
            <p className="text-gray-600 leading-relaxed text-sm sm:text-base text-justify">
              Es importante asegurar que los conceptos ingresados sigan el nombre establecido por OpenAlex definido dentro de la hoja de cálculo mencionada anteriormente. 
              El buscador ha sido desarrollado para poder encontrar coincidencias ingresando letras que compongan la palabra completa a buscar. 
            </p>
          </div>
          <div className="bg-white rounded-xl p-5 sm:p-6 md:p-8 shadow-sm mb-6 sm:mb-8">
            <h3 className="mb-3 sm:mb-4 text-lg sm:text-xl font-semibold">Búsqueda de Autores</h3>
            <p className="text-gray-600 mb-3 sm:mb-4 leading-relaxed text-sm sm:text-base text-justify">
              La búsqueda en base a redes de colaboracion de latam, se hacen en base a la información proveida por OpenAlex, como tal no toda la información de investigadores
              activos está en el dataset usado por la plataforma. Una forma de obtener que investigadores conforman la plataforma es usando el buscador de la plataforma de <a href='https://openalex.org/' target="_blank" rel="noopener noreferrer" className="text-teal-600 hover:text-teal-700 underline">OpenAlex</a>.
            </p>
          </div>
        </div>
        
      </div>
    </div>
  );
}