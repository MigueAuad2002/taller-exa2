import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../environments/environment.development';
import { AuthService } from '../../../services/auth';

// Interfaz para tipar estrictamente nuestros datos
export interface Usuario {
  nro_usuario?: number;
  ci: string;
  nombre_completo: string;
  correo: string;
  telefono: string;
  nombre_rol: string;
  id_empresa: number;
  password?: string; // Solo se usa al crear o editar
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
  private apiUrl = environment.apiUrl;

  // Estados de la tabla
  usuarios: Usuario[] = [];
  cargando: boolean = false;
  mensajeError: string = '';

  // Estados del Modal (Formulario emergente)
  mostrarModal: boolean = false;
  modoEdicion: boolean = false;
  
  // Objeto en blanco para el formulario
  usuarioForm: Usuario = this.inicializarUsuario();

  // Roles disponibles para el selector
  rolesDisponibles = ['ADMINISTRADOR', 'GERENTE TALLER', 'MECANICO', 'CLIENTE'];

  ngOnInit() {
    this.cargarUsuarios();
  }

  inicializarUsuario(): Usuario {
    return {
      ci: '',
      nombre_completo: '',
      correo: '',
      telefono: '',
      nombre_rol: 'MECANICO', // Valor por defecto
      id_empresa: 1 // Por ahora estático, luego lo puedes atar al tenant
    };
  }

  // --- CRUD OPERATIONS ---

  cargarUsuarios() {
    this.cargando = true;
    this.mensajeError = '';
    
    // Necesitamos pasar el token para que FastAPI nos deje ver la lista
    const headers = { Authorization: `Bearer ${this.authService.obtenerToken()}` };

    this.http.get<Usuario[]>(`${this.apiUrl}/usuarios`, { headers }).subscribe({
      next: (data) => {
        this.usuarios = data;
        this.cargando = false;
      },
      error: (err) => {
        this.mensajeError = 'Error al cargar los usuarios. Verifique la conexión.';
        this.cargando = false;
        console.error(err);
      }
    });
  }

  guardarUsuario() {
    if (!this.usuarioForm.ci || !this.usuarioForm.nombre_completo || !this.usuarioForm.correo) {
      alert('Por favor complete los campos obligatorios (CI, Nombre y Correo).');
      return;
    }

    const headers = { Authorization: `Bearer ${this.authService.obtenerToken()}` };
    this.cargando = true;

    if (this.modoEdicion) {
      // ACTUALIZAR (PUT)
      this.http.put(`${this.apiUrl}/usuarios/${this.usuarioForm.nro_usuario}`, this.usuarioForm, { headers }).subscribe({
        next: () => {
          this.cerrarModal();
          this.cargarUsuarios(); // Recargar tabla
        },
        error: (err) => {
          alert('Error al actualizar el usuario.');
          this.cargando = false;
        }
      });
    } else {
      // CREAR (POST)
      if (!this.usuarioForm.password) {
        alert('La contraseña es obligatoria para usuarios nuevos.');
        this.cargando = false;
        return;
      }

      this.http.post(`${this.apiUrl}/usuarios`, this.usuarioForm, { headers }).subscribe({
        next: () => {
          this.cerrarModal();
          this.cargarUsuarios();
        },
        error: (err) => {
          alert('Error al crear el usuario.');
          this.cargando = false;
        }
      });
    }
  }

  eliminarUsuario(id?: number) {
    if (!id) return;
    
    if (confirm('¿Está seguro que desea dar de baja a este usuario? Esta acción es irreversible.')) {
      const headers = { Authorization: `Bearer ${this.authService.obtenerToken()}` };
      
      this.http.delete(`${this.apiUrl}/usuarios/${id}`, { headers }).subscribe({
        next: () => this.cargarUsuarios(),
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
    // Hacemos una copia del usuario para no editar la tabla en tiempo real hasta guardar
    this.usuarioForm = { ...usuario, password: '' }; 
    this.mostrarModal = true;
  }

  cerrarModal() {
    this.mostrarModal = false;
  }
}