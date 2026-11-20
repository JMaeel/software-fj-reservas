import logging

from excepciones import (
    DatosInvalidos,
    EstadoReservaInvalido,
    ErrorProcesamientoReserva,
    ServicioNoDisponible,
)
from modelos import (
    Asesoria,
    AlquilerEquipo,
    Cliente,
    GestorReservas,
    Reserva,
    Sala,
)

logging.basicConfig(
    filename="software_fj.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger("software_fj")


def main():
    print("Sistema de reservas Software FJ")

    # Prueba de un cliente con correo inválido.
    try:
        Cliente("Ana", "correo-invalido")
    except ValueError as error:
        print("Error capturado:", error)
        logger.exception("Error al registrar un cliente")

    # Creación del cliente válido.
    cliente1 = Cliente("Ana", "ana@example.com")
    print(cliente1.nombre)
    print(cliente1.correo)
    print(cliente1.describir())

    # Creación y procesamiento de una reserva de sala.
    sala = Sala(50000)
    reserva1 = Reserva(cliente1, sala, 2)
    print(reserva1.describir())

    try:
        reserva1.confirmar()
    except EstadoReservaInvalido as error:
        print("No se pudo confirmar:", error)
        logger.exception("Error al confirmar la reserva")
    else:
        print("Estado después de confirmar:", reserva1.estado)
        print(
            "Costo procesado:",
            reserva1.procesar(impuesto=0.19, descuento=0.10),
        )
    finally:
        print("Finalizó el intento de confirmación")

    reserva1.cancelar()
    print("Estado después de cancelar:", reserva1.estado)

    try:
        reserva1.procesar()
    except ErrorProcesamientoReserva as error:
        print("Error de procesamiento capturado:", error)
        print("Causa original:", error.__cause__)

    try:
        reserva1.cancelar()
    except EstadoReservaInvalido as error:
        print("Error de estado capturado:", error)
        logger.exception("Intento de cancelar una reserva ya cancelada")

    print(sala.describir())
    print("Costo por 2 horas:", sala.calcular_costo(2))

    # Creación y cálculo de un alquiler de equipo.
    equipo = AlquilerEquipo(80000)
    print(equipo.describir())
    print("Costo por 3 días:", equipo.calcular_costo(3))

    # Creación y cálculo de una asesoría.
    asesoria = Asesoria(100000)
    print(asesoria.describir())
    print("Costo por 2 horas:", asesoria.calcular_costo(2))

    try:
        Sala(-10000)
    except DatosInvalidos as error:
        print("Servicio inválido capturado:", error)
        logger.exception("Intento de crear un servicio con tarifa inválida")

    sala_cerrada = Sala(30000, disponible=False)
    try:
        Reserva(cliente1, sala_cerrada, 1)
    except ServicioNoDisponible as error:
        print("Reserva rechazada:", error)
        logger.exception("Intento de reservar un servicio no disponible")

    print(
        "Costo con impuesto y descuento:",
        sala.costo_final(2, impuesto=0.19, descuento=0.10),
    )

    # Prueba de días inválidos para el alquiler.
    try:
        equipo.calcular_costo(1.5)
    except ValueError as error:
        print("Error de duración capturado:", error)
        logger.exception("Duración inválida para el alquiler")

    gestor = GestorReservas()
    gestor.agregar_cliente(cliente1)
    gestor.agregar_servicio(sala)
    gestor.agregar_servicio(equipo)
    gestor.agregar_servicio(asesoria)
    gestor.agregar_reserva(reserva1)

    print("Clientes guardados:", len(gestor.clientes))
    print("Servicios guardados:", len(gestor.servicios))
    print("Reservas guardadas:", len(gestor.reservas))

    # Prueba de una asesoría menor a una hora.
    try:
        asesoria.calcular_costo(0.5)
    except ValueError as error:
        print("Error de asesoría capturado:", error)
        logger.exception("Duración inválida para la asesoría")


if __name__ == "__main__":
    main()
