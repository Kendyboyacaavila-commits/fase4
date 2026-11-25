from abc import ABC, abstractmethod
from datetime import datetime

# primero esta es la gerarquia de excepciones personalizadas
class ErrorSistemaFJ(Exception):
    pass


class ValidacionError(ErrorSistemaFJ):
    pass


class ServicioNoDisponibleError(ErrorSistemaFJ):
    pass


class ReservaInvalidaError(ErrorSistemaFJ):
    pass


class CalculoCostoError(ErrorSistemaFJ):
    pass

# aqui esta el sistema de auditoria y registro de logs
class RegistradorLogs:
    def __init__(self, ruta_archivo: str = "eventos_software_fj.log"):
        self.ruta_archivo = ruta_archivo

    def registrar(self, nivel: str, mensaje: str) -> None:
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linea = f"[{fecha}] [{nivel.upper()}] {mensaje}\n"
        try:
            with open(self.ruta_archivo, "a", encoding="utf-8") as archivo:
                archivo.write(linea)
        except OSError as err:
            print(f"Error escribiendo log: {err}")

# esta es la clase base abstracta y entidades del dominio
class EntidadSistema(ABC):#representa cualquien estidad i dentificable del sistema
    def __init__(self, entidad_id: str):
        if not entidad_id or not entidad_id.strip():
            raise ValidacionError("El ID no puede estar vacío.")
        self._id = entidad_id.strip()
        self._fecha_creacion = datetime.now()

    @property
    def id(self) -> str:
        return self._id

    @abstractmethod
    def obtener_resumen(self) -> str:
        pass


class Cliente(EntidadSistema):#representa un cliente con atributos y validaciones
    def __init__(self, cliente_id: str, nombre: str, documento: str, correo: str):
        super().__init__(cliente_id)
        self.nombre = nombre
        self.documento = documento
        self.correo = correo

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not valor or len(valor.strip()) < 3:
            raise ValidacionError("El nombre debe tener mínimo 3 caracteres.")
        self.__nombre = valor.strip()

    @property
    def documento(self) -> str:
        return self.__documento

    @documento.setter
    def documento(self, valor: str) -> None:
        if not valor or not valor.strip().isdigit() or len(valor.strip()) < 5:
            raise ValidacionError("El documento debe ser numérico de mínimo 5 dígitos.")
        self.__documento = valor.strip()

    @property
    def correo(self) -> str:
        return self.__correo

    @correo.setter
    def correo(self, valor: str) -> None:
        if not valor or "@" not in valor or "." not in valor.split("@")[-1]:
            raise ValidacionError(f"Correo inválido: '{valor}'.")
        self.__correo = valor.strip().lower()

    def obtener_resumen(self) -> str:
        return f"Cliente [{self.id}] {self.nombre} | Doc: {self.documento} | Email: {self.correo}"

# esta es la gerarquia de servicios
class Servicio(EntidadSistema, ABC):#aqui se define la estructuracomun de todos los serviciosque se ofrecen
    def __init__(self, servicio_id: str, nombre: str, tarifa_base: float, disponible: bool = True):
        super().__init__(servicio_id)
        self._nombre = nombre
        self._tarifa_base = tarifa_base
        self._disponible = disponible
        self.validar_parametros()

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, estado: bool) -> None:
        self._disponible = bool(estado)

    @abstractmethod
    def validar_parametros(self) -> None:
        if not self._nombre or not self._nombre.strip():
            raise ValidacionError("El nombre del servicio es obligatorio.")
        if self._tarifa_base <= 0:
            raise ValidacionError("La tarifa base debe ser mayor a cero.")

    @abstractmethod
    def describir_servicio(self) -> str:
        pass

    @abstractmethod
    def calcular_costo(self, duracion: int, impuesto: float = 0.19, descuento: float = 0.0) -> float:
        pass

    def obtener_resumen(self) -> str:
        return f"Servicio [{self.id}] {self.nombre} - {self.describir_servicio()}"

class ReservaSala(Servicio):#aqui esta el servicio para salas por horas
    def __init__(self, servicio_id: str, nombre: str, tarifa_hora: float, capacidad: int, disponible: bool = True):
        self.capacidad = capacidad
        super().__init__(servicio_id, nombre, tarifa_hora, disponible)

    def validar_parametros(self) -> None:
        super().validar_parametros()
        if self.capacidad <= 0:
            raise ValidacionError("La capacidad de la sala debe ser mayor a cero.")

    def describir_servicio(self) -> str:
        return f"Sala (Capacidad: {self.capacidad} personas, Tarifa/hora: ${self._tarifa_base:,.2f})"

    def calcular_costo(self, duracion: int, impuesto: float = 0.19, descuento: float = 0.0) -> float:
        if duracion <= 0:
            raise CalculoCostoError("Las horas deben ser mayores a cero.")
        subtotal = (self._tarifa_base * duracion) * (1 - descuento)
        return round(subtotal * (1 + impuesto), 2)
    #aquiii
