import { Component, OnInit, inject, PLATFORM_ID, HostListener, ChangeDetectorRef, NgZone, DestroyRef } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { Router, RouterOutlet, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth';
import { NotificacionesService } from '../../services/notificaciones'; // <-- Asegúrate de que la ruta sea correcta
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

@Component({
  selector: 'app-admin-layout',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterModule],
  templateUrl: './admin-layout.html'
})
export class AdminLayoutComponent implements OnInit {
  private authService = inject(AuthService);
  private notificacionesService = inject(NotificacionesService);
  private router = inject(Router);
  private platformId = inject(PLATFORM_ID);
  private cdr = inject(ChangeDetectorRef);
  private ngZone = inject(NgZone);
  private destroyRef = inject(DestroyRef);

  usuarioActual: any = null;
  modoOscuro: boolean = false;
  
  sidebarAbierto: boolean = false; 
  sidebarColapsado: boolean = false; 

  // --- VARIABLES DE NOTIFICACIONES ---
  mostrarNotificaciones: boolean = false;
  listaNotificaciones: any[] = [];
  cantidadNoLeidas: number = 0;

  menuNavegacion = [
    {
      titulo: 'Red de Talleres',
      icono: 'M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0zM12 13a3 3 0 100-6 3 3 0 000 6z',
      rolesPermitidos: ['ADMINISTRADOR', 'GERENTE TALLER'],
      expandido: false,
      submenus: [
        { nombre: 'Talleres Asociados', ruta: '/talleres' },
        { nombre: 'Mapa de Talleres', ruta: '/mapa-talleres' }
      ]
    },
    {
      titulo: 'Seguridad y Usuarios',
      icono: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z',
      rolesPermitidos: ['ADMINISTRADOR'],
      expandido: false,
      submenus: [
        { nombre: 'Gestión de Usuarios', ruta: '/usuarios' },
        { nombre: 'Roles y Permisos', ruta: '/roles' },
        { nombre: 'Tenants (Empresas)', ruta: '/empresas' },
        { nombre: 'Bitácora del Sistema', ruta: '/bitacora' },
        { nombre: 'Copias de Respaldo', ruta: '/backup' }
      ]
    },
    {
      titulo: 'Emergencias',
      icono: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
      rolesPermitidos: ['ADMINISTRADOR', 'GERENTE TALLER', 'MECANICO'],
      expandido: false,
      submenus: [
        { nombre: 'Emergencias Actuales', ruta: '/emergencias-actuales' },
        { nombre: 'Historial Atendidas', ruta: '/emergencias-historial' }
      ]
    }    
  ];

  menuFiltrado: any[] = [];

  ngOnInit() {
    if (isPlatformBrowser(this.platformId)) {
      this.usuarioActual = this.authService.obtenerUsuario();
      
      if (!this.usuarioActual) {
        this.cerrarSesion();
        return;
      }

      const rolUsuario = this.usuarioActual.nombre_rol;
      this.menuFiltrado = this.menuNavegacion.filter(m => m.rolesPermitidos.includes(rolUsuario));

      if (localStorage.getItem('tema_sistema') === 'dark') {
        this.modoOscuro = true;
        document.documentElement.classList.add('dark');
      }

      this.verificarResolucion();

      // --- INICIAR CONEXIÓN WEBSOCKET ---
      this.notificacionesService.conectar();

      // Escuchar las notificaciones entrantes en tiempo real
      this.notificacionesService.notificaciones$
        .pipe(takeUntilDestroyed(this.destroyRef))
        .subscribe((notis) => {
          this.ngZone.run(() => {
            this.listaNotificaciones = notis;
            this.cantidadNoLeidas = notis.filter(n => !n.leida).length;
            this.cdr.detectChanges(); // Forzamos el render para que el punto rojo aparezca
          });
        });
    }
  }

  // Detecta si la ventana cambia de tamaño
  @HostListener('window:resize')
  onResize() {
    if (isPlatformBrowser(this.platformId)) {
      this.verificarResolucion();
    }
  }

  verificarResolucion() {
    const isDesktop = window.innerWidth >= 768;
    if (isDesktop && this.sidebarAbierto) {
      this.sidebarAbierto = false; 
    }
  }

  // --- BOTÓN PARA ABRIR/CERRAR NOTIFICACIONES ---
  toggleNotificaciones() {
    this.mostrarNotificaciones = !this.mostrarNotificaciones;
    if (this.mostrarNotificaciones && this.cantidadNoLeidas > 0) {
      this.notificacionesService.marcarComoLeidas();
      this.cantidadNoLeidas = 0;
      this.cdr.detectChanges();
    }
  }

  toggleSidebar() {
    if (isPlatformBrowser(this.platformId)) {
      if (window.innerWidth < 768) {
        this.sidebarAbierto = !this.sidebarAbierto;
      } else {
        this.sidebarColapsado = !this.sidebarColapsado;
        if (this.sidebarColapsado) {
          this.menuFiltrado.forEach(m => m.expandido = false);
        }
      }
    }
  }

  toggleAcordeon(modulo: any) {
    if (this.sidebarColapsado && window.innerWidth >= 768) {
      this.sidebarColapsado = false;
    }
    modulo.expandido = !modulo.expandido;
  }

  cerrarSidebarMobile() {
    this.sidebarAbierto = false;
  }

  alternarModoOscuro() {
    if (isPlatformBrowser(this.platformId)) {
      this.modoOscuro = !this.modoOscuro;
      if (this.modoOscuro) {
        document.documentElement.classList.add('dark');
        localStorage.setItem('tema_sistema', 'dark');
      } else {
        document.documentElement.classList.remove('dark');
        localStorage.setItem('tema_sistema', 'light');
      }
    }
  }

  cerrarSesion() {
    this.notificacionesService.desconectar(); // Importante: cortar WS al salir
    this.authService.cerrarSesion();
    this.router.navigate(['/login']);
  }
}