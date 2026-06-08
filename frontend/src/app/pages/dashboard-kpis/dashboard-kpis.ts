import { Component, OnInit, inject, ChangeDetectorRef, NgZone, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { Router } from '@angular/router';
import { KpisService, DashboardMetricas } from '../../services/kpis';
import { AuthService } from '../../services/auth';

@Component({
  selector: 'app-dashboard-kpis',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard-kpis.html'
})
export class DashboardKpisComponent implements OnInit {

  private kpisService = inject(KpisService);
  private authService = inject(AuthService);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);
  private ngZone = inject(NgZone);
  private platformId = inject(PLATFORM_ID);

  usuarioActual: any = null;
  modoOscuro: boolean = false;

  metricas: DashboardMetricas | null = null;

  cargando: boolean = false;
  mensajeError: string = '';

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.usuarioActual = this.authService.obtenerUsuario();

      if (!this.usuarioActual || this.authService.tokenExpirado()) {
        this.cerrarSesion();
        return;
      }

      if (localStorage.getItem('tema_sistema') === 'dark') {
        this.modoOscuro = true;
        document.documentElement.classList.add('dark');
      }

      this.cargarMetricas();
    }
  }

  cargarMetricas(): void {
    this.cargando = true;
    this.mensajeError = '';
    this.metricas = null;

    this.kpisService.obtenerMetricasDashboard().subscribe({
      next: (res) => {
        this.ngZone.run(() => {
          if (res.success) {
            this.metricas = res.data;
          } else {
            this.mensajeError = res.message || 'No se pudieron cargar los KPIs.';
          }

          this.cargando = false;
          this.cdr.detectChanges();
        });
      },
      error: (err) => {
        this.ngZone.run(() => {
          this.mensajeError =
            err.error?.detail ||
            'Error al conectar con el módulo de analítica y KPIs.';

          this.cargando = false;
          this.cdr.detectChanges();
        });
      }
    });
  }

  refrescarDashboard(): void {
    this.cargarMetricas();
  }

  alternarModoOscuro(): void {
    this.modoOscuro = !this.modoOscuro;

    if (this.modoOscuro) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('tema_sistema', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('tema_sistema', 'light');
    }
  }

  navegarA(ruta: string): void {
    this.router.navigate([ruta]);
  }

  cerrarSesion(): void {
    this.authService.cerrarSesion();
    this.router.navigate(['/login']);
  }

  getPorcentajeCancelados(): number {
    if (!this.metricas || this.metricas.total_casos_historicos === 0) {
      return 0;
    }

    return Number(
      ((this.metricas.casos_cancelados / this.metricas.total_casos_historicos) * 100).toFixed(2)
    );
  }

  getTotalIncidentesPorTipo(): number {
    if (!this.metricas || !this.metricas.incidentes_por_tipo.length) {
      return 0;
    }

    return this.metricas.incidentes_por_tipo.reduce(
      (total, item) => total + item.cantidad,
      0
    );
  }

  getMaxIncidentes(): number {
    if (!this.metricas || !this.metricas.incidentes_por_tipo.length) {
      return 1;
    }

    return Math.max(...this.metricas.incidentes_por_tipo.map(item => item.cantidad));
  }

  getAnchoBarraIncidente(cantidad: number): number {
    const maximo = this.getMaxIncidentes();

    if (maximo === 0) {
      return 0;
    }

    return Number(((cantidad / maximo) * 100).toFixed(2));
  }

  getMaxTiempoTaller(): number {
    if (!this.metricas || !this.metricas.talleres_eficientes.length) {
      return 1;
    }

    return Math.max(...this.metricas.talleres_eficientes.map(item => item.tiempo_promedio_min));
  }

  getAnchoBarraTaller(tiempo: number): number {
    const maximo = this.getMaxTiempoTaller();

    if (maximo === 0) {
      return 0;
    }

    return Number(((tiempo / maximo) * 100).toFixed(2));
  }

  getSlaComoNumero(): number {
    if (!this.metricas || !this.metricas.nivel_cumplimiento_sla) {
      return 0;
    }

    const valor = this.metricas.nivel_cumplimiento_sla.replace('%', '');
    const numero = Number(valor);

    return isNaN(numero) ? 0 : numero;
  }

  getTextoTiempo(minutos: number): string {
    if (!minutos || minutos <= 0) {
      return '0 min';
    }

    if (minutos < 60) {
      return `${minutos} min`;
    }

    const horas = Math.floor(minutos / 60);
    const minutosRestantes = Math.round(minutos % 60);

    return `${horas} h ${minutosRestantes} min`;
  }

  trackByTipo(index: number, item: any): string {
    return item.tipo;
  }

  trackByTaller(index: number, item: any): string {
    return item.taller;
  }

  trackByPunto(index: number): number {
    return index;
  }
}