def test_listar_derivaciones_incluye_atrasada(client_con_datos):
    response = client_con_datos.get("/derivaciones")

    assert response.status_code == 200
    derivaciones = response.json()

    assert len(derivaciones) == 3
    assert all("atrasada" in derivacion for derivacion in derivaciones)

    derivacion_pendiente = next(
        derivacion
        for derivacion in derivaciones
        if derivacion["estado"] == "Pendiente"
    )
    derivacion_cerrada = next(
        derivacion
        for derivacion in derivaciones
        if derivacion["estado"] == "Cerrada"
    )
    assert derivacion_pendiente["atrasada"] is True
    assert derivacion_cerrada["atrasada"] is False


def test_listar_derivaciones_filtra_por_estado_pendiente(client_con_datos):
    response = client_con_datos.get("/derivaciones", params={"estado": "Pendiente"})

    assert response.status_code == 200
    derivaciones = response.json()

    assert len(derivaciones) == 1
    assert all(derivacion["estado"] == "Pendiente" for derivacion in derivaciones)


def test_indicadores_devuelve_conteos_coherentes(client_con_datos):
    response = client_con_datos.get("/indicadores")

    assert response.status_code == 200
    assert response.json() == {
        "total_derivaciones": 3,
        "pendientes": 1,
        "en_revision": 0,
        "agendadas": 1,
        "atendidas": 0,
        "cerradas": 1,
        "canceladas": 0,
        "prioridad_alta": 2,
        "atrasadas": 1,
    }
