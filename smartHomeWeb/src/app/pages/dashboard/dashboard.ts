import { Component, OnInit } from '@angular/core';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import {SecurityService} from '../../services/security';
import {MatCard, MatCardContent, MatCardTitle} from '@angular/material/card';
import {MatButton} from '@angular/material/button';
import {NgIf} from '@angular/common';
import { interval } from 'rxjs';


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
  styleUrls: ['dashboard.css']
})
export class DashboardComponent implements OnInit {
  mode: 'DISARMED' | 'ARMED' | 'ALARM' | string = '';
  lastMessage = '';
  grafanaUrlSafe: SafeResourceUrl;

  constructor(
    private security: SecurityService,
    sanitizer: DomSanitizer
  ) {
    const grafanaUrl = 'http://localhost:3000/public-dashboards/e555e5477ebe431d87334a69ed8a2652?orgId=1&kiosk';
    this.grafanaUrlSafe = sanitizer.bypassSecurityTrustResourceUrl(grafanaUrl);
  }

  ngOnInit() {
    interval(1500).subscribe(() => this.refresh());
  }


  refresh() {
    this.security.getStatus().subscribe({
      next: (m) => this.mode = m.mode,
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
