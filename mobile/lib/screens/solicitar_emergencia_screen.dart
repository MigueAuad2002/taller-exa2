//solicitar_emergencia_screen.dart
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import '../theme/app_theme.dart';
import '../widgets/ev_widgets.dart';
import '../services/emergencia_service.dart';

// Tipos de emergencia disponibles
const _tiposEmergencia = [
  _TipoEmergencia(
    valor: 'bateria',
    label: 'Batería descargada',
    icon: Icons.battery_alert_rounded,
  ),
  _TipoEmergencia(
    valor: 'neumatico',
    label: 'Neumático pinchado',
    icon: Icons.tire_repair_rounded,
  ),
  _TipoEmergencia(
    valor: 'combustible',
    label: 'Sin combustible',
    icon: Icons.local_gas_station_outlined,
  ),
  _TipoEmergencia(
    valor: 'motor',
    label: 'Falla de motor',
    icon: Icons.settings_outlined,
  ),
  _TipoEmergencia(
    valor: 'accidente',
    label: 'Accidente vehicular',
    icon: Icons.car_crash_outlined,
  ),
  _TipoEmergencia(
    valor: 'otro',
    label: 'Otro problema',
    icon: Icons.help_outline_rounded,
  ),
];

class SolicitarEmergenciaScreen extends StatefulWidget {
  const SolicitarEmergenciaScreen({super.key});

  @override
  State<SolicitarEmergenciaScreen> createState() =>
      _SolicitarEmergenciaScreenState();
}

