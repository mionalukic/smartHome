import { Component, OnInit } from '@angular/core';
import { SecurityService } from '../services/security';
import {FormsModule} from '@angular/forms';
import {NgIf} from '@angular/common';

@Component({
  selector: 'app-security',
  templateUrl: './security.html',
  styleUrl: './security.css',
  imports: [
    FormsModule,
    NgIf
  ],
  standalone: true
})
export class SecurityComponent implements OnInit {

  mode = '';
  reason: string | null = null;
  source: string | null = null;

  pin = '';
  pinResult = '';

  constructor(private security: SecurityService) {}

  ngOnInit() {
    this.refresh();
    setInterval(() => this.refresh(), 1500);
  }

  refresh() {
    this.security.getStatus().subscribe((data: any) => {
      this.mode = data.mode;
      this.reason = data.reason;
      this.source = data.source;
    });
  }

  submitPin() {
    if (!this.pin) return;

    this.security.enterPin(this.pin).subscribe((res: any) => {
      this.pinResult = res.result;
      this.mode = res.mode;
      this.reason = res.reason;
      this.source = res.source;
      this.pin = '';
    });
  }
}
