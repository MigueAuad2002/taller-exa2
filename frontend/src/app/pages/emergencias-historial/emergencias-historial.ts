import { Component, OnInit, inject, ChangeDetectorRef, NgZone, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { EmergenciasService, Emergencia } from '../../services/emergencias';
import { AuthService } from '../../services/auth';

@Component({
  selector: 'app-emergencias-historial',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './emergencias-historial.html'
})
export class EmergenciasHistorialComponent implements OnInit {
  private emergenciasService = inject(EmergenciasService);
  private authService = inject(AuthService);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);
  private ngZone = inject(NgZone);
  private platformId = inject(PLATFORM_ID);

  usuarioActual: any = null;
  emergencias: Emergencia[] = [];
  emergenciasFiltradas: Emergencia[] = [];
  
  cargando: boolean = false;
  mensajeError: string = '';
  textoBusqueda: string = '';
  filtroEstado: string = ''; 

  // Control de Modales
  mostrarModalCotizacion: boolean = false;
  procesandoAccion: boolean = false;
  emergenciaSeleccionada: Emergencia | null = null;
  
  cotizacionForm = {
    precio_estimado: null,
    tiempo_estimado_minutos: null
  };

  ngOnInit() {
    if (isPlatformBrowser(this.platformId)) {
      this.usuarioActual = this.authService.obtenerUsuario() || this.authService.obtenerUsuario();
      if (this.usuarioActual) {
        this.cargarEmergencias();
      }
    }
  }

  cargarEmergencias() {
    this.cargando = true;
    const rol = this.usuarioActual.nombre_rol.toUpperCase();

    let peticion$;
    if (rol === 'ADMINISTRADOR' || rol == 'GERENTE TALLER') {
      peticion$ = this.emergenciasService.obtenerTodasLasEmergencias();
    } else if (rol === 'CLIENTE') {
      peticion$ = this.emergenciasService.obtenerMisEmergencias();
    } else {
      peticion$ = this.emergenciasService.obtenerEmergenciasMiTaller();
    }

    peticion$.subscribe({
      next: (res) => {
        this.ngZone.run(() => {
          if (res.success) {
            this.emergencias = res.data;
            this.aplicarFiltros();
          }
          this.cargando = false;
          this.cdr.detectChanges();
        });
      },
      error: () => {
        this.ngZone.run(() => {
          this.mensajeError = 'Error al conectar con el centro de control.';
          this.cargando = false;
          this.cdr.detectChanges();
        });
      }
    });
  }

  aplicarFiltros() {
    let filtradas = [...this.emergencias];

    if (this.filtroEstado) {
      filtradas = filtradas.filter(e => e.estado.toUpperCase() === this.filtroEstado.toUpperCase());
    }

    if (this.textoBusqueda) {
      const busqueda = this.textoBusqueda.toLowerCase();
      filtradas = filtradas.filter(e => 
        e.tipo_emergencia.toLowerCase().includes(busqueda) || 
        (e.nombre_usuario && e.nombre_usuario.toLowerCase().includes(busqueda))
      );
    }

    this.emergenciasFiltradas = filtradas;
  }

  setFiltroEstado(estado: string) {
    this.filtroEstado = estado;
    this.aplicarFiltros();
  }

  esTallerOMecanico(): boolean {
    if (!this.usuarioActual) return false;
    const rol = this.usuarioActual.nombre_rol.toUpperCase();
    return ['ADMINISTRADOR','GERENTE TALLER', 'MECANICO', 'MECÁNICO'].includes(rol);
  }

  // --- ACCIÓN 1: ABRIR SUBAS DE COTIZACIÓN (ESTADO PENDIENTE) ---
  abrirModalCotizacion(emergencia: Emergencia) {
    this.emergenciaSeleccionada = emergencia;
    this.cotizacionForm = { precio_estimado: null, tiempo_estimado_minutos: null };
    this.mostrarModalCotizacion = true;
  }

  cerrarModalCotizacion() {
    this.mostrarModalCotizacion = false;
    this.emergenciaSeleccionada = null;
    this.procesandoAccion = false;
  }

  enviarCotizacion() {
    if (!this.cotizacionForm.precio_estimado || !this.cotizacionForm.tiempo_estimado_minutos) {
      alert('Ingrese todos los datos de la oferta comercial.');
      return;
    }
    this.procesandoAccion = true;
    
    // Simulación fluida en UI, lista para acoplar tu POST de ofertas
    setTimeout(() => {
      this.ngZone.run(() => {
        alert(`Oferta registrada: Bs. ${this.cotizacionForm.precio_estimado} en ${this.cotizacionForm.tiempo_estimado_minutos} mins.`);
        this.cerrarModalCotizacion();
        this.cargarEmergencias();
      });
    }, 1200);
  }

  // --- ACCIÓN 2: INICIAR TRANSITO / TRACKING (ESTADO ACEPTADA -> EN CURSO) ---
  iniciarTracking(emergencia: Emergencia) {
    if (confirm('¿Confirmas que estás iniciando el viaje hacia la ubicación del incidente? El cliente podrá ver tu ruta.')) {
      this.cargando = true;
      
      // Llamada real a tu endpoint PUT /{nro_emergencia}
      this.emergenciasService.actualizarEmergencia(emergencia.nro_emergencia, { estado: 'EN CURSO' }).subscribe({
        next: (res) => {
          this.ngZone.run(() => {
            this.cargarEmergencias();
            // Redirigir al mapa interactivo inmediatamente para iniciar el tracking real
            this.router.navigate(['/emergencias-actuales']);
          });
        },
        error: (err) => {
          this.ngZone.run(() => {
            alert(err.error?.detail || 'No se pudo iniciar el tracking.');
            this.cargando = false;
            this.cdr.detectChanges();
          });
        }
      });
    }
  }

  // --- ACCIÓN 3: ENLAZAR AL MAPA DE MONITOREO (ESTADOS ACEPTADA / EN CURSO) ---
  verTracking() {
    this.router.navigate(['/emergencias-actuales']);
  }
}