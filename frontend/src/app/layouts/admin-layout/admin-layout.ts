import { Component, OnInit, inject, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { Router, RouterOutlet, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth';

@Component({
  selector: 'app-admin-layout',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterModule],
  templateUrl: './admin-layout.html'
})
export class AdminLayoutComponent implements OnInit {
  private authService = inject(AuthService);
  private router = inject(Router);
  private platformId = inject(PLATFORM_ID);

  usuarioActual: any = null;
  modoOscuro: boolean = false;
  
  // Variables para controlar la visibilidad del menú
  sidebarAbierto: boolean = false; // Controla el deslizamiento en móviles
  sidebarColapsado: boolean = false; // Controla la reducción a íconos en escritorio

  menuNavegacion = [
    {
      titulo: 'Seguridad y Usuarios',
      icono: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z',
      rolesPermitidos: ['ADMINISTRADOR'],
      expandido: true,
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
    }
  }

  // BOTÓN PRINCIPAL (Controla el Menú en todas las pantallas)
  toggleSidebar() {
    if (isPlatformBrowser(this.platformId)) {
      if (window.innerWidth < 768) {
        // En móviles, se desliza desde la izquierda
        this.sidebarAbierto = !this.sidebarAbierto;
      } else {
        // En escritorio, se encoge dejando solo los íconos
        this.sidebarColapsado = !this.sidebarColapsado;
        // Si lo encogemos, cerramos todos los acordeones para mantener el diseño limpio
        if (this.sidebarColapsado) {
          this.menuFiltrado.forEach(m => m.expandido = false);
        }
      }
    }
  }

  // ACORDEÓN DE MÓDULOS
  toggleAcordeon(modulo: any) {
    // Si el usuario hace clic en un ícono cuando el menú está encogido, lo expandimos automáticamente
    if (this.sidebarColapsado) {
      this.sidebarColapsado = false;
    }
    modulo.expandido = !modulo.expandido;
  }

  // CIERRA EL MENÚ EN MÓVILES AL HACER CLIC AFUERA
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
    this.authService.cerrarSesion();
    this.router.navigate(['/login']);
  }
}