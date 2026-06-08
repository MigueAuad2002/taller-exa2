//home_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../theme/app_theme.dart';
import '../services/auth_provider.dart';
import '../services/token_storage.dart';
import 'solicitar_emergencia_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  String _nombreUsuario = '';
  String _rolUsuario = '';

  @override
  void initState() {
    super.initState();
    _cargarDatosUsuario();
  }

  Future<void> _cargarDatosUsuario() async {
    final nombre = await TokenStorage.getValue('nombre_completo') ?? '';
    final rol = await TokenStorage.getValue('nombre_rol') ?? '';
    if (mounted) {
      setState(() {
        _nombreUsuario = nombre;
        _rolUsuario = rol;
      });
    }
  }

  String get _primerNombre {
    if (_nombreUsuario.isEmpty) return '';
    return _nombreUsuario.split(' ').first;
  }

  String get _iniciales {
    if (_nombreUsuario.isEmpty) return '?';
    final partes = _nombreUsuario.trim().split(' ');
    if (partes.length >= 2) {
      return '${partes[0][0]}${partes[1][0]}'.toUpperCase();
    }
    return _nombreUsuario[0].toUpperCase();
  }

  void _confirmarLogout(BuildContext context) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
        title: const Text(
          'Cerrar sesión',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w700,
            color: AppTheme.textPrimary,
          ),
        ),
        content: const Text(
          '¿Estás seguro que deseas salir de tu cuenta?',
          style: TextStyle(fontSize: 14, color: AppTheme.textSecondary),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancelar',
                style: TextStyle(color: AppTheme.textSecondary)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.primary,
              minimumSize: Size.zero,
              padding:
                  const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
            ),
            onPressed: () {
              Navigator.pop(ctx);
              Provider.of<AuthProvider>(context, listen: false).logout();
            },
            child: const Text('Salir',
                style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      body: Column(
        children: [
          // ── Navbar superior (replica web) ─────────────────────────────
          _NavBar(
            iniciales: _iniciales,
            nombreUsuario: _nombreUsuario,
            rolUsuario: _rolUsuario,
            onLogout: () => _confirmarLogout(context),
          ),

          // ── Contenido scrollable ──────────────────────────────────────
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Saludo
                  Text(
                    'Bienvenido${_primerNombre.isNotEmpty ? ', $_primerNombre' : ''}.',
                    style: const TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.w800,
                      color: AppTheme.textPrimary,
                      letterSpacing: -0.3,
                    ),
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    'Seleccione una opción para continuar.',
                    style: TextStyle(
                      fontSize: 13,
                      color: AppTheme.textSecondary,
                    ),
                  ),
                  const SizedBox(height: 24),

                  // ── Botón SOS destacado ─────────────────────────────
                  _SosButton(
                    onTap: () => Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => const SolicitarEmergenciaScreen(),
                      ),
                    ),
                  ),
                  const SizedBox(height: 20),

                  // ── Grid de módulos ─────────────────────────────────
                  const _SectionLabel(text: 'MIS SERVICIOS'),
                  const SizedBox(height: 12),
                  GridView.count(
                    crossAxisCount: 2,
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    crossAxisSpacing: 12,
                    mainAxisSpacing: 12,
                    childAspectRatio: 1.1,
                    children: [
                      _ModuleCard(
                        icon: Icons.history_rounded,
                        title: 'Mis Emergencias',
                        subtitle: 'Historial de solicitudes',
                        onTap: () {
                          // TODO: navegar a historial
                        },
                      ),
                      _ModuleCard(
                        icon: Icons.request_quote_outlined,
                        title: 'Cotizaciones',
                        subtitle: 'Ver y aceptar propuestas',
                        onTap: () {
                          // TODO: navegar a cotizaciones
                        },
                      ),
                      _ModuleCard(
                        icon: Icons.chat_bubble_outline_rounded,
                        title: 'Chat',
                        subtitle: 'Mensajes con el taller',
                        onTap: () {
                          // TODO: navegar a chat
                        },
                      ),
                      _ModuleCard(
                        icon: Icons.person_outline_rounded,
                        title: 'Mi Perfil',
                        subtitle: 'Datos de tu cuenta',
                        onTap: () {
                          // TODO: navegar a perfil
                        },
                      ),
                    ],
                  ),
                  const SizedBox(height: 20),

                  // ── Emergencia activa (si existe) ───────────────────
                  // TODO: mostrar condicionalmente si hay una emergencia en curso
                  // _EmergenciaActivaCard(...),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ── NavBar ────────────────────────────────────────────────────────────────────
class _NavBar extends StatelessWidget {
  final String iniciales;
  final String nombreUsuario;
  final String rolUsuario;
  final VoidCallback onLogout;

