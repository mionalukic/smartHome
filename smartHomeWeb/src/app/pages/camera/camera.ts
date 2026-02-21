import { Component } from '@angular/core';
import { NgIf } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-camera',
  standalone: true,
  templateUrl: './camera.html',
  styleUrls: ['./camera.css'],
  imports: [NgIf, MatCardModule, MatButtonModule]
})
export class CameraComponent {
  streamUrl = 'http://IP_PI:8080/?action=stream';
  // streamUrl = 'https://picsum.photos/800/450'; // test

  connected = true;
  isOffline = false;

  frames = 0;
  fps = 0;
  private lastTick = Date.now();

  onLoad() {
    this.isOffline = false;
    this.frames++;

    const now = Date.now();
    const dt = (now - this.lastTick) / 1000;
    if (dt >= 1) {
      this.fps = this.frames;
      this.frames = 0;
      this.lastTick = now;
    }
  }

  onError() {
    this.isOffline = true;
    this.fps = 0;
  }

  reload() {
    this.connected = false;
    setTimeout(() => this.connected = true, 200);
  }
}
