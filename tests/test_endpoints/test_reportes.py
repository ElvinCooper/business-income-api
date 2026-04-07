from unittest.mock import patch

import pytest


class TestReportes:
    def test_crear_reporte_ventas_termico_success(self, client, auth_headers):
        payload = {
            "empresa": "BlueGym",
            "direccion": "Av. Principal 123",
            "telefono": "809-555-1234",
            "rnc": "123456789",
            "desde": "2025-01-01",
            "hasta": "2025-01-31",
            "fecha_impresion": "2025-01-31 10:00",
            "usuario": "admin",
            "items": [
                {"descripcion": "Membresia Mensual", "valor": 1500.00},
                {"descripcion": "Clase Personalizada", "valor": 500.00},
            ],
            "total": 2000.00,
            "pagos": [
                {"tipo": "Efectivo", "valor": 1500.00},
                {"tipo": "Tarjeta", "valor": 500.00},
            ],
        }

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
            "empresa": "BlueGym",
            "direccion": "Av. Principal 123",
            "telefono": "809-555-1234",
            "rnc": "123456789",
            "desde": "2025-01-01",
            "hasta": "2025-01-31",
            "fecha_impresion": "2025-01-31 10:00",
            "usuario": "admin",
            "items": [{"descripcion": "Membresia", "valor": 1000.00}],
            "total": 1000.00,
            "pagos": [{"tipo": "Efectivo", "valor": 1000.00}],
        }

        response = client.post(
            "/api/v1/reportes/ventas-termico",
            json=payload,
        )

        assert response.status_code == 401

    def test_crear_reporte_ventas_termico_invalid_data(self, client, auth_headers):
        payload = {
            "empresa": "BlueGym",
        }

        response = client.post(
            "/api/v1/reportes/ventas-termico",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 422
