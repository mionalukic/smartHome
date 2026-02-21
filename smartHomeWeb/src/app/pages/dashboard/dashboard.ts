import { Component, OnInit } from '@angular/core';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import {SecurityService} from '../../services/security';
import {MatCard, MatCardContent, MatCardTitle} from '@angular/material/card';
import {MatButton} from '@angular/material/button';
import {NgIf} from '@angular/common';


@Component({
  selector: 'app-dashboard',
  templateUrl: 'dashboard.html',
  standalone: true,
  imports: [
    MatCardTitle,
    MatCardContent,
    MatCard,
    MatButton,
    NgIf
  ],
  styleUrl: 'dashboard.css'
})
export class DashboardComponent implements OnInit {
  mode: 'DISARMED' | 'ARMED' | 'ALARM' | string = '';
  lastMessage = '';
  grafanaUrlSafe: SafeResourceUrl;

  constructor(
    private security: SecurityService,
    sanitizer: DomSanitizer
  ) {
    // ubaci ovde tvoj grafana link (kasnije)
    const grafanaUrl = 'http://localhost:3000/d/XXXX/dashboard?orgId=1&kiosk';
    this.grafanaUrlSafe = sanitizer.bypassSecurityTrustResourceUrl(grafanaUrl);
  }

  ngOnInit() {
    this.refresh();
    setInterval(() => this.refresh(), 1500); // kasnije SSE/WebSocket, za sada polling
  }

  refresh() {
    this.security.getStatus().subscribe({
      next: (m) => this.mode = m,
      error: () => this.mode = 'UNKNOWN'
    });
  }

  arm() {
    this.security.arm().subscribe(() => this.lastMessage = 'ARM command sent');
  }
  disarm() {
    this.security.disarm().subscribe(() => this.lastMessage = 'DISARM command sent');
  }
  alarmOff() {
    this.security.alarmOff().subscribe(() => this.lastMessage = 'ALARM OFF command sent');
  }
}
