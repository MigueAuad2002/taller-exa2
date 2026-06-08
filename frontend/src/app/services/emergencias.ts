import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { AuthService } from './auth';

export interface Emergencia {
  nro_emergencia: number;
  tipo_emergencia: string;
  latitud: number;
  longitud: number;
  fecha_inicio: string;
  fecha_fin?: string;
  estado: string;
  prioridad: string;
  nro_usuario: number;
  nro_taller?: number;
  id_empresa?: number;
  nombre_taller?: string;
  nombre_usuario?:string;
  telefono_cliente?:string;
}

export interface RespuestaApiEmergencias {
  success: boolean;
  message: string;
  data: Emergencia[];
}

@Injectable({
  providedIn: 'root'
})
export class EmergenciasService {
  private http = inject(HttpClient);
  private authService = inject(AuthService);
  private apiUrl = environment.apiUrl;

  private getHeaders(): HttpHeaders {
    const token = this.authService.obtenerToken();
    return token ? new HttpHeaders({ 'Authorization': `Bearer ${token}` }) : new HttpHeaders();
  }

  // Para Administradores
  obtenerTodasLasEmergencias(): Observable<RespuestaApiEmergencias> {
    return this.http.get<RespuestaApiEmergencias>(`${this.apiUrl}/api/emergencias/`, { headers: this.getHeaders() });
  }

  // Para Clientes
  obtenerMisEmergencias(): Observable<RespuestaApiEmergencias> {
    return this.http.get<RespuestaApiEmergencias>(`${this.apiUrl}/api/emergencias/mis-emergencias`, { headers: this.getHeaders() });
  }

  // Para Mecánicos / Gerentes
  obtenerEmergenciasMiTaller(): Observable<RespuestaApiEmergencias> {
    return this.http.get<RespuestaApiEmergencias>(`${this.apiUrl}/api/emergencias/mi-taller`, { headers: this.getHeaders() });
  }

  crearEmergencia(datos: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/api/emergencias/`, datos, { headers: this.getHeaders() });
  }

  actualizarEmergencia(id: number, datos: any): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/api/emergencias/${id}`, datos, { headers: this.getHeaders() });
  }

  eliminarEmergencia(id: number): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/api/emergencias/${id}`, { headers: this.getHeaders() });
  }
}