import { Injectable, inject, PLATFORM_ID, NgZone } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { BehaviorSubject, Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { AuthService } from './auth';

export interface Notificacion {
  tipo_alerta: string;
  titulo: string;
  cuerpo: string;
  data: any;
  leida: boolean;
  fecha: Date;
}

@Injectable({
  providedIn: 'root'
})
export class NotificacionesService {
  
  private authService = inject(AuthService);
  private platformId = inject(PLATFORM_ID);
  private ngZone = inject(NgZone);
  
  private socket: WebSocket | null = null;
  
  // Estado reactivo
  private notificacionesSource = new BehaviorSubject<Notificacion[]>([]);
  notificaciones$: Observable<Notificacion[]> = this.notificacionesSource.asObservable();

  conectar() {
    // 1. Evitar ejecución si no estamos en el navegador
    if (!isPlatformBrowser(this.platformId)) return;
    if (this.socket) return; // Ya existe conexión

    const token = this.authService.obtenerToken();
    if (!token) return;

    // 2. Transformar la URL de la API de http:// a ws:// dinámicamente
    const wsBaseUrl = environment.apiUrl.replace(/^http/, 'ws');
    const wsUrl = `${wsBaseUrl}/api/ws/notificaciones?token=${token}`;

    // 3. Conectar fuera de Angular para mejorar el rendimiento
    this.ngZone.runOutsideAngular(() => {
      this.socket = new WebSocket(wsUrl);

      this.socket.onopen = () => console.log('WebSocket Notificaciones Conectado 🟢');

      this.socket.onmessage = (event) => {
        // 4. Volver a la zona de Angular para actualizar los datos
        this.ngZone.run(() => {
          const dataBackend = JSON.parse(event.data);
          
          const nuevaNotificacion: Notificacion = {
            tipo_alerta: dataBackend.tipo_alerta,
            titulo: dataBackend.titulo,
            cuerpo: dataBackend.cuerpo,
            data: dataBackend.data,
            leida: false,
            fecha: new Date()
          };

          const listaActual = this.notificacionesSource.getValue();
          this.notificacionesSource.next([nuevaNotificacion, ...listaActual]);
        });
      };

      this.socket.onclose = () => {
        console.log('WebSocket Desconectado 🔴. Reconectando...');
        this.socket = null;
        setTimeout(() => this.conectar(), 5000);
      };
    });
  }

  marcarComoLeidas() {
    const listaActual = this.notificacionesSource.getValue();
    const listaActualizada = listaActual.map(n => ({ ...n, leida: true }));
    this.notificacionesSource.next(listaActualizada);
  }

  desconectar() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}