class _SolicitarEmergenciaScreenState
    extends State<SolicitarEmergenciaScreen> {
  final _formKey = GlobalKey<FormState>();
  final _descripcionController = TextEditingController();
  final _referenciaController = TextEditingController();
  final _evidenciaController = TextEditingController();

  String? _tipoSeleccionado;
  Position? _posicion;
  bool _cargandoUbicacion = false;
  bool _enviando = false;
  String? _errorUbicacion;

  // Paso actual del stepper: 0 = tipo, 1 = ubicación, 2 = detalles
  int _pasoActual = 0;

  @override
  void initState() {
    super.initState();
    _obtenerUbicacion(); // intentar al abrir
  }

  @override
  void dispose() {
    _descripcionController.dispose();
    _referenciaController.dispose();
    _evidenciaController.dispose();
    super.dispose();
  }

  // ── GPS ────────────────────────────────────────────────────────────────
  Future<void> _obtenerUbicacion() async {
    setState(() {
      _cargandoUbicacion = true;
      _errorUbicacion = null;
    });

    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        throw Exception('El GPS está desactivado. Activalo en ajustes.');
      }

      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          throw Exception('Se necesita permiso de ubicación para continuar.');
        }
      }
      if (permission == LocationPermission.deniedForever) {
        throw Exception(
            'Permiso denegado permanentemente. Habilitalo en Ajustes > Aplicaciones.');
      }

      final pos = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );

      setState(() => _posicion = pos);
    } catch (e) {
      setState(() => _errorUbicacion = e.toString().replaceAll('Exception: ', ''));
    } finally {
      setState(() => _cargandoUbicacion = false);
    }
  }

  // ── Enviar ─────────────────────────────────────────────────────────────
  Future<void> _enviarEmergencia() async {
    if (_tipoSeleccionado == null) {
      _mostrarError('Seleccioná el tipo de emergencia.');
      return;
    }
    if (_posicion == null) {
      _mostrarError('No se pudo obtener tu ubicación. Intentá de nuevo.');
      return;
    }
    if (!_formKey.currentState!.validate()) return;

    setState(() => _enviando = true);

    try {
      final evidencia = _evidenciaController.text.trim();

      final resultado = await EmergenciaService().crearEmergencia(
        tipoEmergencia: _tipoSeleccionado!,
        latitud: _posicion!.latitude,
        longitud: _posicion!.longitude,
        prioridad: 'MEDIA',
        descripcion: _descripcionController.text.trim(),
        referencia: _referenciaController.text.trim(),
        evidencias: [evidencia],
      );

      if (!mounted) return;
      _mostrarExito(resultado['nro_emergencia']);
    } catch (e) {
      if (!mounted) return;
      _mostrarError(e.toString().replaceAll('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _enviando = false);
    }
  }

  void _mostrarError(String msg) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      content: Text(msg),
      backgroundColor: AppTheme.error,
    ));
  }

  void _mostrarExito(dynamic nroEmergencia) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        contentPadding: const EdgeInsets.all(28),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 56,
              height: 56,
              decoration: BoxDecoration(
                color: AppTheme.success.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.check_circle_outline_rounded,
                  color: AppTheme.success, size: 32),
            ),
            const SizedBox(height: 16),
            const Text(
              '¡Emergencia enviada!',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w800,
                color: AppTheme.textPrimary,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Solicitud N° $nroEmergencia registrada correctamente.',
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 13,
                color: AppTheme.textSecondary,
                height: 1.5,
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context); // cierra dialog
                Navigator.pop(context); // vuelve al home
              },
              child: const Text('VOLVER AL INICIO'),
            ),
          ],
        ),
      ),
    );
  }

  // ── Build ───────────────────────────────────────────────────────────────
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('SOLICITAR AUXILIO'),
        backgroundColor: AppTheme.primary,
        foregroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 18),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Column(
        children: [
          // ── Stepper indicador ──────────────────────────────────────
          _StepIndicator(pasoActual: _pasoActual),

          // ── Contenido por paso ─────────────────────────────────────
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // PASO 0 — Tipo de emergencia
                    _PasoTipo(
                      activo: _pasoActual == 0,
                      completado: _pasoActual > 0,
                      tipoSeleccionado: _tipoSeleccionado,
                      onTipoSeleccionado: (tipo) {
                        setState(() {
                          _tipoSeleccionado = tipo;
                          _pasoActual = 1;
                        });
                      },
                    ),
                    const SizedBox(height: 16),

                    // PASO 1 — Ubicación GPS
                    _PasoUbicacion(
                      activo: _pasoActual == 1,
                      completado: _pasoActual > 1,
                      posicion: _posicion,
                      cargando: _cargandoUbicacion,
                      error: _errorUbicacion,
                      onReintentar: _obtenerUbicacion,
                      onConfirmar: _posicion != null
                          ? () => setState(() => _pasoActual = 2)
                          : null,
                    ),
                    const SizedBox(height: 16),

                    // PASO 2 — Detalles
                    _PasoDetalles(
                      activo: _pasoActual == 2,
                      descripcionController: _descripcionController,
                      referenciaController: _referenciaController,
                      evidenciaController: _evidenciaController,
                    ),
                  ],
                ),
              ),
            ),
          ),

          // ── Botón enviar (solo en paso 2) ──────────────────────────
          if (_pasoActual == 2)
            _BarraEnviar(
              enviando: _enviando,
              onEnviar: _enviarEmergencia,
            ),
        ],
      ),
    );
  }
}

// ── Step Indicator ────────────────────────────────────────────────────────────
class _StepIndicator extends StatelessWidget {
  final int pasoActual;
  const _StepIndicator({required this.pasoActual});

