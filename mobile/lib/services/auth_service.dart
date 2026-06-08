import 'package:dio/dio.dart';
import '../config/app_config.dart';
import 'token_storage.dart';

class AuthService {
  final Dio _dio = Dio(
    BaseOptions(
      baseUrl: AppConfig.apiBaseUrl,
      connectTimeout: const Duration(seconds: 20),
      receiveTimeout: const Duration(seconds: 20),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ),
  );

  // ── LOGIN ──────────────────────────────────────────────────────────────
  // POST /api/auth/login
  // Body: { "ci": "...", "password": "..." }
  // Response: { "success": true, "token": "...", "usuario": { ... } }
  Future<Map<String, dynamic>> login({
    required String ci,
    required String password,
  }) async {
    try {
      final response = await _dio.post(
        '/api/auth/login',
        data: {'ci': ci, 'password': password},
      );

      final data = response.data;

      if (data == null || data['success'] != true) {
        throw Exception(data?['message'] ?? 'Error al iniciar sesión.');
      }

      final token = data['token'] as String;
      final usuario = data['usuario'] as Map<String, dynamic>;

      // Guardamos token y todos los datos del usuario en secure storage
      await TokenStorage.saveToken(token);
      await TokenStorage.saveUserData(
        nroUsuario: usuario['nro_usuario'].toString(),
        ci: usuario['ci'].toString(),
        nombreCompleto: usuario['nombre_completo'].toString(),
        correo: usuario['correo'].toString(),
        nombreRol: usuario['nombre_rol'].toString(),
        telefono: usuario['telefono'].toString(),
        idEmpresa: usuario['id_empresa']?.toString() ?? '',
      );

      return usuario;
    } on DioException catch (e) {
      throw Exception(_parsearErrorDio(e));
    }
  }

  // ── REGISTER ───────────────────────────────────────────────────────────
  // POST /api/auth/register
  // Body: {
  //   "ci": "...",
  //   "nombre_completo": "...",
  //   "nombre_usuario": "...",
  //   "password": "...",
  //   "nro_rol": 3,           ← 3 = Cliente (ajustá según tu BD)
  //   "telefono": "...",
  //   "correo": "...",
  //   "direccion": "",        ← opcional
  //   "id_empresa": null      ← null para clientes sin empresa
  // }
  // Response: { "success": true, "message": "...", "data": { ... } }
  Future<Map<String, dynamic>> register({
    required String ci,
    required String nombreCompleto,
    required String nombreUsuario,
    required String password,
    required String telefono,
    required String correo,
    required int nroRol,
    String direccion = '',
    int? idEmpresa,
  }) async {
    try {
      final response = await _dio.post(
        '/api/auth/register',
        data: {
          'ci': ci,
          'nombre_completo': nombreCompleto,
          'nombre_usuario': nombreUsuario,
          'password': password,
          'nro_rol': nroRol,
          'telefono': telefono,
          'correo': correo,
          'direccion': direccion,
          'id_empresa': idEmpresa,
        },
      );

      final data = response.data;

      if (data == null || data['success'] != true) {
        throw Exception(data?['message'] ?? 'Error al registrar usuario.');
      }

      return data;
    } on DioException catch (e) {
      throw Exception(_parsearErrorDio(e));
    }
  }

  // ── Parser de errores Dio ──────────────────────────────────────────────
  // FastAPI devuelve los errores en response.data['detail']
  String _parsearErrorDio(DioException e) {
    if (e.response != null) {
      final detail = e.response?.data?['detail'];
      if (detail != null) return detail.toString();

      switch (e.response?.statusCode) {
        case 400:
          return 'Petición inválida. Revisá los datos ingresados.';
        case 401:
          return e.response?.data?['detail'] ?? 'Credenciales incorrectas.';
        case 500:
          return 'Error interno del servidor. Intentá más tarde.';
        default:
          return 'Error ${e.response?.statusCode}: ${e.response?.statusMessage}';
      }
    }
    if (e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.receiveTimeout) {
      return 'Tiempo de espera agotado. Verificá tu conexión.';
    }
    if (e.type == DioExceptionType.connectionError) {
      return 'No se pudo conectar al servidor. Verificá que el backend esté corriendo.';
    }
    return 'Error de red: ${e.message}';
  }
}