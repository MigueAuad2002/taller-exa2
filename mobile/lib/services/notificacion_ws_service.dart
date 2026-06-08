import 'dart:async';
import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

import '../config/app_config.dart';
import 'token_storage.dart';

class NotificacionWsService {
  WebSocketChannel? _channel;
  StreamSubscription? _subscription;
  bool _activo = false;

  bool get activo => _activo;

  Future<void> conectar({
    required void Function(bool activo) onEstado,
    required void Function(Map<String, dynamic> mensaje) onMensaje,
    required void Function(String error) onError,
  }) async {
    if (_activo) return;

    final token = await TokenStorage.getToken();

    if (token == null || token.trim().isEmpty) {
      onError('No hay token para conectar WebSocket.');
      return;
    }

    try {
      final apiUri = Uri.parse(AppConfig.apiBaseUrl);

      final wsUri = apiUri.replace(
        scheme: apiUri.scheme == 'https' ? 'wss' : 'ws',
        path: '/api/ws/notificaciones',
        queryParameters: {
          'token': token,
        },
      );

      _channel = WebSocketChannel.connect(wsUri);

      _activo = true;
      onEstado(true);

      _subscription = _channel!.stream.listen(
        (event) {
          try {
            final decoded = jsonDecode(event.toString());

            if (decoded is Map) {
              onMensaje(Map<String, dynamic>.from(decoded));
            }
          } catch (_) {
            onMensaje({
              'tipo_alerta': 'MENSAJE_WS',
              'titulo': 'Mensaje recibido',
              'cuerpo': event.toString(),
              'data': {},
            });
          }
        },
        onError: (error) {
          _activo = false;
          onEstado(false);
          onError(error.toString());
        },
        onDone: () {
          _activo = false;
          onEstado(false);
        },
        cancelOnError: true,
      );
    } catch (e) {
      _activo = false;
      onEstado(false);
      onError(e.toString());
    }
  }

  void enviarPing() {
    if (!_activo || _channel == null) return;
    _channel!.sink.add('ping');
  }

  Future<void> desconectar() async {
    _activo = false;

    await _subscription?.cancel();
    _subscription = null;

    await _channel?.sink.close();
    _channel = null;
  }
}