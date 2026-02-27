import { Component, ViewChild, ElementRef, OnDestroy, NgZone, ChangeDetectorRef } from '@angular/core';
import { NgIf, NgSwitch, NgSwitchCase } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';

type SourceType = 'laptop' | 'rpi';

@Component({
  selector: 'app-camera',
  standalone: true,
  templateUrl: './camera.html',
  styleUrls: ['./camera.css'],
  imports: [NgIf, NgSwitch, NgSwitchCase, MatCardModule, MatButtonModule, MatSelectModule, MatFormFieldModule]
})
export class CameraComponent implements OnDestroy {
  // --- RPi stream (replace IP_PI) ---
  baseStreamUrl = 'http://192.168.107.147:8080/?action=stream';
  streamUrl = this.baseStreamUrl;

  // --- UI state ---
  source: SourceType = 'laptop';
  isOffline = false;
  connected = true;

  // --- FPS state ---
  frames = 0;
  fps = 0;
  private fpsTimerId: any = null;

  // --- Laptop webcam refs/state ---
  @ViewChild('videoEl', { static: false }) videoEl?: ElementRef<HTMLVideoElement>;
  private mediaStream?: MediaStream;

  // requestVideoFrameCallback handle
  private cancelVideoRvf?: number;
  private rafId?: number;

  constructor(private zone: NgZone, private cdr: ChangeDetectorRef) {}

  ngOnDestroy(): void {
    this.stopAll();
  }

  // ======== Source switching ========
  async onSourceChange(src: SourceType) {
    if (src === this.source) return;

    this.stopAll();
    this.source = src;
    this.isOffline = false;

    if (src === 'laptop') {
      await this.startLaptopCamera();
    } else {
      this.reloadRpi(); // will reconnect <img> and start counting on (load)
    }
    this.startFpsTicker();
  }

  // ======== Laptop camera ========
  async startLaptopCamera() {
    try {
      this.mediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
      if (!this.videoEl) return;
      const video = this.videoEl.nativeElement;
      video.srcObject = this.mediaStream;
      this.isOffline = false;

      // Prefer accurate per-decoded-frame counting
      this.startVideoFrameCounting();
      this.startFpsTicker();
    } catch (err) {
      console.error('Camera error:', err);
      this.isOffline = true;
      this.stopFpsTicker();
    }
  }

  private startVideoFrameCounting() {
    const video = this.videoEl?.nativeElement;
    if (!video) return;

    // Use requestVideoFrameCallback if available
    const anyVideo = video as any;
    if (typeof anyVideo.requestVideoFrameCallback === 'function') {
      const onFrame = (_now: number, _metadata: any) => {
        // Count decoded frames
        this.zone.run(() => {
          this.frames++;
        });
        this.cancelVideoRvf = anyVideo.requestVideoFrameCallback(onFrame);
      };
      this.cancelVideoRvf = anyVideo.requestVideoFrameCallback(onFrame);
    } else {
      // Fallback: RAF-based counting (less precise but works)
      const tick = () => {
        this.zone.run(() => {
          this.frames++;
        });
        this.rafId = requestAnimationFrame(tick);
      };
      this.rafId = requestAnimationFrame(tick);
    }
  }

  private stopLaptopCamera() {
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(t => t.stop());
      this.mediaStream = undefined;
    }
    if (this.videoEl?.nativeElement) {
      this.videoEl.nativeElement.srcObject = null;
    }
    // Stop frame callbacks
    if (this.cancelVideoRvf) {
      // There is no standard cancel for rVFC; we just don't schedule another
      this.cancelVideoRvf = undefined;
    }
    if (this.rafId != null) {
      cancelAnimationFrame(this.rafId);
      this.rafId = undefined;
    }
  }

  onVideoLoadedData() {
    // Called once when the video metadata/first frame is available
    this.isOffline = false;
  }

  // ======== RPi (MJPEG) ========
  onImageLoad() {
    // Each <img> load is one MJPEG frame
    this.zone.run(() => {
      this.isOffline = false;
      this.frames++;
    });
  }

  onImageError() {
    this.zone.run(() => {
      this.isOffline = true;
    });
  }

  reloadRpi() {
    // Force re-render and cache-bust to avoid stale connections
    this.connected = false;
    this.isOffline = false;
    this.resetFpsCounters();
    const cacheBust = `&t=${Date.now()}`;
    this.streamUrl = this.baseStreamUrl + cacheBust;

    setTimeout(() => {
      this.connected = true;
    }, 50);
  }

  // ======== FPS ticker (shared) ========
  private startFpsTicker() {
    if (this.fpsTimerId) return;
    this.resetFpsCounters();

    // Compute FPS once per second
    this.fpsTimerId = setInterval(() => {
      // Pull and reset the counter
      const current = this.frames;
      this.frames = 0;

      this.zone.run(() => {
        this.fps = current;
        // If using OnPush CD strategy, ensure UI updates:
        this.cdr.markForCheck();
      });
    }, 1000);
  }

  private stopFpsTicker() {
    if (this.fpsTimerId) {
      clearInterval(this.fpsTimerId);
      this.fpsTimerId = null;
    }
  }

  private resetFpsCounters() {
    this.frames = 0;
    this.fps = 0;
  }

  private stopAll() {
    this.stopLaptopCamera();
    this.stopFpsTicker();
  }
}