import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import './App.css'

type Estado =
  | 'Pendiente'
  | 'En revisión'
  | 'Agendada'
  | 'Atendida'
  | 'Cerrada'
  | 'Cancelada'
type Prioridad = 'Alta' | 'Media' | 'Baja'

type Derivacion = {
  id: number
  especialidad: string
  motivo: string
  prioridad: Prioridad
  estado: Estado
  responsable: string
  observaciones: string | null
  fecha_creacion: string
  fecha_limite: string | null
  atrasada: boolean
}

type Indicadores = {
  total_derivaciones: number
  pendientes: number
  en_revision: number
  agendadas: number
  atendidas: number
  cerradas: number
  canceladas: number
  prioridad_alta: number
  atrasadas: number
}

type AnalisisCopilot = {
  resumen: string
  datos_faltantes: string[]
  calidad_datos: string
  prioridad_sugerida: Prioridad
  justificacion: string
  incertidumbre: string
  limitacion: string
  requiere_revision_humana: true
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

const estados: Estado[] = [
  'Pendiente',
  'En revisión',
  'Agendada',
  'Atendida',
  'Cerrada',
  'Cancelada',
]
const prioridades: Prioridad[] = ['Alta', 'Media', 'Baja']

function formatoFecha(fecha: string | null) {
  if (!fecha) return 'Sin fecha límite'

  return new Intl.DateTimeFormat('es-CL', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(fecha))
}

function App() {
  const [derivaciones, setDerivaciones] = useState<Derivacion[]>([])
  const [indicadores, setIndicadores] = useState<Indicadores | null>(null)
  const [estadoFiltro, setEstadoFiltro] = useState('')
  const [prioridadFiltro, setPrioridadFiltro] = useState('')
  const [cargandoLista, setCargandoLista] = useState(true)
  const [cargandoIndicadores, setCargandoIndicadores] = useState(true)
  const [error, setError] = useState('')
  const [analizandoId, setAnalizandoId] = useState<number | null>(null)
  const [analisis, setAnalisis] = useState<AnalisisCopilot | null>(null)
  const [derivacionAnalizada, setDerivacionAnalizada] = useState<Derivacion | null>(null)

  async function leerRespuesta<T>(respuesta: Response): Promise<T> {
    if (!respuesta.ok) {
      throw new Error('No fue posible obtener la información solicitada.')
    }

    return respuesta.json() as Promise<T>
  }

  async function cargarIndicadores() {
    setCargandoIndicadores(true)
    try {
      const respuesta = await fetch(`${API_BASE_URL}/indicadores`)
      setIndicadores(await leerRespuesta<Indicadores>(respuesta))
    } catch {
      setError('No se pudieron cargar los indicadores. Verifica que la API esté disponible.')
    } finally {
      setCargandoIndicadores(false)
    }
  }

  async function cargarDerivaciones(
    estadoSeleccionado = estadoFiltro,
    prioridadSeleccionada = prioridadFiltro,
  ) {
    setCargandoLista(true)
    setError('')

    const parametros = new URLSearchParams()
    if (estadoSeleccionado) parametros.set('estado', estadoSeleccionado)
    if (prioridadSeleccionada) parametros.set('prioridad', prioridadSeleccionada)
    const consulta = parametros.toString()

    try {
      const respuesta = await fetch(
        `${API_BASE_URL}/derivaciones${consulta ? `?${consulta}` : ''}`,
      )
      setDerivaciones(await leerRespuesta<Derivacion[]>(respuesta))
    } catch {
      setError('No se pudieron cargar las derivaciones. Verifica la conexión con la API.')
      setDerivaciones([])
    } finally {
      setCargandoLista(false)
    }
  }

  useEffect(() => {
    void cargarIndicadores()
    void cargarDerivaciones()
  }, [])

  function aplicarFiltros(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    void cargarDerivaciones()
  }

  function limpiarFiltros() {
    setEstadoFiltro('')
    setPrioridadFiltro('')
    void cargarDerivaciones('', '')
  }

  async function analizarConCopilot(derivacion: Derivacion) {
    setAnalizandoId(derivacion.id)
    setError('')

    try {
      const respuesta = await fetch(
        `${API_BASE_URL}/derivaciones/${derivacion.id}/copilot/analizar`,
        { method: 'POST' },
      )
      setAnalisis(await leerRespuesta<AnalisisCopilot>(respuesta))
      setDerivacionAnalizada(derivacion)
    } catch {
      setError('No se pudo completar el análisis del Copilot. Inténtalo nuevamente.')
    } finally {
      setAnalizandoId(null)
    }
  }

  const tarjetas = indicadores
    ? [
        ['Total de derivaciones', indicadores.total_derivaciones, 'neutral'],
        ['Pendientes', indicadores.pendientes, 'azul'],
        ['En revisión', indicadores.en_revision, 'violeta'],
        ['Agendadas', indicadores.agendadas, 'verde'],
        ['Atendidas', indicadores.atendidas, 'turquesa'],
        ['Cerradas', indicadores.cerradas, 'gris'],
        ['Canceladas', indicadores.canceladas, 'gris'],
        ['Prioridad alta', indicadores.prioridad_alta, 'naranja'],
        ['Atrasadas', indicadores.atrasadas, 'rojo'],
      ]
    : []

  return (
    <main className="app-shell">
      <header className="encabezado">
        <div>
          <p className="etiqueta">HealthBridge · Gestión de derivaciones</p>
          <h1>Panel de seguimiento</h1>
          <p className="subtitulo">
            Consulta administrativa de derivaciones ficticias y apoyo determinista del Copilot.
          </p>
        </div>
        <div className="modo-lectura">Solo lectura</div>
      </header>

      {error && (
        <div className="mensaje-error" role="alert">
          <span>{error}</span>
          <button type="button" onClick={() => setError('')} aria-label="Cerrar mensaje de error">
            Cerrar
          </button>
        </div>
      )}

      <section className="seccion" aria-labelledby="indicadores-titulo">
        <div className="seccion-cabecera">
          <div>
            <p className="eyebrow">Vista general</p>
            <h2 id="indicadores-titulo">Indicadores operativos</h2>
          </div>
          <button className="boton-secundario" type="button" onClick={() => void cargarIndicadores()}>
            Actualizar indicadores
          </button>
        </div>

        {cargandoIndicadores ? (
          <p className="estado-carga">Cargando indicadores…</p>
        ) : (
          <div className="indicadores-grid">
            {tarjetas.map(([titulo, valor, tono]) => (
              <article className={`indicador ${tono}`} key={titulo}>
                <span>{titulo}</span>
                <strong>{valor}</strong>
              </article>
            ))}
          </div>
        )}
      </section>

      <section className="seccion" aria-labelledby="derivaciones-titulo">
        <div className="seccion-cabecera">
          <div>
            <p className="eyebrow">Consulta</p>
            <h2 id="derivaciones-titulo">Derivaciones</h2>
          </div>
          <span className="contador">{derivaciones.length} resultados</span>
        </div>

        <form className="filtros" onSubmit={aplicarFiltros}>
          <label>
            Estado
            <select value={estadoFiltro} onChange={(evento) => setEstadoFiltro(evento.target.value)}>
              <option value="">Todos los estados</option>
              {estados.map((estado) => <option key={estado} value={estado}>{estado}</option>)}
            </select>
          </label>
          <label>
            Prioridad
            <select value={prioridadFiltro} onChange={(evento) => setPrioridadFiltro(evento.target.value)}>
              <option value="">Todas las prioridades</option>
              {prioridades.map((prioridad) => <option key={prioridad} value={prioridad}>{prioridad}</option>)}
            </select>
          </label>
          <div className="acciones-filtro">
            <button className="boton-primario" type="submit">Aplicar filtros</button>
            <button className="boton-texto" type="button" onClick={limpiarFiltros}>Limpiar</button>
          </div>
        </form>

        {cargandoLista ? (
          <p className="estado-carga">Cargando derivaciones…</p>
        ) : derivaciones.length === 0 ? (
          <div className="lista-vacia">
            <strong>No hay derivaciones para mostrar.</strong>
            <span>Prueba con otros filtros o revisa que existan datos ficticios en la API.</span>
          </div>
        ) : (
          <div className="derivaciones-grid">
            {derivaciones.map((derivacion) => (
              <article className="tarjeta-derivacion" key={derivacion.id}>
                <div className="tarjeta-superior">
                  <span className={`badge prioridad-${derivacion.prioridad.toLowerCase()}`}>
                    Prioridad {derivacion.prioridad}
                  </span>
                  <span className="badge estado">{derivacion.estado}</span>
                </div>
                <h3>{derivacion.especialidad}</h3>
                <p className="motivo">{derivacion.motivo}</p>
                <dl>
                  <div><dt>Fecha límite</dt><dd>{formatoFecha(derivacion.fecha_limite)}</dd></div>
                  <div><dt>Seguimiento</dt><dd>{derivacion.atrasada ? 'Atrasada' : 'En plazo o sin fecha límite'}</dd></div>
                </dl>
                {derivacion.atrasada && <p className="alerta-atraso">Requiere revisión por fecha límite vencida.</p>}
                <button
                  className="boton-copilot"
                  type="button"
                  onClick={() => void analizarConCopilot(derivacion)}
                  disabled={analizandoId === derivacion.id}
                >
                  {analizandoId === derivacion.id ? 'Analizando…' : 'Analizar con Copilot'}
                </button>
              </article>
            ))}
          </div>
        )}
      </section>

      {analisis && derivacionAnalizada && (
        <section className="panel-copilot" aria-labelledby="copilot-titulo">
          <div className="seccion-cabecera">
            <div>
              <p className="eyebrow">Referral Copilot</p>
              <h2 id="copilot-titulo">Análisis administrativo</h2>
            </div>
            <button className="boton-texto" type="button" onClick={() => setAnalisis(null)}>Cerrar</button>
          </div>
          <p className="contexto-copilot">Derivación de {derivacionAnalizada.especialidad}</p>
          <div className="analisis-grid">
            <article><span>Calidad de datos</span><strong>{analisis.calidad_datos}</strong></article>
            <article><span>Prioridad sugerida</span><strong>{analisis.prioridad_sugerida}</strong></article>
            <article><span>Revisión humana</span><strong>Obligatoria</strong></article>
          </div>
          <div className="contenido-analisis">
            <div><h3>Resumen</h3><p>{analisis.resumen}</p></div>
            <div><h3>Datos faltantes</h3><p>{analisis.datos_faltantes.length ? analisis.datos_faltantes.join(', ') : 'No se detectaron datos faltantes.'}</p></div>
            <div><h3>Justificación</h3><p>{analisis.justificacion}</p></div>
            <div><h3>Incertidumbre</h3><p>{analisis.incertidumbre}</p></div>
            <div className="limitacion"><h3>Limitación</h3><p>{analisis.limitacion}</p></div>
          </div>
        </section>
      )}
    </main>
  )
}

export default App