  @override
  Widget build(BuildContext context) {
    const pasos = ['Tipo', 'Ubicación', 'Detalles'];
    return Container(
      color: AppTheme.surface,
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
      child: Row(
        children: List.generate(pasos.length * 2 - 1, (i) {
          if (i.isOdd) {
            // línea conectora
            final completado = (i ~/ 2) < pasoActual;
            return Expanded(
              child: Container(
                height: 2,
                color: completado ? AppTheme.primary : AppTheme.border,
              ),
            );
          }
          final idx = i ~/ 2;
          final completado = idx < pasoActual;
          final activo = idx == pasoActual;
          return Column(
            children: [
              AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                width: 28,
                height: 28,
                decoration: BoxDecoration(
                  color: completado || activo
                      ? AppTheme.primary
                      : AppTheme.background,
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: completado || activo
                        ? AppTheme.primary
                        : AppTheme.border,
                    width: 1.5,
                  ),
                ),
                child: Center(
                  child: completado
                      ? const Icon(Icons.check_rounded,
                          color: Colors.white, size: 14)
                      : Text(
                          '${idx + 1}',
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                            color: activo
                                ? Colors.white
                                : AppTheme.textSecondary,
                          ),
                        ),
                ),
              ),
              const SizedBox(height: 4),
              Text(
                pasos[idx],
                style: TextStyle(
                  fontSize: 10,
                  fontWeight:
                      activo ? FontWeight.w700 : FontWeight.w400,
                  color: activo
                      ? AppTheme.primary
                      : AppTheme.textSecondary,
                ),
              ),
            ],
          );
        }),
      ),
    );
  }
}

// ── Paso 0 — Tipo ─────────────────────────────────────────────────────────────
class _PasoTipo extends StatelessWidget {
  final bool activo;
  final bool completado;
  final String? tipoSeleccionado;
  final void Function(String) onTipoSeleccionado;

  const _PasoTipo({
    required this.activo,
    required this.completado,
    required this.tipoSeleccionado,
    required this.onTipoSeleccionado,
  });

  @override
  Widget build(BuildContext context) {
    return _PasoCard(
      numero: '01',
      titulo: 'Tipo de emergencia',
      subtitulo: 'Seleccioná qué le pasó a tu vehículo',
      activo: activo,
      completado: completado,
      child: GridView.count(
        crossAxisCount: 2,
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        crossAxisSpacing: 10,
        mainAxisSpacing: 10,
        childAspectRatio: 2.4,
        children: _tiposEmergencia.map((tipo) {
          final selected = tipoSeleccionado == tipo.valor;
          return InkWell(
            onTap: () => onTipoSeleccionado(tipo.valor),
            borderRadius: BorderRadius.circular(6),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 150),
              padding:
                  const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
              decoration: BoxDecoration(
                color: selected
                    ? AppTheme.primary
                    : AppTheme.background,
                borderRadius: BorderRadius.circular(6),
                border: Border.all(
                  color: selected ? AppTheme.primary : AppTheme.border,
                  width: selected ? 1.5 : 1,
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    tipo.icon,
                    size: 16,
                    color: selected ? Colors.white : AppTheme.textSecondary,
                  ),
                  const SizedBox(width: 6),
                  Expanded(
                    child: Text(
                      tipo.label,
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                        color: selected
                            ? Colors.white
                            : AppTheme.textPrimary,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
            ),
          );
        }).toList(),
      ),
    );
  }
}

// ── Paso 1 — Ubicación ────────────────────────────────────────────────────────
class _PasoUbicacion extends StatelessWidget {
  final bool activo;
  final bool completado;
  final Position? posicion;
  final bool cargando;
  final String? error;
  final VoidCallback onReintentar;
  final VoidCallback? onConfirmar;

  const _PasoUbicacion({
    required this.activo,
    required this.completado,
    required this.posicion,
    required this.cargando,
    required this.error,
    required this.onReintentar,
    required this.onConfirmar,
  });

