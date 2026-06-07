import { Component, OnInit, OnDestroy, inject, NgZone, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { TalleresService, Taller } from '../../services/talleres';
import type * as LeafletType from 'leaflet';

@Component({
  selector: 'app-mapa-talleres',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './mapa-talleres.html'
})
export class MapaTalleresComponent implements OnInit, OnDestroy {
  private talleresService = inject(TalleresService);
  private ngZone = inject(NgZone);
  private platformId = inject(PLATFORM_ID);

  private L!: typeof LeafletType;
  private mapa: LeafletType.Map | null = null;
  private talleres: Taller[] = [];

  async ngOnInit() {
    if (!isPlatformBrowser(this.platformId)) return;

    this.L = await import('leaflet') as any;

    // Fix íconos Leaflet + Angular/Webpack
    const iconDefault = this.L.icon({
      iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
      iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
      shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
      shadowSize: [41, 41]
    });
    this.L.Marker.prototype.options.icon = iconDefault;

    this.ngZone.runOutsideAngular(() => {
      this.mapa = this.L.map('mapa-completo', {
        center: [-17.7833, -63.1821],
        zoom: 13,
        zoomControl: true
      });

      this.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        maxZoom: 19
      }).addTo(this.mapa!);
    });

    this.cargarTalleres();
  }

  ngOnDestroy() {
    if (this.mapa) {
      this.mapa.remove();
      this.mapa = null;
    }
  }

  cargarTalleres() {
    this.talleresService.obtenerTalleres().subscribe({
      next: (res) => {
        this.talleres = res.data;
        this.pintarPines();
      },
      error: (err) => console.error('Error al cargar talleres:', err)
    });
  }

  pintarPines() {
    if (!this.mapa) return;

    const bounds: LeafletType.LatLngTuple[] = [];

    this.talleres.forEach(taller => {
      if (taller.latitud == null || taller.longitud == null) return;

      const iconColor = taller.disponibilidad ? '#1e3a8a' : '#dc2626';
      const iconSvg = `
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 42" width="32" height="42">
          <path d="M16 0C7.163 0 0 7.163 0 16c0 10 16 26 16 26S32 26 32 16C32 7.163 24.837 0 16 0z"
                fill="${iconColor}" stroke="white" stroke-width="1.5"/>
          <circle cx="16" cy="16" r="7" fill="white"/>
        </svg>
      `;

      const customIcon = this.L.divIcon({
        html: iconSvg,
        className: '',
        iconSize: [32, 42],
        iconAnchor: [16, 42],
        popupAnchor: [0, -44]
      });

      this.ngZone.runOutsideAngular(() => {
        const marker = this.L.marker(
          [taller.latitud!, taller.longitud!],
          { icon: customIcon }
        ).addTo(this.mapa!);

        const estadoColor = taller.disponibilidad ? '#16a34a' : '#dc2626';
        const estadoTexto = taller.disponibilidad ? 'OPERATIVO' : 'CERRADO';
        const tooltipHtml = `
          <div style="min-width:180px; font-family: sans-serif;">
            <div style="background:#1e3a8a; color:white; padding:8px 10px; border-radius:6px 6px 0 0; font-weight:700; font-size:12px; line-height:1.3;">
              ${taller.nombre_taller}
            </div>
            <div style="padding:8px 10px; background:white; border-radius:0 0 6px 6px; display:flex; flex-direction:column; gap:4px;">
              <div style="font-size:11px; color:#6b7280;">
                📍 ${taller.direccion_escrita}
              </div>
              <div style="margin-top:2px;">
                <span style="background:${estadoColor}20; color:${estadoColor}; border:1px solid ${estadoColor}50;
                             font-size:10px; font-weight:700; padding:2px 8px; border-radius:99px;">
                  ● ${estadoTexto}
                </span>
              </div>
            </div>
          </div>
        `;

        marker.bindTooltip(tooltipHtml, {
          direction: 'top',
          offset: [0, -44],
          opacity: 1,
          className: 'leaflet-tooltip-taller'
        });
      });

      bounds.push([taller.latitud, taller.longitud]);
    });

    if (bounds.length > 1 && this.mapa) {
      this.mapa.fitBounds(bounds, { padding: [50, 50] });
    }
  }
}