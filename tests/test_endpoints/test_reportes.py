from unittest.mock import patch

import pytest


class TestReportes:
    def test_crear_recibo_success(self, client, auth_headers):
        payload = {
            "idnum": 1234,
            "cliente": "Juan Perez",
            "monto": 1500.00,
        }

        response = client.post(
            "/api/v1/reportes/recibo",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert "recibo_1234" in response.headers.get("content-disposition", "")

    def test_crear_recibo_no_auth(self, client):
        payload = {
            "idnum": 1234,
            "cliente": "Juan Perez",
            "monto": 1500.00,
        }

        response = client.post(
            "/api/v1/reportes/recibo",
            json=payload,
        )

        assert response.status_code == 401

    def test_crear_recibo_invalid_data(self, client, auth_headers):
        payload = {
            "idnum": "invalid",
        }

        response = client.post(
            "/api/v1/reportes/recibo",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_crear_reporte_ventas_termico_success(self, client, auth_headers):
        payload = {
            "desde": "2025-01-01",
            "hasta": "2025-01-31",
            "metodos_pago": ["Efectivo", "Tarjeta"],
        }

        with patch("app.api.v1.endpoints.reportes.fetch_all") as mock_resumen:
            mock_resumen.return_value = [
                {
                    "descrip": "Membresia Mensual",
                    "total": 1500.00,
                    "tipo_pago": "Efectivo",
                },
                {
                    "descrip": "Clase Personalizada",
                    "total": 500.00,
                    "tipo_pago": "Tarjeta",
                },
            ]

            response = client.post(
                "/api/v1/reportes/ventas-termico",
                json=payload,
                headers=auth_headers,
            )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert "attachment" in response.headers.get("content-disposition", "")

    def test_crear_reporte_ventas_termico_no_auth(self, client):
        payload = {
            "desde": "2025-01-01",
            "hasta": "2025-01-31",
        }

        response = client.post(
            "/api/v1/reportes/ventas-termico",
            json=payload,
        )

        assert response.status_code == 401

    def test_crear_reporte_ventas_termico_invalid_data(self, client, auth_headers):
        payload = {
            "desde": "invalid-date",
        }

        response = client.post(
            "/api/v1/reportes/ventas-termico",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 422
