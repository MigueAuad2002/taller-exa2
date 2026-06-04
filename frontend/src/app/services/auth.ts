import { Injectable, inject, PLATFORM_ID } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { isPlatformBrowser } from '@angular/common'; 
import { environment } from '../../environments/environment.development';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;
  private platformId = inject(PLATFORM_ID); 

  iniciarSesion(credenciales: any) {
    return this.http.post<any>(`${this.apiUrl}/api/auth/login`, credenciales);
  }

  guardarSesion(token: string, usuario: any) {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.setItem('token', token);
      localStorage.setItem('usuario', JSON.stringify(usuario));
    }
  }

  obtenerToken() {
    if (isPlatformBrowser(this.platformId)) {
      return localStorage.getItem('token');
    }
    return null;
  }

  obtenerUsuario() {

    if (!isPlatformBrowser(this.platformId)) {
      return null;
    }
    

    const usuarioString = localStorage.getItem('usuario');
    return usuarioString ? JSON.parse(usuarioString) : null;
  }

  cerrarSesion() {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.clear();
    }
  }
}