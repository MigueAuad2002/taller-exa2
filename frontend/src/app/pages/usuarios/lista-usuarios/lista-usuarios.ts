import { Component, OnInit, inject, ChangeDetectorRef, NgZone } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../environments/environment.development';
import { AuthService } from '../../../services/auth';

export interface Usuario {
  nro_usuario?: number;
  ci: string;
  nombre_usuario: string;
  estado: string;
  id_empresa?: number | null;
  nombre_completo: string;
  correo: string;
  telefono: string;
  direccion: string;
  nombre_rol?: string; 
  nro_rol: number;     
  password?: string;
}

export interface RespuestaApi {
  success: boolean;
  message: string;
  data: Usuario[];
}

@Component({
  selector: 'app-lista-usuarios',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './lista-usuarios.html'
})
export class ListaUsuariosComponent implements OnInit {
  
  private http = inject(HttpClient);
  private authService = inject(AuthService);
  private cdr = inject(ChangeDetectorRef);
  private ngZone = inject(NgZone); // <--- INYECTAMOS NGZONE
  private apiUrl = environment.apiUrl;

  usuarios: Usuario[] = [];
  cargando: boolean = false;
  mensajeError: string = '';

  mostrarModal: boolean = false;
  modoEdicion: boolean = false;
  
  usuarioForm: Usuario = this.inicializarUsuario();

  totalUsuarios: number = 0;
  usuariosActivos: number = 0;
  usuariosInactivos: number = 0;

  rolesDisponibles = [
    { id: 1, nombre: 'ADMINISTRADOR' },
    { id: 2, nombre: 'GERENTE TALLER' },
    { id: 3, nombre: 'MECANICO' },
    { id: 4, nombre: 'CLIENTE' }
  ];

  ngOnInit() {
    this.cargarUsuarios();
  }

  actualizarMetricas() {
    this.totalUsuarios = this.usuarios.length;
    this.usuariosActivos = this.usuarios.filter(u => u.estado === 'ACTIVO').length;
    this.usuariosInactivos = this.usuarios.filter(u => u.estado === 'INACTIVO').length;
  }

  obtenerIniciales(nombre: string): string {
    if (!nombre) return 'XX';
    const partes = nombre.trim().split(' ');
    if (partes.length >= 2) {
      return (partes[0][0] + partes[1][0]).toUpperCase();
    }
    return nombre.substring(0, 2).toUpperCase();
  }

  inicializarUsuario(): Usuario {
    return {
      ci: '', nombre_usuario: '', nombre_completo: '', correo: '',
      telefono: '', direccion: '', estado: 'ACTIVO', nro_rol: 3, id_empresa: 1
    };
  }

  // --- CRUD OPERATIONS ---

  cargarUsuarios() {
    this.cargando = true;
    this.mensajeError = '';
    
    const headers = { Authorization: `Bearer ${this.authService.obtenerToken()}` };

    this.http.get<RespuestaApi>(`${this.apiUrl}/api/usuarios/`, { headers }).subscribe({
      next: (res) => {
        // ENVOLVEMOS LA RESPUESTA EN NGZONE PARA FORZAR EL RENDERIZADO
        this.ngZone.run(() => {
          if (res.success) {
            // USAMOS [...] PARA CREAR UNA NUEVA REFERENCIA EN MEMORIA
            this.usuarios = [...res.data]; 
            this.actualizarMetricas();
          } else {
            this.mensajeError = res.message || 'Error al obtener datos.';
          }
          this.cargando = false;
          this.cdr.detectChanges(); 
        });
      },
      error: (err) => {
        this.ngZone.run(() => {
          this.mensajeError = 'Error de conexión al cargar los usuarios.';
          this.cargando = false;
          this.cdr.detectChanges();
          console.error(err);
        });
      }
    });
  }

  guardarUsuario() {
    if (!this.usuarioForm.ci || !this.usuarioForm.nombre_completo || !this.usuarioForm.nombre_usuario) {
      alert('Por favor complete los campos obligatorios.');
      return;
    }

    const headers = { Authorization: `Bearer ${this.authService.obtenerToken()}` };
    this.cargando = true;

    if (this.modoEdicion) {
      this.http.put(`${this.apiUrl}/api/usuarios/${this.usuarioForm.nro_usuario}`, this.usuarioForm, { headers }).subscribe({
        next: () => {
          this.ngZone.run(() => {
            this.cerrarModal();
            this.cargarUsuarios();
          });
        },
        error: () => {
          this.ngZone.run(() => {
            alert('Error al actualizar el usuario en el servidor.');
            this.cargando = false;
            this.cdr.detectChanges();
          });
        }
      });
    } else {
      if (!this.usuarioForm.password) {
        alert('La contraseña es obligatoria para usuarios nuevos.');
        this.cargando = false;
        return;
      }

      this.http.post(`${this.apiUrl}/api/usuarios/`, this.usuarioForm, { headers }).subscribe({
        next: () => {
          this.ngZone.run(() => {
            this.cerrarModal();
            this.cargarUsuarios();
          });
        },
        error: () => {
          this.ngZone.run(() => {
            alert('Error al crear el usuario. Verifique los datos.');
            this.cargando = false;
            this.cdr.detectChanges();
          });
        }
      });
    }
  }

  eliminarUsuario(id?: number) {
    if (!id) return;
    
    if (confirm('¿Está seguro que desea eliminar a este usuario?')) {
      const headers = { Authorization: `Bearer ${this.authService.obtenerToken()}` };
      
      this.http.delete(`${this.apiUrl}/api/usuarios/${id}`, { headers }).subscribe({
        next: () => {
          this.ngZone.run(() => {
            this.cargarUsuarios();
          });
        },
        error: () => alert('Error al eliminar el usuario.')
      });
    }
  }

  // --- CONTROL DEL MODAL ---

  abrirModalNuevo() {
    this.modoEdicion = false;
    this.usuarioForm = this.inicializarUsuario();
    this.mostrarModal = true;
  }

  abrirModalEditar(usuario: Usuario) {
    this.modoEdicion = true;
    this.usuarioForm = { ...usuario, password: '' }; 
    this.mostrarModal = true;
  }

  cerrarModal() {
    this.mostrarModal = false;
  }
}