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

  // Control de Modal: Cotización
  mostrarModalCotizacion: boolean = false;
  procesandoAccion: boolean = false;
  
  // Control de Modal: Detalles y Evidencias
  mostrarModalDetalles: boolean = false;
  cargandoEvidencias: boolean = false;
  evidenciasDetalle: any[] = [];
  
  emergenciaSeleccionada: Emergencia | null = null;
  
  cotizacionForm = {
    precio_estimado: null,
    tiempo_estimado_minutos: null
  };

  ngOnInit() {
    if (isPlatformBrowser(this.platformId)) {
      this.usuarioActual = this.authService.obtenerUsuario();
      if (this.usuarioActual) {
        this.cargarEmergencias();
      }
    }
  }

  cargarEmergencias() {
    this.cargando = true;
    const rol = this.usuarioActual.nombre_rol.toUpperCase();

    let peticion$;
    if (rol === 'ADMINISTRADOR' || rol === 'GERENTE TALLER') {
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

  // --- MODAL DETALLES Y EVIDENCIAS ---
  abrirModalDetalles(emergencia: Emergencia) {
    this.emergenciaSeleccionada = emergencia;
    this.mostrarModalDetalles = true;
    this.cargandoEvidencias = true;
    this.evidenciasDetalle = [];

    this.emergenciasService.obtenerEvidenciasEmergencia(emergencia.nro_emergencia).subscribe({
      next: (res) => {
        this.ngZone.run(() => {
          if (res.success) this.evidenciasDetalle = res.data;
          this.cargandoEvidencias = false;
          this.cdr.detectChanges();
        });
      },
      error: () => {
        this.ngZone.run(() => {
          this.cargandoEvidencias = false;
          this.cdr.detectChanges();
        });
      }
    });
  }

  cerrarModalDetalles() {
    this.mostrarModalDetalles = false;
    // Si no vamos a cotizar, limpiamos la selección
    if (!this.mostrarModalCotizacion) {
      this.emergenciaSeleccionada = null;
    }
  }

  pasarACotizacionDesdeDetalles() {
    this.mostrarModalDetalles = false; // Cerramos detalles
    this.cotizacionForm = { precio_estimado: null, tiempo_estimado_minutos: null };
    this.mostrarModalCotizacion = true; // Abrimos cotización
  }

  // --- MODAL COTIZACIÓN ---
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

  // --- REEMPLAZA ESTE MÉTODO EN TU COMPONENTE ---
  
  enviarCotizacion() {
    // 1. Validación de seguridad en Frontend
    if (!this.cotizacionForm.precio_estimado || !this.cotizacionForm.tiempo_estimado_minutos) {
      alert('Ingrese todos los datos de la oferta comercial.');
      return;
    }
    
    if (!this.emergenciaSeleccionada) {
      alert('No hay una emergencia seleccionada.');
      return;
    }

    this.procesandoAccion = true;
    
    // 2. Armar el JSON exacto que espera FastAPI
    const payloadOferta = {
      nro_emergencia: this.emergenciaSeleccionada.nro_emergencia,
      precio_estimado: this.cotizacionForm.precio_estimado,
      tiempo_estimado_minutos: this.cotizacionForm.tiempo_estimado_minutos
    };

    // 3. Petición HTTP Real
    this.emergenciasService.emitirOferta(payloadOferta).subscribe({
      next: (res) => {
        this.ngZone.run(() => {
          if (res.success) {
            alert('¡Oferta enviada exitosamente al cliente! El cliente recibirá una notificación.');
            this.cerrarModalCotizacion();
            this.cargarEmergencias(); // Refrescamos el tablero
          }
        });
      },
      error: (err) => {
        this.ngZone.run(() => {
          alert(err.error?.detail || 'Ocurrió un error al intentar enviar la cotización.');
          this.procesandoAccion = false;
          this.cdr.detectChanges();
        });
      }
    });
  }

  // --- TRACKING ---
  iniciarTracking(emergencia: Emergencia) {
    if (confirm('¿Confirmas que estás iniciando el viaje hacia la ubicación del incidente? El cliente podrá ver tu ruta.')) {
      this.cargando = true;
      this.emergenciasService.actualizarEmergencia(emergencia.nro_emergencia, { estado: 'EN CURSO' }).subscribe({
        next: () => {
          this.ngZone.run(() => {
            this.cargarEmergencias();
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

  verTracking() {
    this.router.navigate(['/emergencias-actuales']);
  }
}