class AlquilerEquipo(Servicio):#aqui se encuentra el servicio para alquiler de equipos
    def __init__(self, servicio_id: str, nombre: str, tarifa_dia: float, cantidad_stock: int):
        self.cantidad_stock = cantidad_stock
        super().__init__(servicio_id, nombre, tarifa_dia, disponible=cantidad_stock > 0)

    def validar_parametros(self) -> None:
        super().validar_parametros()
        if self.cantidad_stock < 0:
            raise ValidacionError("El stock no puede ser negativo.")

    def describir_servicio(self) -> str:
        return f"Equipo (Stock: {self.cantidad_stock}, Tarifa/día: ${self._tarifa_base:,.2f})"

    def calcular_costo(self, duracion: int, impuesto: float = 0.19, descuento: float = 0.0) -> float:
        if duracion <= 0:
            raise CalculoCostoError("Los días deben ser mayores a cero.")
        subtotal = ((self._tarifa_base * duracion) + 15000.0) * (1 - descuento)
        return round(subtotal * (1 + impuesto), 2)


class AsesoriaEspecializada(Servicio):# aqui servicio de consultoria tecnica por sesiones
    def __init__(self, servicio_id: str, nombre: str, tarifa_sesion: float, especialidad: str, disponible: bool = True):
        self.especialidad = especialidad
        super().__init__(servicio_id, nombre, tarifa_sesion, disponible)

    def validar_parametros(self) -> None:
        super().validar_parametros()
        if not self.especialidad or not self.especialidad.strip():
            raise ValidacionError("Debe indicar la especialidad.")

    def describir_servicio(self) -> str:
        return f"Asesoría {self.especialidad} (Tarifa/sesión: ${self._tarifa_base:,.2f})"

    def calcular_costo(self, duracion: int, impuesto: float = 0.19, descuento: float = 0.0) -> float:
        if duracion <= 0:
            raise CalculoCostoError("Las sesiones deben ser mayores a cero.")
        desc_total = min(0.9, descuento + (0.05 if duracion >= 4 else 0.0))
        subtotal = (self._tarifa_base * duracion) * (1 - desc_total)
        return round(subtotal * (1 + impuesto), 2)

# aqui esta gestion de reservas y controlador principal
class Reserva(EntidadSistema):
    def __init__(self, reserva_id: str, cliente: Cliente, servicio: Servicio, duracion: int):
        super().__init__(reserva_id)
        if not isinstance(cliente, Cliente) or not isinstance(servicio, Servicio) or duracion <= 0:
            raise ReservaInvalidaError("Datos inválidos para crear la reserva.")
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "PENDIENTE"
        self.costo_total = 0.0

    def procesar(self, impuesto: float = 0.19, descuento: float = 0.0) -> None:#se verifica la disponibilidad y calcula el costo
        try:
            if not self.servicio.disponible:
                raise ServicioNoDisponibleError(f"Servicio '{self.servicio.nombre}' no disponible.")
            if isinstance(self.servicio, AlquilerEquipo) and self.servicio.cantidad_stock <= 0:
                raise ServicioNoDisponibleError(f"Sin stock para '{self.servicio.nombre}'.")
            self.costo_total = self.servicio.calcular_costo(self.duracion, impuesto, descuento)
        except (ServicioNoDisponibleError, CalculoCostoError) as err:
            self.estado = "FALLIDA"
            raise ReservaInvalidaError(f"Error procesando reserva {self.id}: {err}") from err

    def confirmar(self) -> None:#para confirmar una reserva y actualizar el inventario
        if self.estado in ("CANCELADA", "FALLIDA") or self.costo_total <= 0:
            raise ReservaInvalidaError("No se puede confirmar esta reserva.")
        if isinstance(self.servicio, AlquilerEquipo):
            self.servicio.cantidad_stock -= 1
            if self.servicio.cantidad_stock == 0:
                self.servicio.disponible = False
        self.estado = "CONFIRMADA"

    def cancelar(self) -> None:#para cancelar y restaurar stock
        if self.estado == "CANCELADA":
            raise ReservaInvalidaError("La reserva ya está cancelada.")
        if self.estado == "CONFIRMADA" and isinstance(self.servicio, AlquilerEquipo):
            self.servicio.cantidad_stock += 1
            self.servicio.disponible = True
        self.estado = "CANCELADA"

    def obtener_resumen(self) -> str:
        return f"Reserva [{self.id}] | {self.estado} | {self.cliente.nombre} | {self.servicio.nombre} | Total: ${self.costo_total:,.2f}"

