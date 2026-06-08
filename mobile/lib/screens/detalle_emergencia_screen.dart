import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../services/emergencia_service.dart';
import '../theme/app_theme.dart';
import '../widgets/ev_widgets.dart';

class DetalleEmergenciaScreen extends StatefulWidget {
  final Map<String, dynamic> emergencia;

  const DetalleEmergenciaScreen({
    super.key,
    required this.emergencia,
  });

  @override
  State<DetalleEmergenciaScreen> createState() =>
      _DetalleEmergenciaScreenState();
}

class _DetalleEmergenciaScreenState extends State<DetalleEmergenciaScreen> {
  bool _agregando = false;

  int get _nroEmergencia {
    return int.parse(widget.emergencia['nro_emergencia'].toString());
  }

  String _texto(dynamic valor) {
    if (valor == null) return 'No asignado';
    final texto = valor.toString().trim();
    return texto.isEmpty ? 'No asignado' : texto;
  }

  Color _colorEstado(String estado) {
    final e = estado.toUpperCase();

    if (e == 'PENDIENTE') return AppTheme.primary;
    if (e == 'ASIGNADA') return AppTheme.accent;
    if (e == 'EN_PROCESO' || e == 'EN PROCESO') return AppTheme.accentLight;
    if (e == 'FINALIZADA' || e == 'COMPLETADA') return AppTheme.success;
    if (e == 'CANCELADA') return AppTheme.error;

    return AppTheme.textSecondary;
  }

  Future<void> _mostrarDialogoAgregarEvidencia() async {
    final controller = TextEditingController();

    await showDialog(
      context: context,
      builder: (ctx) {
        return AlertDialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
          title: const Text(
            'Agregar evidencia',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w800,
              color: AppTheme.textPrimary,
            ),
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              EvTextField(
                label: 'URL DE EVIDENCIA',
                hint: 'Ej: https://servidor.com/evidencia.jpg',
                controller: controller,
                keyboardType: TextInputType.url,
                validator: (_) => null,
              ),
              const SizedBox(height: 10),
              const Text(
                'Por ahora el backend recibe evidencias como URL. Luego se puede agregar subida de imagen o audio.',
                style: TextStyle(
                  fontSize: 11,
                  color: AppTheme.textSecondary,
                  height: 1.4,
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: _agregando ? null : () => Navigator.pop(ctx),
              child: const Text(
                'Cancelar',
                style: TextStyle(color: AppTheme.textSecondary),
              ),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                minimumSize: Size.zero,
                padding: const EdgeInsets.symmetric(
                  horizontal: 18,
                  vertical: 10,
                ),
              ),
              onPressed: _agregando
                  ? null
                  : () async {
                      final url = controller.text.trim();

                      if (url.isEmpty) {
                        _mostrarError('Ingrese una URL de evidencia.');
                        return;
                      }

                      if (!url.startsWith('http://') &&
                          !url.startsWith('https://')) {
                        _mostrarError('Ingrese una URL válida.');
                        return;
                      }

                      Navigator.pop(ctx);
                      await _agregarEvidencia(url);
                    },
              child: const Text(
                'AGREGAR',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
          ],
        );
      },
    );

    controller.dispose();
  }

