from unittest.mock import AsyncMock, patch

import pytest


class TestResumenUsuarios:
    def test_get_resumen_usuarios_success(self, client, auth_headers):
        with patch(
            "app.api.v1.endpoints.ingresos_diarios.fetch_all",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = [
                {"usuario": "NICOL", "total_recibos": 100, "total": 50000.00},
                {"usuario": "ALEXANDRA", "total_recibos": 80, "total": 40000.00},
            ]

            response = client.get(
                "/api/v1/ingresos/usuarios",
                params={"fecha_inicio": "2025-01-01", "fecha_fin": "2025-01-31"},
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["fecha_inicio"] == "2025-01-01"
            assert data["fecha_fin"] == "2025-01-31"
            assert len(data["data"]) == 2
            assert data["data"][0]["usuario"] == "NICOL"
            assert data["data"][0]["total_recibos"] == 100
            assert data["data"][0]["total"] == 50000.0
            assert data["total_general"] == 90000.0

    def test_get_resumen_usuarios_no_auth(self, client):
        response = client.get(
            "/api/v1/ingresos/usuarios",
            params={"fecha_inicio": "2025-01-01", "fecha_fin": "2025-01-31"},
        )

        assert response.status_code == 401

    def test_get_resumen_usuarios_empty(self, client, auth_headers):
        with patch(
            "app.api.v1.endpoints.ingresos_diarios.fetch_all",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = []

            response = client.get(
                "/api/v1/ingresos/usuarios",
                params={"fecha_inicio": "2025-01-01", "fecha_fin": "2025-01-31"},
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["data"] == []
            assert data["total_general"] == 0


class TestResumenFormasPago:
    def test_get_resumen_formas_pago_success(self, client, auth_headers):
        with patch(
            "app.api.v1.endpoints.ingresos_diarios.fetch_all",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = [
                {"fpago": "Efectivo", "total_recibos": 100, "total": 50000.00},
                {"fpago": "Tarjeta", "total_recibos": 50, "total": 25000.00},
            ]

            response = client.get(
                "/api/v1/ingresos/formas-pago",
                params={"fecha_inicio": "2025-01-01", "fecha_fin": "2025-01-31"},
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["fecha_inicio"] == "2025-01-01"
            assert data["fecha_fin"] == "2025-01-31"
            assert len(data["data"]) == 2
            assert data["data"][0]["fpago"] == "Efectivo"
            assert data["data"][0]["total_recibos"] == 100
            assert data["data"][0]["total"] == 50000.0
            assert data["total_general"] == 75000.0

    def test_get_resumen_formas_pago_no_auth(self, client):
        response = client.get(
            "/api/v1/ingresos/formas-pago",
            params={"fecha_inicio": "2025-01-01", "fecha_fin": "2025-01-31"},
        )

        assert response.status_code == 401

    def test_get_resumen_formas_pago_empty(self, client, auth_headers):
        with patch(
            "app.api.v1.endpoints.ingresos_diarios.fetch_all",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = []

            response = client.get(
                "/api/v1/ingresos/formas-pago",
                params={"fecha_inicio": "2025-01-01", "fecha_fin": "2025-01-31"},
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["data"] == []
            assert data["total_general"] == 0
