from abc import ABC, abstractmethod
import logging

from excepciones import (
    DatosInvalidos,
    EstadoReservaInvalido,
    ErrorProcesamientoReserva,
    ServicioNoDisponible,
)

logger = logging.getLogger("software_fj")


class Entidad(ABC):
    @abstractmethod
    def describir(self):
        pass


class Cliente(Entidad):
    def __init__(self, nombre, correo):
        if not isinstance(nombre, str) or not nombre.strip():
            raise DatosInvalidos("El nombre no puede estar vacío")
        if not isinstance(correo, str) or "@" not in correo:
            raise DatosInvalidos("El correo debe incluir @")
        self._nombre = nombre
        self._correo = correo

    @property
    def nombre(self):
        return self._nombre

    @property
    def correo(self):
        return self._correo

    def describir(self):
        return f"Cliente: {self.nombre} ({self.correo})"


class Servicio(Entidad):
    def __init__(self, tarifa_base, disponible=True):
        if (not isinstance(tarifa_base, (int, float))
                or isinstance(tarifa_base, bool) or tarifa_base <= 0):
            raise DatosInvalidos("La tarifa base debe ser un número positivo")
        self.tarifa_base = tarifa_base
        self.disponible = disponible

    def validar_disponibilidad(self):
        if not self.disponible:
            raise ServicioNoDisponible("El servicio no está disponible")

    @abstractmethod
    def calcular_costo(self, unidades):
        pass

    @abstractmethod
    def describir(self):
        pass

    def costo_final(self, unidades, impuesto=0, descuento=0):
        if not 0 <= impuesto <= 1:
            raise ValueError("El impuesto debe estar entre 0 y 1")
        if not 0 <= descuento <= 1:
            raise ValueError("El descuento debe estar entre 0 y 1")
        subtotal = self.calcular_costo(unidades)
        return round(subtotal * (1 - descuento) * (1 + impuesto), 2)


class Sala(Servicio):
    def calcular_costo(self, unidades):
        if (not isinstance(unidades, (int, float)) or isinstance(unidades, bool)
                or unidades <= 0):
            raise ValueError("Las horas de sala deben ser positivas")
        return self.tarifa_base * unidades

    def describir(self):
        return f"Sala por hora: ${self.tarifa_base}"


class AlquilerEquipo(Servicio):
    def calcular_costo(self, unidades):
        if not isinstance(unidades, int) or isinstance(unidades, bool) or unidades <= 0:
            raise ValueError("Los días de alquiler deben ser un entero positivo")
        return self.tarifa_base * unidades

    def describir(self):
        return f"Alquiler de equipo por día: ${self.tarifa_base}"


class Asesoria(Servicio):
    def calcular_costo(self, unidades):
        if (not isinstance(unidades, (int, float)) or isinstance(unidades, bool)
                or unidades < 1):
            raise ValueError("La asesoría requiere mínimo una hora")
        return self.tarifa_base * unidades

    def describir(self):
        return f"Asesoría por hora: ${self.tarifa_base}"


class Reserva(Entidad):
    def __init__(self, cliente, servicio, unidades):
        if not isinstance(cliente, Cliente):
            raise DatosInvalidos("La reserva requiere un cliente válido")
        if not isinstance(servicio, Servicio):
            raise DatosInvalidos("La reserva requiere un servicio válido")
        servicio.validar_disponibilidad()
        servicio.calcular_costo(unidades)
        self.cliente = cliente
        self.servicio = servicio
        self.unidades = unidades
        self.estado = "Pendiente"

    def describir(self):
        return (
            f"Reserva para {self.cliente.nombre}: "
            f"{self.servicio.describir()}, {self.unidades} unidades, "
            f"estado {self.estado}"
        )

    def confirmar(self):
        if self.estado != "Pendiente":
            raise EstadoReservaInvalido(
                "Solo se puede confirmar una reserva pendiente"
            )
        self.servicio.validar_disponibilidad()
        self.estado = "Confirmada"
        logger.info("Reserva confirmada: %s", self.describir())

    def procesar(self, impuesto=0, descuento=0):
        try:
            if self.estado != "Confirmada":
                raise EstadoReservaInvalido(
                    "Solo se procesa una reserva confirmada"
                )
            self.servicio.validar_disponibilidad()
            return self.servicio.costo_final(
                self.unidades, impuesto=impuesto, descuento=descuento
            )
        except Exception as error:
            logger.exception("Falló el procesamiento de la reserva")
            raise ErrorProcesamientoReserva(
                "No se pudo procesar la reserva"
            ) from error

    def cancelar(self):
        if self.estado == "Cancelada":
            raise EstadoReservaInvalido("La reserva ya está cancelada")
        self.estado = "Cancelada"
        logger.info("Reserva cancelada: %s", self.describir())


class GestorReservas:
    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def agregar_cliente(self, cliente):
        self.clientes.append(cliente)
        logger.info("Cliente agregado: %s", cliente.describir())

    def agregar_servicio(self, servicio):
        self.servicios.append(servicio)
        logger.info("Servicio agregado: %s", servicio.describir())

    def agregar_reserva(self, reserva):
        self.reservas.append(reserva)
        logger.info("Reserva agregada: %s", reserva.describir())
