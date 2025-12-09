import {Target, Network, TrendingUp, Users, BookOpen, Lightbulb } from 'lucide-react';

export default function About() {
  return (
    <div className="min-h-screen">
      {/* Mission Section */}
      <div className="py-16 px-6 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl mb-4">Acerca de</h2>
            <p className="text-gray-600 max-w-3xl mx-auto text-lg text-start">
				Esta plataforma surge frente a la baja colaboración entre investigadores en inteligencia artificial dentro de Latinoamérica, 
				una situación destacada en el último reporte de ILIA (2024). Su objetivo es ofrecer una primera herramienta que facilite el 
				descubrimiento de investigadores en la región con quienes establecer colaboraciones.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-teal-100 rounded-xl flex items-center justify-center mx-auto mb-4">
                <Network className="w-8 h-8 text-teal-600" />
              </div>
              <h3 className="mb-2">Conectar</h3>
              <p className="text-gray-600">
                Facilitar conexiones entre investigadores con intereses afines en toda América Latina
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-teal-100 rounded-xl flex items-center justify-center mx-auto mb-4">
                <Lightbulb className="w-8 h-8 text-teal-600" />
              </div>
              <h3 className="mb-2">Descubrir</h3>
              <p className="text-gray-600">
                Ayudar a encontrar nuevas oportunidades de colaboración basadas en perfiles académicos
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-teal-100 rounded-xl flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="w-8 h-8 text-teal-600" />
              </div>
              <h3 className="mb-2">Impulsar</h3>
              <p className="text-gray-600">
                Fortalecer la investigación regional mediante colaboraciones estratégicas y efectivas
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-16 px-6 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl mb-4">Características Principales</h2>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {/* Feature 1 */}
            <div className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-teal-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Target className="w-6 h-6 text-teal-600" />
                </div>
                <div>
                  <h3 className="mb-2">Búsqueda por Conceptos</h3>
                  <p className="text-gray-600">
                    Ingresa los temas de IA que te interesan y encuentra investigadores trabajando en áreas similares. 
                  </p>
                </div>
              </div>
            </div>

            {/* Feature 2 */}
            <div className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-teal-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Users className="w-6 h-6 text-teal-600" />
                </div>
                <div>
                  <h3 className="mb-2">Análisis de Redes de Coautoría</h3>
                  <p className="text-gray-600">
                    Descubre investigadores a través de sus conexiones académicas. Si conoces a un investigador, 
                    podemos recomendarte otros en base a la red de colaboración regional.
                  </p>
                </div>
              </div>
            </div>

            {/* Feature 3 */}
            <div className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-teal-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <BookOpen className="w-6 h-6 text-teal-600" />
                </div>
                <div>
					<h3 className="mb-2">Información Relevante</h3>
					<p className="text-gray-600">
						Explora información relevante acerca de los investigadores recomendados, como información personal y 
						sus ultimas publicaciones.
					</p>
                </div>
              </div>
            </div>

            {/* Feature 4 */}
            <div className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-teal-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Network className="w-6 h-6 text-teal-600" />
                </div>
                <div>
                  <h3 className="mb-2">Búsqueda Híbrida</h3>
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
            <h2 className="mb-4 text-3xl">¿Cómo Funciona?</h2>
            <p className="text-gray-600 text-lg">
              Encuentra colaboradores en tres simples pasos
            </p>
          </div>

          <div className="space-y-8">
            <div className="flex gap-6 items-start">
              <div className="w-12 h-12 bg-teal-500 text-white rounded-full flex items-center justify-center flex-shrink-0">
                <span>1</span>
              </div>
              <div>
                <h3 className="mb-2">Elige tu método de búsqueda</h3>
                <p className="text-gray-600">
                  Selecciona si quieres buscar por conceptos de IA, por un investigador conocido, o combinar ambos criterios 
                  para resultados más precisos.
                </p>
              </div>
            </div>

            <div className="flex gap-6 items-start">
              <div className="w-12 h-12 bg-teal-500 text-white rounded-full flex items-center justify-center flex-shrink-0">
                <span>2</span>
              </div>
              <div>
                <h3 className="mb-2">Ingresa tus criterios</h3>
                <p className="text-gray-600">
                  Añade conceptos relevantes como "Machine Learning", "Computer Vision", o "NLP", y/o ingresa el nombre 
                  de un investigador que conozcas en el campo.
                </p>
              </div>
            </div>

            <div className="flex gap-6 items-start">
              <div className="w-12 h-12 bg-teal-500 text-white rounded-full flex items-center justify-center flex-shrink-0">
                <span>3</span>
              </div>
              <div>
                <h3 className="mb-2">Explora resultados personalizados</h3>
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
      <div className="py-16 px-6 bg-gray-50">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="mb-4 text-3xl">Tecnología y Datos</h2>
          </div>

          <div className="bg-white rounded-xl p-8 shadow-sm mb-8">
            <h3 className="mb-4">Powered by OpenAlex</h3>
            <p className="text-gray-600 mb-4 leading-relaxed">
              Colaborador IA utiliza <a href="https://openalex.org" target="_blank" rel="noopener noreferrer" className="text-teal-600 hover:text-teal-700 underline">OpenAlex</a>, 
              una base de datos abierta y completa de producción académica que indexa millones de publicaciones, autores, instituciones y conceptos. 
              OpenAlex permite acceder a información sobre investigadores latinoamericanos en el campo de la Inteligencia Artificial, 
              incluyendo sus publicaciones, colaboraciones y conceptos relacionados.
            </p>
            <p className="text-gray-600 leading-relaxed">
				En base a la información obtenida por OpenAlex, es posible alimentar un modelo de recomendación híbrido compuesto por un modelo que genera recomendaciones
				por afinidad temática, y un modelo que genera recomendaciones en base a la red de colaboraciones regional.
            </p>
          </div>

          <div className="bg-white rounded-xl p-8 shadow-sm">
            <h3 className="mb-4">Jerarquía de Conceptos</h3>
            <p className="text-gray-600 mb-4 leading-relaxed">
              OpenAlex organiza los conceptos académicos en una jerarquía multinivel que va desde conceptos amplios hasta temas muy específicos. 
              Los conceptos se organizan de manera jerárquica, similar a un árbol. Existen 19 conceptos raíz, con 6 niveles de descendientes. Esto compone
			  aproximadamente 65000 conceptos. Este árbol de conceptos es una versión modificada del creado por <a href='https://arxiv.org/abs/1805.12216' target="_blank" rel="noopener noreferrer" className="text-teal-600 hover:text-teal-700 underline">MAG</a>.
			  Una lista comprensiva de todos los conceptos puede ser vista en la siguiente <a href='https://docs.google.com/spreadsheets/d/1LBFHjPt4rj_9r0t0TTAlT68NwOtNH8Z21lBMsJDMoZg/edit?gid=575855905#gid=575855905'
			  target="_blank" rel="noopener noreferrer" className="text-teal-600 hover:text-teal-700 underline">hoja de calculo</a>.
            </p>
			<p className="text-gray-600 mb-4 leading-relaxed">
				Es importante asegurar que los conceptos ingresados sigan el nombre establecido por OpenAlex definido dentro de la hoja de cálculo mencionada anteriormente. 
				El buscador ha sido desarrollado para poder encontrar coincidencias ingresando letras que compongan la palabra completa a buscar. 
			</p>
          </div>
        </div>
      </div>
    </div>
  );
}