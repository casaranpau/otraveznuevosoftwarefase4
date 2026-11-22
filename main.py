"""Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ.
Proyecto académico de Programación (UNAD), Fase 4. No utiliza bases de datos.
Ejecutar con: python main.py
"""
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
import logging
import re

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    filename=LOG_DIR / "software_fj.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8",
)


# --------------------------- Excepciones personalizadas --------------------
class SistemaFJError(Exception):
    """Excepción base del sistema."""


class DatosInvalidosError(SistemaFJError):
    pass


class ServicioNoDisponibleError(SistemaFJError):
    pass


class ReservaInvalidaError(SistemaFJError):
    pass


class OperacionNoPermitidaError(SistemaFJError):
    pass


# --------------------------- Entidades -------------------------------------
class Entidad(ABC):
    """Clase abstracta que representa cualquier entidad del sistema."""
    def __init__(self, identificador):
        if not identificador or not str(identificador).strip():
            raise DatosInvalidosError("El identificador es obligatorio.")
        self._identificador = str(identificador).strip()

    @property
    def identificador(self):
        return self._identificador

    @abstractmethod
    def describir(self):
        pass


class Cliente(Entidad):
    def __init__(self, identificador, nombre, correo, telefono):
        super().__init__(identificador)
        nombre = str(nombre).strip()
        correo = str(correo).strip()
        telefono = str(telefono).strip()
        if len(nombre) < 3:
            raise DatosInvalidosError("El nombre debe tener al menos 3 caracteres.")
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", correo):
            raise DatosInvalidosError("El correo electrónico no tiene un formato válido.")
        if not re.fullmatch(r"[0-9+() -]{7,20}", telefono):
            raise DatosInvalidosError("El teléfono debe contener entre 7 y 20 caracteres válidos.")
        self._nombre = nombre
        self._correo = correo
        self._telefono = telefono

    @property
    def nombre(self):
        return self._nombre

    @property
    def correo(self):
        return self._correo

    @property
    def telefono(self):
        return self._telefono

    def describir(self):
        return f"Cliente {self.identificador}: {self.nombre} ({self.correo})"


# --------------------------- Servicios -------------------------------------
class Servicio(Entidad, ABC):
    def __init__(self, identificador, nombre, tarifa_base, disponible=True):
        super().__init__(identificador)
        if not nombre or not str(nombre).strip():
            raise DatosInvalidosError("El nombre del servicio es obligatorio.")
        if not isinstance(tarifa_base, (int, float)) or tarifa_base <= 0:
            raise DatosInvalidosError("La tarifa base debe ser un número positivo.")
        self._nombre = str(nombre).strip()
        self._tarifa_base = float(tarifa_base)
        self._disponible = bool(disponible)

    @property
    def nombre(self):
        return self._nombre

    @property
    def disponible(self):
        return self._disponible

    def cambiar_disponibilidad(self, disponible):
        self._disponible = bool(disponible)
        logging.info("Disponibilidad de %s cambiada a %s", self.nombre, self._disponible)

    def calcular_costo(self, impuesto=0.0, descuento=0.0):
        """Método con variantes por parámetros opcionales (sobrecarga simulada).
        calcular_costo(); calcular_costo(impuesto); calcular_costo(impuesto, descuento).
        """
        if not (0 <= impuesto <= 1) or not (0 <= descuento <= 1):
            raise DatosInvalidosError("Impuesto y descuento deben estar entre 0 y 1.")
        subtotal = self._tarifa_base
        return round(subtotal * (1 + impuesto) * (1 - descuento), 2)

    @abstractmethod
    def validar_parametros(self, duracion, **kwargs):
        pass

    @abstractmethod
    def describir(self):
        pass


class ReservaSala(Servicio):
    def __init__(self, identificador, tarifa_hora, capacidad, disponible=True):
        super().__init__(identificador, "Reserva de sala", tarifa_hora, disponible)
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise DatosInvalidosError("La capacidad de la sala debe ser un entero positivo.")
        self.capacidad = capacidad

    def validar_parametros(self, duracion, **kwargs):
        asistentes = kwargs.get("asistentes", 1)
        if duracion <= 0 or asistentes <= 0 or asistentes > self.capacidad:
            raise DatosInvalidosError("Duración o cantidad de asistentes inválida para la sala.")

    def calcular_costo(self, duracion=1, impuesto=0.0, descuento=0.0):
        if duracion <= 0:
            raise DatosInvalidosError("La duración debe ser positiva.")
        total = self._tarifa_base * duracion
        if not (0 <= impuesto <= 1 and 0 <= descuento <= 1):
            raise DatosInvalidosError("Impuesto y descuento deben estar entre 0 y 1.")
        return round(total * (1 + impuesto) * (1 - descuento), 2)

    def describir(self):
        return f"{self.nombre}: capacidad para {self.capacidad} personas."