  @override
  Widget build(BuildContext context) {
    return _PasoCard(
      numero: '02',
      titulo: 'Tu ubicación',
      subtitulo: 'Necesitamos saber dónde estás',
      activo: activo,
      completado: completado,
      child: Column(
        children: [
          // Estado GPS
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: posicion != null
                  ? AppTheme.success.withOpacity(0.06)
                  : error != null
                      ? AppTheme.error.withOpacity(0.06)
                      : AppTheme.primary.withOpacity(0.06),
              borderRadius: BorderRadius.circular(6),
              border: Border.all(
                color: posicion != null
                    ? AppTheme.success.withOpacity(0.3)
                    : error != null
                        ? AppTheme.error.withOpacity(0.3)
                        : AppTheme.primary.withOpacity(0.2),
              ),
            ),
            child: cargando
                ? const Row(
                    children: [
                      SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: AppTheme.primary,
                        ),
                      ),
                      SizedBox(width: 10),
                      Text(
                        'Obteniendo ubicación...',
                        style: TextStyle(
                          fontSize: 13,
                          color: AppTheme.textSecondary,
                        ),
                      ),
                    ],
                  )
                : posicion != null
                    ? Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Row(
                            children: [
                              Icon(Icons.location_on_rounded,
                                  color: AppTheme.success, size: 16),
                              SizedBox(width: 6),
                              Text(
                                'Ubicación obtenida',
                                style: TextStyle(
                                  fontSize: 13,
                                  fontWeight: FontWeight.w700,
                                  color: AppTheme.success,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 6),
                          Text(
                            'Lat: ${posicion!.latitude.toStringAsFixed(6)}\n'
                            'Lng: ${posicion!.longitude.toStringAsFixed(6)}',
                            style: const TextStyle(
                              fontSize: 11,
                              fontFamily: 'monospace',
                              color: AppTheme.textSecondary,
                              height: 1.6,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'Precisión: ±${posicion!.accuracy.toStringAsFixed(0)}m',
                            style: const TextStyle(
                              fontSize: 11,
                              color: AppTheme.textSecondary,
                            ),
                          ),
                        ],
                      )
                    : Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              const Icon(Icons.location_off_outlined,
                                  color: AppTheme.error, size: 16),
                              const SizedBox(width: 6),
                              Expanded(
                                child: Text(
                                  error ?? 'No se pudo obtener la ubicación',
                                  style: const TextStyle(
                                    fontSize: 12,
                                    color: AppTheme.error,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              // Reintentar
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: cargando ? null : onReintentar,
                  icon: const Icon(Icons.refresh_rounded, size: 16),
                  label: const Text('Reintentar'),
                  style: OutlinedButton.styleFrom(
                    minimumSize: const Size(0, 44),
                    textStyle: const TextStyle(
                        fontSize: 12, fontWeight: FontWeight.w600),
                  ),
                ),
              ),
              if (posicion != null) ...[
                const SizedBox(width: 10),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: onConfirmar,
                    icon: const Icon(Icons.check_rounded, size: 16),
                    label: const Text('Confirmar'),
                    style: ElevatedButton.styleFrom(
                      minimumSize: const Size(0, 44),
                      textStyle: const TextStyle(
                          fontSize: 12, fontWeight: FontWeight.w700),
                    ),
                  ),
                ),
              ],
            ],
          ),
        ],
      ),
    );
  }
}

// ── Paso 2 — Detalles ─────────────────────────────────────────────────────────
class _PasoDetalles extends StatelessWidget {
  final bool activo;
  final TextEditingController descripcionController;
  final TextEditingController referenciaController;
  final TextEditingController evidenciaController;

  const _PasoDetalles({
    required this.activo,
    required this.descripcionController,
    required this.referenciaController,
    required this.evidenciaController,
  });

