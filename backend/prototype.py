paciente = {
    "nombre": "Paciente Demo",
    "edad": 35,
    "rut": "11.111.111-1",
    "sexo": "Masculino",
    "activo": True
}

derivacion = {
    "id": 1,
    "paciente_rut": paciente["rut"],
    "especialidad": "Cardiología",
    "motivo": "Evaluación por dolor torácico",
    "prioridad": "Alta",
    "estado": "Pendiente",
    "responsable": "Unidad de Cardiología",
    "observaciones": "Sin observaciones"
}

derivacion_2 = {
    "id": 2,
    "paciente_rut": paciente["rut"],
    "especialidad": "Traumatología",
    "motivo": "Evaluación por dolor de rodilla",
    "prioridad": "Media",
    "estado": "Pendiente",
    "responsable": "Unidad de Traumatología",
    "observaciones": "Sin observaciones"
}

derivacion_3 = {
    "id": 3,
    "paciente_rut": paciente["rut"],
    "especialidad": "Dermatología",
    "motivo": "Evaluación por erupción cutánea",
    "prioridad": "Baja",
    "estado": "Pendiente",
    "responsable": "Unidad de Dermatología",
    "observaciones": "Sin observaciones"
}

derivaciones = [derivacion, derivacion_2, derivacion_3]


def registrar_derivacion(paciente_actual, lista_derivaciones):
    print()
    print("=== REGISTRAR NUEVA DERIVACIÓN ===")

    especialidad = input("Especialidad: ").strip()
    motivo = input("Motivo: ").strip()

    prioridad = input(
        "Prioridad (Alta, Media, Baja): "
    ).strip().capitalize()

    while prioridad not in ["Alta", "Media", "Baja"]:
        print("Prioridad no válida.")
        prioridad = input(
            "Prioridad (Alta, Media, Baja): "
        ).strip().capitalize()

    responsable = input("Responsable: ").strip()
    observaciones = input("Observaciones: ").strip()

    nueva_derivacion = {
        "id": len(lista_derivaciones) + 1,
        "paciente_rut": paciente_actual["rut"],
        "especialidad": especialidad,
        "motivo": motivo,
        "prioridad": prioridad,
        "estado": "Pendiente",
        "responsable": responsable,
        "observaciones": observaciones
    }

    return nueva_derivacion


def mostrar_paciente(paciente_actual):
    print()
    print("=== PACIENTE ===")
    print("Nombre:", paciente_actual["nombre"])
    print("Edad:", paciente_actual["edad"])
    print("RUT:", paciente_actual["rut"])
    print("Sexo:", paciente_actual["sexo"])
    print("Activo:", paciente_actual["activo"])


def mostrar_derivaciones(lista_derivaciones):
    print()
    print("=== LISTADO DE DERIVACIONES ===")

    for derivacion_actual in lista_derivaciones:
        print("ID:", derivacion_actual["id"])
        print("Paciente RUT:", derivacion_actual["paciente_rut"])
        print("Especialidad:", derivacion_actual["especialidad"])
        print("Motivo:", derivacion_actual["motivo"])
        print("Prioridad:", derivacion_actual["prioridad"])

        if derivacion_actual["prioridad"] == "Alta":
            print("¡Esta derivación tiene prioridad alta!")
        elif derivacion_actual["prioridad"] == "Media":
            print("Esta derivación tiene prioridad media.")
        else:
            print("Esta derivación tiene prioridad baja.")

        print("Estado:", derivacion_actual["estado"])
        print("Responsable:", derivacion_actual["responsable"])
        print("Observaciones:", derivacion_actual["observaciones"])
        print()


nueva_derivacion = registrar_derivacion(paciente, derivaciones)
derivaciones.append(nueva_derivacion)

mostrar_paciente(paciente)
mostrar_derivaciones(derivaciones)