#este es el contyrolador central, administra listas y coordina operaciones
class GestorSoftwareFJ:
    def __init__(self, logger: RegistradorLogs):
        self.clientes: list[Cliente] = []
        self.servicios: list[Servicio] = []
        self.reservas: list[Reserva] = []
        self.logger = logger

    def registrar_cliente(self, cliente: Cliente) -> bool:#registra y evita duplicados
        try:
            if any(c.id == cliente.id or c.documento == cliente.documento for c in self.clientes):
                raise ErrorSistemaFJ(f"Cliente duplicado: {cliente.id}")
            self.clientes.append(cliente)
        except ErrorSistemaFJ as err:
            self.logger.registrar("ERROR", str(err))
            print(f"[ERROR] {err}")
            return False
        else:
            self.logger.registrar("INFO", cliente.obtener_resumen())
            print(f"[OK] {cliente.obtener_resumen()}")
            return True
        finally:
            self.logger.registrar("AUDIT", "Fin intento registro cliente.")
# para agregar un nuevo servicio
    def agregar_servicio(self, servicio: Servicio) -> bool:
        try:
            if any(s.id == servicio.id for s in self.servicios):
                raise ErrorSistemaFJ(f"Servicio duplicado: {servicio.id}")
            self.servicios.append(servicio)
        except ErrorSistemaFJ as err:
            self.logger.registrar("ERROR", str(err))
            print(f"[ERROR] {err}")
            return False
        else:
            self.logger.registrar("INFO", servicio.obtener_resumen())
            print(f"[OK] {servicio.obtener_resumen()}")
            return True
#aqui se crea y confirma una reserva
    def crear_reserva(self, res_id: str, cliente: Cliente, servicio: Servicio, duracion: int, imp: float = 0.19, desc: float = 0.0) -> Reserva | None:
        reserva = None
        try:
            reserva = Reserva(res_id, cliente, servicio, duracion)
            reserva.procesar(imp, desc)
            reserva.confirmar()
        except ErrorSistemaFJ as err:
            self.logger.registrar("ERROR", str(err))
            print(f"[FALLO RESERVA] {err}")
            if reserva:
                self.reservas.append(reserva)
            return None
        else:
            self.reservas.append(reserva)
            self.logger.registrar("INFO", reserva.obtener_resumen())
            print(f"[RESERVA OK] {reserva.obtener_resumen()}")
            return reserva
        finally:
            self.logger.registrar("AUDIT", f"Ciclo reserva {res_id} cerrado.")

# esta es la simulacion de operaciones del sistema
def ejecutar_simulacion():
    logger = RegistradorLogs()
    gestor = GestorSoftwareFJ(logger)
    logger.registrar("INFO", "INICIO SIMULACIÓN")

    c1 = Cliente("CLI-01", "Laura Gómez", "10203040", "laura@empresa.com")
    gestor.registrar_cliente(c1)

    c2 = Cliente("CLI-02", "Carlos Ruiz", "98765432", "carlos@tech.co")
    gestor.registrar_cliente(c2)

    try:
        gestor.registrar_cliente(Cliente("CLI-03", "Ana", "112233", "correo_malo.com"))
    except ErrorSistemaFJ as err:
        logger.registrar("ERROR", str(err))
        print(f"[ERROR] {err}")

    gestor.registrar_cliente(Cliente("CLI-01", "Laura Duplicada", "10203040", "otra@empresa.com"))

    s1 = ReservaSala("SRV-01", "Sala Innovación A", 85000.0, 12)# se crra tres tipos de servicios especializados
    gestor.agregar_servicio(s1)

    s2 = AlquilerEquipo("SRV-02", "Workstation Dell", 120000.0, 1)
    gestor.agregar_servicio(s2)

    s3 = AsesoriaEspecializada("SRV-03", "Arquitectura Cloud", 200000.0, "AWS")
    gestor.agregar_servicio(s3)

    try:
        gestor.agregar_servicio(ReservaSala("SRV-04", "Sala Error", -50000.0, 5))
    except ErrorSistemaFJ as err:
        logger.registrar("ERROR", str(err))
        print(f"[ERROR] {err}")

    gestor.crear_reserva("RES-01", c1, s1, 3)
    gestor.crear_reserva("RES-02", c2, s2, 2, desc=0.10)
    gestor.crear_reserva("RES-03", c1, s2, 1)

    r4 = gestor.crear_reserva("RES-04", c2, s3, 4, imp=0.19, desc=0.05)
    if r4:
        try:
            r4.cancelar()
            logger.registrar("INFO", f"Cancelada: {r4.obtener_resumen()}")
            print(f"[CANCELACIÓN OK] {r4.obtener_resumen()}")
        except ErrorSistemaFJ as err:
            logger.registrar("ERROR", str(err))

    print(f"\nResumen -> Clientes: {len(gestor.clientes)} | Servicios: {len(gestor.servicios)} | Reservas: {len(gestor.reservas)}")
    logger.registrar("INFO", "FIN SIMULACIÓN")
ejecutar_simulacion()