  Future<void> _agregarEvidencia(String url) async {
    setState(() => _agregando = true);

    try {
      await EmergenciaService().agregarEvidencia(
        nroEmergencia: _nroEmergencia,
        urlEvidencia: url,
      );

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Evidencia agregada correctamente.'),
          backgroundColor: AppTheme.success,
        ),
      );
    } catch (e) {
      if (!mounted) return;
      _mostrarError(e.toString().replaceAll('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _agregando = false);
    }
  }

  void _mostrarError(String mensaje) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(mensaje),
        backgroundColor: AppTheme.error,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final emergencia = widget.emergencia;

    final estado = _texto(emergencia['estado']);
    final latitud = emergencia['latitud'];
    final longitud = emergencia['longitud'];

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('DETALLE EMERGENCIA'),
        backgroundColor: AppTheme.primary,
        foregroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 18),
          onPressed: () => Navigator.pop(context, true),
        ),
      ),
      bottomNavigationBar: Container(
        color: AppTheme.surface,
        padding: EdgeInsets.only(
          left: 20,
          right: 20,
          top: 12,
          bottom: MediaQuery.of(context).padding.bottom + 12,
        ),
        child: EvPrimaryButton(
          label: 'Agregar Evidencia',
          loading: _agregando,
          onPressed: _mostrarDialogoAgregarEvidencia,
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            _HeaderDetalle(
              nroEmergencia: _texto(emergencia['nro_emergencia']),
              tipoEmergencia: _texto(emergencia['tipo_emergencia']),
              estado: estado,
              colorEstado: _colorEstado(estado),
            ),
            const SizedBox(height: 14),
            _DetalleCard(
              title: 'Información general',
              children: [
                _InfoRow(
                  icon: Icons.priority_high_rounded,
                  label: 'Prioridad',
                  value: _texto(emergencia['prioridad']).toUpperCase(),
                ),
                const SizedBox(height: 10),
                _InfoRow(
                  icon: Icons.calendar_today_outlined,
                  label: 'Fecha inicio',
                  value: _texto(emergencia['fecha_inicio']),
                ),
                const SizedBox(height: 10),
                _InfoRow(
                  icon: Icons.check_circle_outline_rounded,
                  label: 'Fecha fin',
                  value: _texto(emergencia['fecha_fin']),
                ),
                const SizedBox(height: 10),
                _InfoRow(
                  icon: Icons.build_outlined,
                  label: 'Taller',
                  value: emergencia['nro_taller'] == null
                      ? 'Pendiente de asignación'
                      : 'Taller N° ${emergencia['nro_taller']}',
                ),
              ],
            ),
            const SizedBox(height: 14),
            _DetalleCard(
              title: 'Ubicación',
              children: [
                _InfoRow(
                  icon: Icons.location_on_outlined,
                  label: 'Coordenadas',
                  value: latitud == null || longitud == null
                      ? 'Ubicación no disponible'
                      : 'Lat: $latitud\nLng: $longitud',
                ),
                if (latitud != null && longitud != null) ...[
                  const SizedBox(height: 14),
                  _MapaDetalle(
                    latitud: double.parse(latitud.toString()),
                    longitud: double.parse(longitud.toString()),
                  ),
                ],
              ],
            ),
            const SizedBox(height: 14),
            _DetalleCard(
              title: 'Evidencias',
              children: const [
                Row(
                  children: [
                    Icon(
                      Icons.info_outline_rounded,
                      size: 16,
                      color: AppTheme.textSecondary,
                    ),
                    SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Puedes agregar evidencias a esta emergencia. El backend actual no devuelve la lista de evidencias en este endpoint.',
                        style: TextStyle(
                          fontSize: 12,
                          color: AppTheme.textSecondary,
                          height: 1.4,
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _HeaderDetalle extends StatelessWidget {
  final String nroEmergencia;
  final String tipoEmergencia;
  final String estado;
  final Color colorEstado;

  const _HeaderDetalle({
    required this.nroEmergencia,
    required this.tipoEmergencia,
    required this.estado,
    required this.colorEstado,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: AppTheme.primary,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.15),
              borderRadius: BorderRadius.circular(6),
            ),
            child: const Icon(
              Icons.car_crash_outlined,
              color: Colors.white,
              size: 26,
            ),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'EMERGENCIA N° $nroEmergencia',
                  style: const TextStyle(
                    color: Color(0xFFBFCFFF),
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 1,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  tipoEmergencia.toUpperCase(),
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.w900,
                  ),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(
              horizontal: 8,
              vertical: 4,
            ),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.12),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(
                color: Colors.white.withOpacity(0.2),
              ),
            ),
            child: Text(
              estado.toUpperCase(),
              style: const TextStyle(
                color: Colors.white,
                fontSize: 9,
                fontWeight: FontWeight.w800,
                letterSpacing: 0.6,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _DetalleCard extends StatelessWidget {
  final String title;
  final List<Widget> children;

  const _DetalleCard({
    required this.title,
    required this.children,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppTheme.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title.toUpperCase(),
            style: const TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w800,
              color: AppTheme.textSecondary,
              letterSpacing: 1.1,
            ),
          ),
          const SizedBox(height: 14),
          ...children,
        ],
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _InfoRow({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(
          icon,
          size: 16,
          color: AppTheme.textSecondary,
        ),
        const SizedBox(width: 8),
        SizedBox(
          width: 92,
          child: Text(
            label,
            style: const TextStyle(
              fontSize: 11,
              color: AppTheme.textSecondary,
            ),
          ),
        ),
        Expanded(
          child: Text(
            value,
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: AppTheme.textPrimary,
              height: 1.35,
            ),
          ),
        ),
      ],
    );
  }
}

class _MapaDetalle extends StatelessWidget {
  final double latitud;
  final double longitud;

  const _MapaDetalle({
    required this.latitud,
    required this.longitud,
  });

  @override
  Widget build(BuildContext context) {
    final punto = LatLng(latitud, longitud);

    return Container(
      width: double.infinity,
      height: 190,
      decoration: BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppTheme.border),
      ),
      clipBehavior: Clip.antiAlias,
      child: FlutterMap(
        options: MapOptions(
          initialCenter: punto,
          initialZoom: 16,
        ),
        children: [
          TileLayer(
            urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
            userAgentPackageName: 'com.example.emergencias_vehiculares',
          ),
          MarkerLayer(
            markers: [
              Marker(
                point: punto,
                width: 44,
                height: 44,
                child: const Icon(
                  Icons.location_on_rounded,
                  color: AppTheme.error,
                  size: 36,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}