  @override
  Widget build(BuildContext context) {
    return _PasoCard(
      numero: '03',
      titulo: 'Detalles del problema',
      subtitulo: 'Ayudá al taller a entender mejor la situación',
      activo: activo,
      completado: false,
      child: Column(
        children: [
          EvTextField(
            label: 'DESCRIPCIÓN DEL PROBLEMA',
            hint: 'Ej: El motor hace un ruido extraño y el auto no arranca...',
            controller: descripcionController,
            validator: (v) {
              if (v == null || v.trim().isEmpty) {
                return 'Describí brevemente el problema';
              }
              if (v.trim().length < 10) {
                return 'Mínimo 10 caracteres';
              }
              return null;
            },
          ),

          const SizedBox(height: 16),

          EvTextField(
            label: 'REFERENCIA DE UBICACIÓN (opcional)',
            hint: 'Ej: Frente al mercado, esquina con Av. Montes...',
            controller: referenciaController,
          ),

          const SizedBox(height: 8),

          const Row(
            children: [
              Icon(
                Icons.info_outline_rounded,
                size: 13,
                color: AppTheme.textSecondary,
              ),
              SizedBox(width: 6),
              Expanded(
                child: Text(
                  'La referencia ayuda al mecánico a encontrarte más rápido.',
                  style: TextStyle(
                    fontSize: 11,
                    color: AppTheme.textSecondary,
                    height: 1.4,
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),

          EvTextField(
            label: 'URL DE EVIDENCIA',
            hint: 'Ej: https://midominio.com/evidencia.jpg',
            controller: evidenciaController,
            keyboardType: TextInputType.url,
            validator: (v) {
              if (v == null || v.trim().isEmpty) {
                return 'El backend exige al menos una evidencia';
              }

              final texto = v.trim();

              if (!texto.startsWith('http://') &&
                  !texto.startsWith('https://')) {
                return 'Ingrese una URL válida';
              }

              return null;
            },
          ),

          const SizedBox(height: 8),

          const Row(
            children: [
              Icon(
                Icons.link_rounded,
                size: 13,
                color: AppTheme.textSecondary,
              ),
              SizedBox(width: 6),
              Expanded(
                child: Text(
                  'Por ahora el backend recibe evidencias como URLs. Luego se puede agregar subida de imágenes.',
                  style: TextStyle(
                    fontSize: 11,
                    color: AppTheme.textSecondary,
                    height: 1.4,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

// ── Barra de envío inferior ───────────────────────────────────────────────────
class _BarraEnviar extends StatelessWidget {
  final bool enviando;
  final VoidCallback onEnviar;

  const _BarraEnviar({required this.enviando, required this.onEnviar});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: AppTheme.surface,
      padding: EdgeInsets.only(
        left: 20,
        right: 20,
        top: 12,
        bottom: MediaQuery.of(context).padding.bottom + 12,
      ),
      child: EvPrimaryButton(
        label: 'Enviar Solicitud de Auxilio',
        loading: enviando,
        onPressed: onEnviar,
      ),
    );
  }
}

// ── Card contenedor de paso ───────────────────────────────────────────────────
class _PasoCard extends StatelessWidget {
  final String numero;
  final String titulo;
  final String subtitulo;
  final bool activo;
  final bool completado;
  final Widget child;

  const _PasoCard({
    required this.numero,
    required this.titulo,
    required this.subtitulo,
    required this.activo,
    required this.completado,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    return AnimatedOpacity(
      duration: const Duration(milliseconds: 250),
      opacity: activo || completado ? 1.0 : 0.45,
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppTheme.surface,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: activo ? AppTheme.primary : AppTheme.border,
            width: activo ? 1.5 : 1,
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header del paso
            Row(
              children: [
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
                  decoration: BoxDecoration(
                    color: completado
                        ? AppTheme.success
                        : activo
                            ? AppTheme.primary
                            : AppTheme.border,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: completado
                      ? const Icon(Icons.check_rounded,
                          color: Colors.white, size: 11)
                      : Text(
                          numero,
                          style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.w800,
                            color: activo ? Colors.white : AppTheme.textSecondary,
                            letterSpacing: 0.5,
                          ),
                        ),
                ),
                const SizedBox(width: 10),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      titulo,
                      style: const TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w700,
                        color: AppTheme.textPrimary,
                      ),
                    ),
                    Text(
                      subtitulo,
                      style: const TextStyle(
                        fontSize: 11,
                        color: AppTheme.textSecondary,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            if (activo) ...[
              const SizedBox(height: 16),
              const Divider(height: 1),
              const SizedBox(height: 16),
              child,
            ],
          ],
        ),
      ),
    );
  }
}

// ── Modelo interno ────────────────────────────────────────────────────────────
class _TipoEmergencia {
  final String valor;
  final String label;
  final IconData icon;
  const _TipoEmergencia(
      {required this.valor, required this.label, required this.icon});
}