  const _NavBar({
    required this.iniciales,
    required this.nombreUsuario,
    required this.rolUsuario,
    required this.onLogout,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      color: AppTheme.primary,
      padding: EdgeInsets.only(
        top: MediaQuery.of(context).padding.top + 10,
        bottom: 12,
        left: 16,
        right: 16,
      ),
      child: Row(
        children: [
          // Logo — solo ícono + "EV" para no desbordar en móvil
          Container(
            width: 28,
            height: 28,
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.15),
              borderRadius: BorderRadius.circular(6),
            ),
            child: const Icon(Icons.flash_on_rounded, color: Colors.white, size: 16),
          ),
          const SizedBox(width: 8),
          const Text(
            'EMERGENCIAS',
            style: TextStyle(
              color: Colors.white,
              fontSize: 12,
              fontWeight: FontWeight.w900,
              letterSpacing: 0.2,
            ),
          ),

          const Spacer(),

          // Info usuario — Flexible para truncar si el nombre es largo
          Flexible(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  nombreUsuario.isNotEmpty ? nombreUsuario.toUpperCase() : '...',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 10,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 0.4,
                  ),
                  overflow: TextOverflow.ellipsis,
                  maxLines: 1,
                ),
                Text(
                  rolUsuario.toUpperCase(),
                  style: const TextStyle(
                    color: Color(0xFF8FA8E8),
                    fontSize: 9,
                    letterSpacing: 0.4,
                  ),
                  overflow: TextOverflow.ellipsis,
                  maxLines: 1,
                ),
              ],
            ),
          ),
          const SizedBox(width: 10),

          // Avatar + logout
          PopupMenuButton<String>(
            offset: const Offset(0, 40),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(6),
              side: const BorderSide(color: AppTheme.border),
            ),
            onSelected: (val) {
              if (val == 'logout') onLogout();
            },
            itemBuilder: (_) => [
              PopupMenuItem(
                value: 'profile',
                child: Row(
                  children: const [
                    Icon(Icons.person_outline, size: 16, color: AppTheme.textSecondary),
                    SizedBox(width: 8),
                    Text('Mi Perfil', style: TextStyle(fontSize: 13)),
                  ],
                ),
              ),
              const PopupMenuDivider(),
              PopupMenuItem(
                value: 'logout',
                child: Row(
                  children: const [
                    Icon(Icons.logout, size: 16, color: AppTheme.error),
                    SizedBox(width: 8),
                    Text('Cerrar Sesión',
                        style: TextStyle(fontSize: 13, color: AppTheme.error)),
                  ],
                ),
              ),
            ],
            child: CircleAvatar(
              radius: 16,
              backgroundColor: const Color(0xFF2D3A8C),
              child: Text(
                iniciales,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ── Botón SOS destacado ───────────────────────────────────────────────────────
class _SosButton extends StatelessWidget {
  final VoidCallback onTap;
  const _SosButton({required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(8),
        child: Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(vertical: 22, horizontal: 20),
          decoration: BoxDecoration(
            color: AppTheme.primary,
            borderRadius: BorderRadius.circular(8),
            boxShadow: [
              BoxShadow(
                color: AppTheme.primary.withOpacity(0.3),
                blurRadius: 12,
                offset: const Offset(0, 4),
              ),
            ],
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
                child: const Icon(Icons.directions_car_rounded,
                    color: Colors.white, size: 26),
              ),
              const SizedBox(width: 16),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'SOLICITAR AUXILIO',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 15,
                        fontWeight: FontWeight.w900,
                        letterSpacing: 0.8,
                      ),
                    ),
                    SizedBox(height: 3),
                    Text(
                      'Envía tu ubicación y describe el problema',
                      style: TextStyle(
                        color: Color(0xFFBFCFFF),
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
              const Icon(Icons.arrow_forward_ios_rounded,
                  color: Colors.white54, size: 16),
            ],
          ),
        ),
      ),
    );
  }
}

// ── Tarjeta de módulo ─────────────────────────────────────────────────────────
class _ModuleCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final String? badge;
  final VoidCallback onTap;

  const _ModuleCard({
    required this.icon,
    required this.title,
    required this.subtitle,
    this.badge,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(8),
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppTheme.surface,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: AppTheme.border),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    width: 36,
                    height: 36,
                    decoration: BoxDecoration(
                      color: AppTheme.primary.withOpacity(0.08),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Icon(icon, color: AppTheme.primary, size: 18),
                  ),
                  if (badge != null) ...[
                    const Spacer(),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 7, vertical: 2),
                      decoration: BoxDecoration(
                        color: AppTheme.primary,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Text(
                        badge!,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 10,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                  ],
                ],
              ),
              const Spacer(),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                  color: AppTheme.textPrimary,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                subtitle,
                style: const TextStyle(
                  fontSize: 11,
                  color: AppTheme.textSecondary,
                ),
              ),
              const SizedBox(height: 8),
              const Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  Icon(Icons.arrow_forward,
                      size: 14, color: AppTheme.textSecondary),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ── Label de sección ──────────────────────────────────────────────────────────
class _SectionLabel extends StatelessWidget {
  final String text;
  const _SectionLabel({required this.text});

  @override
  Widget build(BuildContext context) {
    return Text(
      text,
      style: const TextStyle(
        fontSize: 11,
        fontWeight: FontWeight.w700,
        color: AppTheme.textSecondary,
        letterSpacing: 1.2,
      ),
    );
  }
}