# =========================================================
# 4. GESTOR EN MEMORIA
# =========================================================
class GestorSoftwareFJ:
    """Administra listas internas de clientes, servicios y reservas con control de excepciones."""

    def _init_(self, logger: RegistradorLogs):
        self.clientes: list[Cliente] = []
        self.servicios: list[Servicio] = []
        self.reservas: list[Reserva] = []
        self.logger = logger

    def registrar_cliente(self, cliente: Cliente) -> bool:
        try:
            if any(c.id == cliente.id or c.documento == cliente.documento for c in self.clientes):
                raise ErrorSistemaFJ(f"Cliente duplicado con ID {cliente.id} o documento {cliente.documento}.")
            self.clientes.append(cliente)
        except ErrorSistemaFJ as err:
            self.logger.registrar("ERROR", f"Registro de cliente fallido: {err}")
            print(f"[ERROR CONTROLADO] {err}")
            return False
        else:
            self.logger.registrar("INFO", f"Cliente registrado: {cliente.obtener_resumen()}")
            print(f"[OK] {cliente.obtener_resumen()}")
            return True
        finally:
            self.logger.registrar("AUDIT", "Intento de operación registrar_cliente finalizado.")

    def agregar_servicio(self, servicio: Servicio) -> bool:
        try:
            if any(s.id == servicio.id for s in self.servicios):
                raise ErrorSistemaFJ(f"Ya existe un servicio con ID {servicio.id}.")
            self.servicios.append(servicio)
        except ErrorSistemaFJ as err:
            self.logger.registrar("ERROR", f"Creación de servicio fallida: {err}")
            print(f"[ERROR CONTROLADO] {err}")
            return False
        else:
            self.logger.registrar("INFO", f"Servicio agregado: {servicio.obtener_resumen()}")
            print(f"[OK] {servicio.obtener_resumen()}")
            return True

    def crear_y_confirmar_reserva(
        self,
        reserva_id: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion: int,
        impuesto: float = 0.19,
        descuento: float = 0.0,
    ) -> Reserva | None:
        reserva = None
        try:
            reserva = Reserva(reserva_id, cliente, servicio, duracion)
            reserva.procesar(impuesto=impuesto, descuento=descuento)
            reserva.confirmar()
        except ErrorSistemaFJ as err:
            self.logger.registrar("ERROR", f"Error en reserva {reserva_id}: {err}")
            print(f"[RESERVA FALLIDA] {err}")
            if reserva is not None:
                self.reservas.append(reserva)
            return None
        else:
            self.reservas.append(reserva)
            self.logger.registrar("INFO", f"Reserva confirmada: {reserva.obtener_resumen()}")
            print(f"[RESERVA EXITOSA] {reserva.obtener_resumen()}")
            return reserva
        finally:
            self.logger.registrar("AUDIT", f"Ciclo de reserva {reserva_id} cerrado.")


# =========================================================
# 5. SIMULACIÓN DE 12 OPERACIONES (PUNTO DE ENTRADA)
# =========================================================
def ejecutar_simulacion():
    logger = RegistradorLogs("eventos_software_fj.log")
    gestor = GestorSoftwareFJ(logger)
    logger.registrar("INFO", "=== INICIO DE SIMULACIÓN SOFTWARE FJ ===")

    print("--- 1. REGISTRO DE CLIENTES (VÁLIDOS E INVÁLIDOS) ---")
    c1 = Cliente("CLI-01", "Laura Gómez", "10203040", "laura@empresa.com")
    gestor.registrar_cliente(c1)

    c2 = Cliente("CLI-02", "Carlos Ruiz", "98765432", "carlos@tech.co")
    gestor.registrar_cliente(c2)

    try:
        c_invalido = Cliente("CLI-03", "Ana", "112233", "correo_invalido.com")
        gestor.registrar_cliente(c_invalido)
    except ErrorSistemaFJ as err:
        logger.registrar("ERROR", f"Instanciación inválida de cliente: {err}")
        print(f"[ERROR CONTROLADO] {err}")

    c_duplicado = Cliente("CLI-01", "Laura Duplicada", "10203040", "otra@empresa.com")
    gestor.registrar_cliente(c_duplicado)

    print("\n--- 2. CREACIÓN DE SERVICIOS (CORRECTOS E INCORRECTOS) ---")
    s1 = ReservaSala("SRV-01", "Sala Innovación A", 85000.0, capacidad=12)
    gestor.agregar_servicio(s1)

    s2 = AlquilerEquipo("SRV-02", "Workstation Dell Precision", 120000.0, cantidad_stock=1)
    gestor.agregar_servicio(s2)

    s3 = AsesoriaEspecializada("SRV-03", "Arquitectura Cloud", 200000.0, especialidad="AWS & Microservicios")
    gestor.agregar_servicio(s3)

    try:
        s_invalido = ReservaSala("SRV-04", "Sala Error", -50000.0, capacidad=5)
        gestor.agregar_servicio(s_invalido)
    except ErrorSistemaFJ as err:
        logger.registrar("ERROR", f"Instanciación inválida de servicio: {err}")
        print(f"[ERROR CONTROLADO] {err}")

    print("\n--- 3. PROCESAMIENTO DE RESERVAS (EXITOSAS Y FALLIDAS) ---")
    gestor.crear_y_confirmar_reserva("RES-01", c1, s1, duracion=3)
    gestor.crear_y_confirmar_reserva("RES-02", c2, s2, duracion=2, descuento=0.10)
    gestor.crear_y_confirmar_reserva("RES-03", c1, s2, duracion=1)

    r4 = gestor.crear_y_confirmar_reserva("RES-04", c2, s3, duracion=4, impuesto=0.19, descuento=0.05)
    if r4:
        try:
            r4.cancelar()
            logger.registrar("INFO", f"Reserva cancelada correctamente: {r4.obtener_resumen()}")
            print(f"[CANCELACIÓN OK] {r4.obtener_resumen()}")
        except ErrorSistemaFJ as err:
            logger.registrar("ERROR", str(err))

    print("\n--- RESUMEN FINAL EN MEMORIA ---")
    print(f"Total Clientes: {len(gestor.clientes)} | Total Servicios: {len(gestor.servicios)} | Total Reservas: {len(gestor.reservas)}")
    logger.registrar("INFO", "=== FIN DE SIMULACIÓN SOFTWARE FJ ===")


if _name_ == "_main_":
    ejecutar_simulacion()
