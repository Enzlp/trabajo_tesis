import { Globe, Target, Network, TrendingUp, Users, BookOpen, Lightbulb, Sparkles } from 'lucide-react';


export default function About() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-teal-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-br from-teal-50 via-cyan-50 to-white py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-teal-500 to-cyan-600 rounded-2xl mb-6 shadow-xl">
            <Sparkles className="w-12 h-12 text-white" />
          </div>
          <h1 className="text-xl font-bold mb-6 bg-gradient-to-r from-teal-600 to-cyan-600 bg-clip-text text-transparent">
            Conectando la investigación en IA de América Latina
          </h1>
          <p className="text-xl text-gray-600 mb-8 leading-relaxed">
            Esta plataforma surge como respuesta a la baja colaboración entre investigadores en inteligencia artificial en Latinoamérica, 
            un fenómeno destacado en el reporte de ILIA 2024. Su objetivo es ofrecer una herramienta exploratoria que facilite el 
            descubrimiento de investigadores en la región con quienes se podrían establecer colaboraciones académicas.
          </p>
        </div>
      </div>

      {/* Mission Section */}
      <div className="py-16 px-6 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center bg-gradient-to-br from-teal-50 to-cyan-50 rounded-2xl p-8 border border-teal-100">
              <div className="w-16 h-16 bg-gradient-to-br from-teal-500 to-cyan-600 rounded-xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                <Network className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Conectar</h3>
              <p className="text-gray-600">
                Facilitar conexiones iniciales entre investigadores con intereses afines en toda Latinoamérica.
              </p>
            </div>

            <div className="text-center bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-8 border border-purple-100">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                <Lightbulb className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Descubrir</h3>
              <p className="text-gray-600">
                Ayudar a identificar nuevas oportunidades de colaboración basadas en perfiles académicos y áreas de interés.
              </p>
            </div>

            <div className="text-center bg-gradient-to-br from-blue-50 to-cyan-50 rounded-2xl p-8 border border-blue-100">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                <TrendingUp className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Impulsar</h3>
              <p className="text-gray-600">
                Apoyar la creación de redes de colaboración y fortalecer la investigación regional mediante la exploración de relaciones existentes en la red de coautoría.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-16 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Características Principales</h2>
            <p className="text-gray-600 text-lg">
              Herramientas potentes para encontrar los colaboradores perfectos
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Feature 1 */}
            <div className="bg-white rounded-2xl p-6 shadow-md hover:shadow-xl transition-all duration-300 border border-gray-100">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-gradient-to-br from-teal-100 to-cyan-100 rounded-xl flex items-center justify-center flex-shrink-0">
                  <Target className="w-6 h-6 text-teal-600" />
                </div>
                <div>
                  <h3 className="font-semibold mb-2">Búsqueda por Conceptos</h3>
                  <p className="text-gray-600">
                    Ingresa los temas relacionados con inteligencia artificial en inglés que te interesan y encuentra investigadores trabajando en áreas similares.
                  </p>
                </div>
              </div>
            </div>

            {/* Feature 2 */}
            <div className="bg-white rounded-2xl p-6 shadow-md hover:shadow-xl transition-all duration-300 border border-gray-100">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-gradient-to-br from-purple-100 to-pink-100 rounded-xl flex items-center justify-center flex-shrink-0">
                  <Users className="w-6 h-6 text-purple-600" />
                </div>
                <div>
                  <h3 className="font-semibold mb-2">Análisis de Redes de Coautoría</h3>
                  <p className="text-gray-600">
                    Descubre investigadores a través de sus conexiones académicas. Si conoces a un investigador, 
                    podemos recomendarte otros en base a la red de colaboración regional.
                  </p>
                </div>
              </div>
            </div>

            {/* Feature 3 */}
            <div className="bg-white rounded-2xl p-6 shadow-md hover:shadow-xl transition-all duration-300 border border-gray-100">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-100 to-cyan-100 rounded-xl flex items-center justify-center flex-shrink-0">
                  <BookOpen className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold mb-2">Información Relevante</h3>
                  <p className="text-gray-600">
                    Explora información relevante acerca de los investigadores recomendados, como información personal y 
                    sus últimas publicaciones.
                  </p>
                </div>
              </div>
            </div>

            {/* Feature 4 */}
            <div className="bg-white rounded-2xl p-6 shadow-md hover:shadow-xl transition-all duration-300 border border-gray-100">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-gradient-to-br from-green-100 to-teal-100 rounded-xl flex items-center justify-center flex-shrink-0">
                  <Network className="w-6 h-6 text-green-600" />
                </div>
                <div>
                  <h3 className="font-semibold mb-2">Búsqueda Híbrida</h3>
                  <p className="text-gray-600">
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
      <div className="py-16 px-6 bg-white">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">¿Cómo Funciona?</h2>
            <p className="text-gray-600 text-lg">
              Encuentra colaboradores en tres simples pasos
            </p>
          </div>

          <div className="space-y-6">
            <div className="flex gap-6 items-start bg-gradient-to-r from-teal-50 to-cyan-50 rounded-2xl p-6 border border-teal-100">
              <div className="w-12 h-12 bg-gradient-to-br from-teal-500 to-cyan-600 text-white rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg font-semibold">
                <span>1</span>
              </div>
              <div>
                <h3 className="font-semibold mb-2">Elige tu método de búsqueda</h3>
                <p className="text-gray-600">
                  Selecciona si quieres buscar por conceptos de IA, por un investigador conocido, o combinar ambos criterios 
                  para resultados más precisos.
                </p>
              </div>
            </div>

            <div className="flex gap-6 items-start bg-gradient-to-r from-purple-50 to-pink-50 rounded-2xl p-6 border border-purple-100">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-600 text-white rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg font-semibold">
                <span>2</span>
              </div>
              <div>
                <h3 className="font-semibold mb-2">Ingresa tus criterios</h3>
                <p className="text-gray-600">
                  Añade conceptos relevantes como "Machine Learning", "Computer Vision", o "NLP", y/o ingresa el nombre 
                  de un investigador que conozcas en el campo.
                </p>
              </div>
            </div>

            <div className="flex gap-6 items-start bg-gradient-to-r from-blue-50 to-cyan-50 rounded-2xl p-6 border border-blue-100">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-cyan-600 text-white rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg font-semibold">
                <span>3</span>
              </div>
              <div>
                <h3 className="font-semibold mb-2">Explora resultados personalizados</h3>
                <p className="text-gray-600">
                  Recibe una lista ordenada de investigadores relevantes con métricas de afinidad, información sobre sus 
                  publicaciones, y enlaces directos a sus perfiles ORCID.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* OpenAlex and Concept Hierarchy Section */}
      <div className="py-16 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Tecnología y Datos</h2>
          </div>

          <div className="bg-white rounded-2xl p-8 shadow-xl mb-8 border border-gray-100">
            <div className="flex items-start gap-4 mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-teal-100 to-cyan-100 rounded-xl flex items-center justify-center flex-shrink-0">
                <Globe className="w-6 h-6 text-teal-600" />
              </div>
              <h3 className="text-xl font-semibold">Powered by OpenAlex</h3>
            </div>
            <p className="text-gray-600 mb-4 leading-relaxed">
              Colaborador IA utiliza <a href="https://openalex.org" target="_blank" rel="noopener noreferrer" className="text-teal-600 hover:text-teal-700 underline">OpenAlex</a>, 
              una base de datos abierta y completa de producción académica que indexa millones de publicaciones, autores, instituciones y conceptos. 
              Esta plataforma trabaja con un snapshot de OpenAlex, por lo que algunos datos pueden no estar completamente actualizados. 
              Para obtener la información más reciente sobre un investigador o sus publicaciones, puedes visitar el enlace al perfil correspondiente en OpenAlex que se incluye en cada recomendación. 
              OpenAlex permite acceder a información sobre investigadores latinoamericanos en el campo de la Inteligencia Artificial, incluyendo sus publicaciones, colaboraciones y conceptos relacionados.
            </p>
            <p className="text-gray-600 leading-relaxed">
              En base a la información obtenida por OpenAlex, es posible alimentar un modelo de recomendación híbrido compuesto por un modelo que genera recomendaciones
              por afinidad temática, y un modelo que genera recomendaciones en base a la red de colaboraciones regional.
            </p>
          </div>

          <div className="bg-white rounded-2xl p-8 shadow-xl mb-8 border border-gray-100">
            <div className="flex items-start gap-4 mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-100 to-pink-100 rounded-xl flex items-center justify-center flex-shrink-0">
                <Network className="w-6 h-6 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold">Jerarquía de Conceptos</h3>
            </div>
            <p className="text-gray-600 mb-4 leading-relaxed">
              OpenAlex organiza los conceptos académicos en una jerarquía multinivel que va desde conceptos amplios hasta temas muy específicos. 
              Los conceptos se organizan de manera jerárquica, similar a un árbol. Existen 19 conceptos raíz, con 6 niveles de descendientes. Esto compone
              aproximadamente 65000 conceptos. Este árbol de conceptos es una versión modificada del creado por <a href='https://arxiv.org/abs/1805.12216' target="_blank" rel="noopener noreferrer" className="text-teal-600 hover:text-teal-700 underline">MAG</a>.
              Una lista comprensiva de todos los conceptos puede ser vista en la siguiente <a href='https://docs.google.com/spreadsheets/d/1LBFHjPt4rj_9r0t0TTAlT68NwOtNH8Z21lBMsJDMoZg/edit?gid=575855905#gid=575855905'
              target="_blank" rel="noopener noreferrer" className="text-teal-600 hover:text-teal-700 underline">hoja de cálculo</a>.
            </p>
            <p className="text-gray-600 leading-relaxed">
              Es importante asegurar que los conceptos ingresados sigan el nombre establecido por OpenAlex definido dentro de la hoja de cálculo mencionada anteriormente. 
              El buscador ha sido desarrollado para poder encontrar coincidencias ingresando letras que compongan la palabra completa a buscar.
            </p>
          </div>

          <div className="bg-white rounded-2xl p-8 shadow-xl border border-gray-100">
            <div className="flex items-start gap-4 mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-100 to-cyan-100 rounded-xl flex items-center justify-center flex-shrink-0">
                <Users className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold">Búsqueda de Autores</h3>
            </div>
            <p className="text-gray-600 leading-relaxed">
              La búsqueda en base a redes de colaboración de latam, se hacen en base a la información proveída por OpenAlex, como tal no toda la información de investigadores
              activos está en el dataset usado por la plataforma. Una forma de obtener qué investigadores conforman la plataforma es usando el buscador de la plataforma de <a href='https://openalex.org/' target="_blank" rel="noopener noreferrer" className="text-teal-600 hover:text-teal-700 underline">OpenAlex</a>.
            </p>
          </div>
        </div>
      </div>


    </div>
  );
}