class AlquilerEquipo(Servicio):
    def __init__(self, identificador, tarifa_dia, unidades_disponibles, disponible=True):
        super().__init__(identificador, "Alquiler de equipos", tarifa_dia, disponible)
        if not isinstance(unidades_disponibles, int) or unidades_disponibles < 0:
            raise DatosInvalidosError("Las unidades disponibles deben ser un entero no negativo.")
        self.unidades_disponibles = unidades_disponibles

    def validar_parametros(self, duracion, **kwargs):
        unidades = kwargs.get("unidades", 1)
        if duracion <= 0 or not isinstance(unidades, int) or unidades <= 0:
            raise DatosInvalidosError("Duración o cantidad de equipos inválida.")
        if unidades > self.unidades_disponibles:
            raise ServicioNoDisponibleError("No hay suficientes equipos disponibles.")

    def calcular_costo(self, duracion=1, unidades=1, impuesto=0.0, descuento=0.0):
        if duracion <= 0 or unidades <= 0:
            raise DatosInvalidosError("Duración y unidades deben ser positivas.")
        if not (0 <= impuesto <= 1 and 0 <= descuento <= 1):
            raise DatosInvalidosError("Impuesto y descuento deben estar entre 0 y 1.")
        return round(self._tarifa_base * duracion * unidades * (1 + impuesto) * (1 - descuento), 2)

    def describir(self):
        return f"{self.nombre}: {self.unidades_disponibles} unidades disponibles por día."


class AsesoriaEspecializada(Servicio):
    def __init__(self, identificador, tarifa_hora, especialidad, disponible=True):
        super().__init__(identificador, "Asesoría especializada", tarifa_hora, disponible)
        if not especialidad or not str(especialidad).strip():
            raise DatosInvalidosError("La especialidad de la asesoría es obligatoria.")
        self.especialidad = str(especialidad).strip()

    def validar_parametros(self, duracion, **kwargs):
        if duracion <= 0 or duracion > 8:
            raise DatosInvalidosError("La asesoría debe durar entre 1 y 8 horas.")

    def calcular_costo(self, duracion=1, impuesto=0.0, descuento=0.0):
        if duracion <= 0:
            raise DatosInvalidosError("La duración debe ser positiva.")
        if not (0 <= impuesto <= 1 and 0 <= descuento <= 1):
            raise DatosInvalidosError("Impuesto y descuento deben estar entre 0 y 1.")
        return round(self._tarifa_base * duracion * (1 + impuesto) * (1 - descuento), 2)

    def describir(self):
        return f"{self.nombre} en {self.especialidad}."


# --------------------------- Reserva y gestión -----------------------------
class Reserva(Entidad):
    ESTADOS = ("PENDIENTE", "CONFIRMADA", "CANCELADA")

    def __init__(self, identificador, cliente, servicio, duracion, **parametros):
        super().__init__(identificador)
        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError("La reserva requiere un cliente válido.")
        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError("La reserva requiere un servicio válido.")
        if not servicio.disponible:
            raise ServicioNoDisponibleError(f"El servicio {servicio.nombre} no está disponible.")
        servicio.validar_parametros(duracion, **parametros)
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.parametros = parametros
        self.estado = "PENDIENTE"
        self.costo = None

    def confirmar(self, impuesto=0.0, descuento=0.0):
        if self.estado != "PENDIENTE":
            raise OperacionNoPermitidaError("Solo se puede confirmar una reserva pendiente.")
        try:
            if isinstance(self.servicio, AlquilerEquipo):
                self.costo = self.servicio.calcular_costo(
                    self.duracion, self.parametros.get("unidades", 1), impuesto, descuento
                )
            else:
                self.costo = self.servicio.calcular_costo(self.duracion, impuesto, descuento)
            self.estado = "CONFIRMADA"
            logging.info("Reserva %s confirmada por $%.2f", self.identificador, self.costo)
            return self.costo
        except (DatosInvalidosError, TypeError, ValueError) as exc:
            logging.exception("Error al confirmar reserva %s", self.identificador)
            raise ReservaInvalidaError("No fue posible calcular o confirmar la reserva.") from exc

    def cancelar(self):
        if self.estado == "CANCELADA":
            raise OperacionNoPermitidaError("La reserva ya se encuentra cancelada.")
        self.estado = "CANCELADA"
        logging.info("Reserva %s cancelada", self.identificador)

    def describir(self):
        return (f"Reserva {self.identificador} | Cliente: {self.cliente.nombre} | "
                f"Servicio: {self.servicio.nombre} | Estado: {self.estado} | Costo: {self.costo}")


class SistemaSoftwareFJ:
    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, cliente):
        if any(c.identificador == cliente.identificador for c in self.clientes):
            raise DatosInvalidosError("Ya existe un cliente con ese identificador.")
        self.clientes.append(cliente)
        logging.info("Cliente registrado: %s", cliente.identificador)
        return cliente

    def registrar_servicio(self, servicio):
        if any(s.identificador == servicio.identificador for s in self.servicios):
            raise DatosInvalidosError("Ya existe un servicio con ese identificador.")
        self.servicios.append(servicio)
        logging.info("Servicio registrado: %s", servicio.identificador)
        return servicio

    def crear_reserva(self, reserva):
        if any(r.identificador == reserva.identificador for r in self.reservas):
            raise ReservaInvalidaError("Ya existe una reserva con ese identificador.")
        self.reservas.append(reserva)
        logging.info("Reserva creada: %s", reserva.identificador)
        return reserva


def ejecutar_pruebas():
    sistema = SistemaSoftwareFJ()
    print("\n========== SISTEMA SOFTWARE FJ - DEMOSTRACIÓN ==========")
    operaciones = 0

    def ejecutar(titulo, accion):
        nonlocal operaciones
        operaciones += 1
        print(f"\nOPERACIÓN {operaciones}: {titulo}")
        try:
            resultado = accion()
            print("Correcto:", resultado if resultado is not None else "Operación realizada")
        except Exception as exc:
            logging.exception("Operación %s fallida: %s", operaciones, titulo)
            print(f"Error controlado: {type(exc).__name__}: {exc}")

    # try/except/else/finally: el registro de cliente muestra los cuatro bloques.
    def registrar_cliente_valido():
        try:
            cliente = Cliente("C001", "Laura Gómez", "laura@email.com", "3001234567")
            sistema.registrar_cliente(cliente)
        except DatosInvalidosError:
            print("No se pudo registrar el cliente.")
            raise
        else:
            print("Bloque else: el cliente se registró sin errores.")
            return cliente.describir()
        finally:
            print("Bloque finally: finalizó el intento de registro.")

    ejecutar("Registrar cliente válido", registrar_cliente_valido)
    ejecutar("Rechazar cliente con correo inválido", lambda: sistema.registrar_cliente(
        Cliente("C002", "Carlos Pérez", "correo-invalido", "3015555555")))
    ejecutar("Registrar segundo cliente válido", lambda: sistema.registrar_cliente(
        Cliente("C003", "Andrés Ruiz", "andres@email.com", "3024444444")).describir())
    ejecutar("Crear servicio de sala", lambda: sistema.registrar_servicio(
        ReservaSala("S001", 50000, 12)).describir())
    ejecutar("Crear servicio de alquiler de equipos", lambda: sistema.registrar_servicio(
        AlquilerEquipo("S002", 30000, 5)).describir())
    ejecutar("Crear servicio de asesoría", lambda: sistema.registrar_servicio(
        AsesoriaEspecializada("S003", 80000, "desarrollo de software")).describir())
    ejecutar("Rechazar servicio con tarifa inválida", lambda: ReservaSala("S004", -1000, 10))
    ejecutar("Crear reserva válida de sala", lambda: sistema.crear_reserva(
        Reserva("R001", sistema.clientes[0], sistema.servicios[0], 2, asistentes=8)).describir())
    ejecutar("Confirmar reserva y calcular costo con impuesto", lambda: sistema.reservas[0].confirmar(
        impuesto=0.19))
    ejecutar("Crear reserva de equipos con cantidad no disponible", lambda: Reserva(
        "R002", sistema.clientes[1], sistema.servicios[1], 2, unidades=8))
    ejecutar("Crear y confirmar reserva de asesoría con descuento", lambda: (
        sistema.crear_reserva(Reserva("R003", sistema.clientes[1], sistema.servicios[2], 2)),
        sistema.reservas[-1].confirmar(descuento=0.10))[1])
    ejecutar("Cancelar reserva confirmada", lambda: (sistema.reservas[0].cancelar(), sistema.reservas[0].estado)[1])
    ejecutar("Intentar confirmar nuevamente una reserva cancelada", lambda: sistema.reservas[0].confirmar())
    ejecutar("Intentar reservar un servicio no disponible", lambda: (
        sistema.servicios[0].cambiar_disponibilidad(False),
        Reserva("R004", sistema.clientes[0], sistema.servicios[0], 1, asistentes=2))[1])

    print("\n========================================================")
    print(f"Total de operaciones ejecutadas: {operaciones}")
    print(f"Clientes registrados: {len(sistema.clientes)}")
    print(f"Servicios registrados: {len(sistema.servicios)}")
    print(f"Reservas creadas: {len(sistema.reservas)}")
    print(f"Archivo de eventos y errores: {LOG_DIR / 'software_fj.log'}")
    print("El programa finalizó sin detenerse por los errores controlados.")


if __name__ == "__main__":
    try:
        ejecutar_pruebas()
    except Exception as exc:
        # Última barrera: evita que una excepción inesperada cierre silenciosamente el sistema.
        logging.exception("Error no controlado en la ejecución principal")
        print("Se presentó un error inesperado, registrado en el archivo de logs:", exc)
    finally:
        logging.info("Fin de ejecución del Sistema Software FJ")
